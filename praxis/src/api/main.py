"""
Praxis v0.3 - Main API Application

FastAPI application implementing the REST API for Praxis MVP.
Implements Phase 2 decisions from §16:
- Default autonomy level: 1 (supervised execution)
- KnowledgeBase: empty at start
- Traceability: present but non-blocking
- Job queue: synchronous processing
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from src.models import (
    Task, TaskStatus, TaskType, Project, ProjectStatus,
    Artifact, ArtifactKind, Deliverable, AutonomyLevel, LearningLog
)
from src.services.database import get_session, init_db, get_engine
from src.services.task_service import TaskService
from src.services.project_service import ProjectService
from src.services.artifact_service import ArtifactService
from src.services.learning_service import LearningService
from src.services.error_recovery import ErrorRecoveryService
from src.services.validation_service import ValidationService
from src.config import settings


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class TaskCreate(BaseModel):
    title: str
    raw_request: str
    task_type: TaskType = TaskType.AUTRE
    domain: Optional[str] = None
    objective: Optional[str] = None
    project_id: Optional[str] = None
    deadline: Optional[datetime] = None
    estimated_duration: Optional[int] = None
    priority: int = 5


class TaskResponse(BaseModel):
    id: str
    title: str
    raw_request: str
    type: TaskType
    status: TaskStatus
    readiness_score: Optional[float]
    autonomy_level: AutonomyLevel
    project_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: ProjectStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReadinessUpdate(BaseModel):
    dimension_scores: Dict[str, float]


class PlanValidation(BaseModel):
    approved: bool


class ClarificationAnswers(BaseModel):
    answers: Dict[str, str]


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Praxis v0.3 - Personal Intelligent Work System (MVP)"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# LIFECYCLE EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    engine = get_engine()
    init_db(engine)


# ============================================================================
# TASK ENDPOINTS
# ============================================================================

@app.post("/tasks", response_model=TaskResponse, tags=["Tasks"])
def create_task(task_data: TaskCreate, db: Session = Depends(get_session)):
    """Create a new task"""
    service = TaskService(db)
    
    task = service.create_task(
        title=task_data.title,
        raw_request=task_data.raw_request,
        task_type=task_data.task_type,
        domain=task_data.domain,
        project_id=task_data.project_id,
        objective=task_data.objective,
        deadline=task_data.deadline,
        estimated_duration=task_data.estimated_duration,
        priority=task_data.priority
    )
    
    return task


@app.get("/tasks", response_model=List[TaskResponse], tags=["Tasks"])
def list_tasks(
    project_id: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    limit: int = 50,
    db: Session = Depends(get_session)
):
    """List tasks with optional filters"""
    service = TaskService(db)
    return service.list_tasks(project_id=project_id, status=status, limit=limit)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
def get_task(task_id: str, db: Session = Depends(get_session)):
    """Get a task by ID"""
    service = TaskService(db)
    task = service.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@app.post("/tasks/{task_id}/readiness", tags=["Tasks"])
def update_readiness(
    task_id: str,
    readiness_data: ReadinessUpdate,
    db: Session = Depends(get_session)
):
    """Update task readiness and get clarification questions if needed"""
    service = TaskService(db)
    
    try:
        result = service.update_task_readiness(
            task_id=task_id,
            dimension_scores=readiness_data.dimension_scores
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/tasks/{task_id}/clarification", response_model=TaskResponse, tags=["Tasks"])
def answer_clarification(
    task_id: str,
    answers: ClarificationAnswers,
    db: Session = Depends(get_session)
):
    """Submit answers to clarification questions"""
    service = TaskService(db)
    
    try:
        task = service.answer_clarification(task_id, answers.answers)
        return task
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/tasks/{task_id}/plan", tags=["Tasks"])
def propose_plan(task_id: str, db: Session = Depends(get_session)):
    """Generate a plan proposal for a task"""
    service = TaskService(db)
    
    try:
        result = service.propose_plan(task_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/plans/{plan_id}/validate", tags=["Plans"])
def validate_plan(
    plan_id: str,
    validation: PlanValidation,
    db: Session = Depends(get_session)
):
    """Validate or reject a plan"""
    service = TaskService(db)
    
    try:
        plan = service.validate_plan(plan_id, validation.approved)
        return {"plan": plan, "status": plan.status}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/tasks/{task_id}", tags=["Tasks"])
def delete_task(task_id: str, db: Session = Depends(get_session)):
    """Delete a task"""
    service = TaskService(db)
    
    if not service.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"message": "Task deleted successfully"}


# ============================================================================
# PROJECT ENDPOINTS
# ============================================================================

@app.post("/projects", response_model=ProjectResponse, tags=["Projects"])
def create_project(project_data: ProjectCreate, db: Session = Depends(get_session)):
    """Create a new project"""
    service = ProjectService(db)
    
    project = service.create_project(
        name=project_data.name,
        description=project_data.description,
        deadline=project_data.deadline
    )
    
    return project


@app.get("/projects", response_model=List[ProjectResponse], tags=["Projects"])
def list_projects(
    status: Optional[ProjectStatus] = None,
    limit: int = 50,
    db: Session = Depends(get_session)
):
    """List projects"""
    service = ProjectService(db)
    return service.list_projects(status=status, limit=limit)


@app.get("/projects/{project_id}", response_model=ProjectResponse, tags=["Projects"])
def get_project(project_id: str, db: Session = Depends(get_session)):
    """Get a project by ID"""
    service = ProjectService(db)
    project = service.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project


@app.post("/projects/{project_id}/tasks/{task_id}", tags=["Projects"])
def add_task_to_project(
    project_id: str,
    task_id: str,
    db: Session = Depends(get_session)
):
    """Add a task to a project"""
    service = ProjectService(db)
    
    if not service.add_task_to_project(project_id, task_id):
        raise HTTPException(status_code=404, detail="Project or task not found")
    
    return {"message": "Task added to project successfully"}


@app.get("/projects/{project_id}/task-order", tags=["Projects"])
def get_task_order(project_id: str, db: Session = Depends(get_session)):
    """Get tasks in execution order based on dependencies"""
    service = ProjectService(db)
    
    tasks = service.get_task_order(project_id)
    
    return {
        "project_id": project_id,
        "ordered_tasks": [
            {"id": t.id, "title": t.title, "status": t.status.value}
            for t in tasks
        ]
    }


# ============================================================================
# ARTIFACT ENDPOINTS
# ============================================================================

@app.get("/artifacts", tags=["Artifacts"])
def list_artifacts(
    task_id: Optional[str] = None,
    kind: Optional[ArtifactKind] = None,
    limit: int = 100,
    db: Session = Depends(get_session)
):
    """List artifacts with filters"""
    service = ArtifactService(db)
    return service.list_artifacts(task_id=task_id, kind=kind, limit=limit)


@app.get("/artifacts/{artifact_id}/provenance", tags=["Artifacts"])
def get_artifact_provenance(artifact_id: str, db: Session = Depends(get_session)):
    """Get full provenance chain for an artifact"""
    service = ArtifactService(db)
    return service.get_artifact_provenance(artifact_id)


@app.get("/deliverables", tags=["Deliverables"])
def list_deliverables(
    task_id: Optional[str] = None,
    project_id: Optional[str] = None,
    db: Session = Depends(get_session)
):
    """List deliverables"""
    service = ArtifactService(db)
    return service.get_deliverables(task_id=task_id, project_id=project_id)


@app.post("/deliverables/{deliverable_id}/validate", tags=["Deliverables"])
def validate_deliverable(deliverable_id: str, db: Session = Depends(get_session)):
    """Mark a deliverable as validated"""
    service = ArtifactService(db)
    
    result = service.validate_deliverable(deliverable_id)
    if not result:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    
    return {"message": "Deliverable validated", "deliverable": result}


# ============================================================================
# LEARNING ENDPOINTS
# ============================================================================

@app.get("/learning/candidates", tags=["Learning"])
def get_learning_candidates(db: Session = Depends(get_session)):
    """Get learning candidates awaiting validation"""
    service = LearningService(db)
    candidates = service.get_candidates_for_validation()
    
    return {
        "count": len(candidates),
        "candidates": [
            {
                "id": c.id,
                "task_id": c.task_id,
                "hypothesis": c.hypothesis,
                "confidence": c.confidence,
                "created_at": c.created_at
            }
            for c in candidates
        ]
    }


@app.post("/learning/{log_id}/validate", tags=["Learning"])
def validate_learning_candidate(
    log_id: str,
    preference: Dict[str, Any],
    db: Session = Depends(get_session)
):
    """Validate a learning candidate"""
    service = LearningService(db)
    
    result = service.validate_candidate(log_id, preference)
    if not result:
        raise HTTPException(status_code=404, detail="Learning log not found")
    
    return {"message": "Learning candidate validated", "log": result}


@app.post("/learning/{log_id}/reject", tags=["Learning"])
def reject_learning_candidate(log_id: str, db: Session = Depends(get_session)):
    """Reject a learning candidate"""
    service = LearningService(db)
    
    result = service.reject_candidate(log_id)
    if not result:
        raise HTTPException(status_code=404, detail="Learning log not found")
    
    return {"message": "Learning candidate rejected"}


# ============================================================================
# METRICS ENDPOINTS (§14)
# ============================================================================

@app.get("/metrics/errors", tags=["Metrics"])
def get_error_metrics(db: Session = Depends(get_session)):
    """Get error statistics for system metrics"""
    service = ErrorRecoveryService(db)
    return service.get_error_statistics()


@app.get("/metrics/learning", tags=["Metrics"])
def get_learning_metrics(db: Session = Depends(get_session)):
    """Get learning statistics"""
    service = LearningService(db)
    
    return {
        "validated_preferences": service.count_validated_preferences(),
        "total_observations": db.query(LearningLog).count()
    }


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "database": settings.DATABASE_URL.split(":")[0]
    }


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
