"""
Artifact Service - Manage artifacts and deliverables with provenance
"""

from typing import Dict, List, Optional
from datetime import datetime
import os
import shutil
from sqlalchemy.orm import Session

from ..models import Artifact, ArtifactKind, Deliverable, Task, Project
from ..config import settings


class ArtifactService:
    """Service for managing artifacts and deliverables"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_artifact(
        self,
        task_id: str,
        kind: ArtifactKind,
        format: str,
        file_path: str,
        project_id: Optional[str] = None,
        produced_by_agent: Optional[str] = None,
        execution_id: Optional[str] = None,
        derived_from: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
        version: int = 1
    ) -> Artifact:
        """Create a new artifact"""
        
        # Store file in designated storage
        stored_path = self._store_file(file_path, task_id)
        
        # Get file size
        file_size = os.path.getsize(stored_path) if os.path.exists(stored_path) else 0
        
        artifact = Artifact(
            task_id=task_id,
            project_id=project_id,
            kind=kind,
            format=format,
            file_ref=stored_path,
            file_size=file_size,
            version=version,
            produced_by_agent=produced_by_agent,
            produced_by_execution=execution_id,
            derived_from=derived_from or [],
            metadata=metadata or {}
        )
        
        self.db.add(artifact)
        self.db.commit()
        self.db.refresh(artifact)
        
        return artifact
    
    def _store_file(self, source_path: str, task_id: str) -> str:
        """Store file in artifact storage with proper path structure"""
        dest_dir = os.path.join(settings.STORAGE_PATH, task_id)
        os.makedirs(dest_dir, exist_ok=True)
        
        filename = os.path.basename(source_path)
        dest_path = os.path.join(dest_dir, filename)
        
        shutil.copy2(source_path, dest_path)
        return dest_path
    
    def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        """Get an artifact by ID"""
        return self.db.query(Artifact).filter(Artifact.id == artifact_id).first()
    
    def list_artifacts(
        self,
        task_id: Optional[str] = None,
        project_id: Optional[str] = None,
        kind: Optional[ArtifactKind] = None,
        limit: int = 100
    ) -> List[Artifact]:
        """List artifacts with filters"""
        query = self.db.query(Artifact)
        
        if task_id:
            query = query.filter(Artifact.task_id == task_id)
        if project_id:
            query = query.filter(Artifact.project_id == project_id)
        if kind:
            query = query.filter(Artifact.kind == kind)
        
        return query.order_by(Artifact.created_at.desc()).limit(limit).all()
    
    def create_deliverable_from_artifact(
        self,
        artifact_id: str,
        task_id: str,
        project_id: Optional[str] = None
    ) -> Deliverable:
        """
        Mark an artifact as a deliverable.
        
        Rule from §3.12: A Deliverable is an Artifact with kind=deliverable,
        produced in exact correspondence with Task.deliverables[]
        """
        artifact = self.get_artifact(artifact_id)
        if not artifact:
            raise ValueError(f"Artifact {artifact_id} not found")
        
        # Update artifact kind to deliverable
        artifact.kind = ArtifactKind.DELIVERABLE
        self.db.commit()
        
        # Create deliverable record
        deliverable = Deliverable(
            artifact_id=artifact_id,
            task_id=task_id,
            project_id=project_id,
            validated=False
        )
        
        self.db.add(deliverable)
        self.db.commit()
        self.db.refresh(deliverable)
        
        return deliverable
    
    def get_deliverables(
        self,
        task_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> List[Deliverable]:
        """Get deliverables with optional filters"""
        query = self.db.query(Deliverable)
        
        if task_id:
            query = query.filter(Deliverable.task_id == task_id)
        if project_id:
            query = query.filter(Deliverable.project_id == project_id)
        
        return query.all()
    
    def validate_deliverable(self, deliverable_id: str) -> Optional[Deliverable]:
        """Mark a deliverable as validated"""
        deliverable = self.db.query(Deliverable).filter(
            Deliverable.id == deliverable_id
        ).first()
        
        if not deliverable:
            return None
        
        deliverable.validated = True
        deliverable.delivered_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(deliverable)
        
        return deliverable
    
    def get_artifact_provenance(self, artifact_id: str) -> Dict:
        """Get full provenance chain for an artifact"""
        artifact = self.get_artifact(artifact_id)
        if not artifact:
            return {}
        
        provenance = {
            "artifact": {
                "id": artifact.id,
                "kind": artifact.kind.value,
                "format": artifact.format,
                "version": artifact.version,
                "produced_by_agent": artifact.produced_by_agent,
                "created_at": artifact.created_at.isoformat() if artifact.created_at else None
            },
            "derived_from": [],
            "task": None,
            "execution": None
        }
        
        # Get parent artifacts
        if artifact.derived_from:
            parents = self.db.query(Artifact).filter(
                Artifact.id.in_(artifact.derived_from)
            ).all()
            provenance["derived_from"] = [
                {"id": p.id, "kind": p.kind.value, "version": p.version}
                for p in parents
            ]
        
        # Get task info
        if artifact.task:
            provenance["task"] = {
                "id": artifact.task.id,
                "title": artifact.task.title,
                "type": artifact.task.type.value if artifact.task.type else None
            }
        
        return provenance
    
    def create_new_version(
        self,
        artifact_id: str,
        new_file_path: str
    ) -> Artifact:
        """Create a new version of an artifact (§3.19)"""
        original = self.get_artifact(artifact_id)
        if not original:
            raise ValueError(f"Artifact {artifact_id} not found")
        
        # Create new version
        new_artifact = self.create_artifact(
            task_id=original.task_id,
            kind=original.kind,
            format=original.format,
            file_path=new_file_path,
            project_id=original.project_id,
            produced_by_agent=original.produced_by_agent,
            derived_from=[artifact_id],
            version=original.version + 1
        )
        
        # Link to previous version
        new_artifact.previous_version_id = artifact_id
        self.db.commit()
        self.db.refresh(new_artifact)
        
        return new_artifact
    
    def delete_artifact(self, artifact_id: str) -> bool:
        """Delete an artifact and its file"""
        artifact = self.get_artifact(artifact_id)
        if not artifact:
            return False
        
        # Delete file
        if os.path.exists(artifact.file_ref):
            os.remove(artifact.file_ref)
        
        self.db.delete(artifact)
        self.db.commit()
        
        return True
