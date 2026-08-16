"""
Task Service - CRUD operations and business logic for Tasks
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session

from ..models import Task, TaskStatus, TaskType, AutonomyLevel, Project
from .orchestrator import Orchestrator
from .readiness_engine import ReadinessEngine


class TaskService:
    """Service for managing tasks through their lifecycle"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.orchestrator = Orchestrator(db_session)
        self.readiness_engine = ReadinessEngine(db_session)
    
    def create_task(
        self,
        title: str,
        raw_request: str,
        task_type: TaskType = TaskType.AUTRE,
        domain: Optional[str] = None,
        project_id: Optional[str] = None,
        objective: Optional[str] = None,
        deliverables: Optional[List[str]] = None,
        hard_constraints: Optional[List[Dict]] = None,
        soft_preferences: Optional[List[Dict]] = None,
        contextual_preferences: Optional[List[Dict]] = None,
        deadline: Optional[datetime] = None,
        estimated_duration: Optional[int] = None,
        priority: int = 5,
        data_sources: Optional[List[str]] = None,
        success_criteria: Optional[List[str]] = None
    ) -> Task:
        """Create a new task in DRAFT status"""
        
        task = Task(
            title=title,
            raw_request=raw_request,
            type=task_type,
            domain=domain,
            project_id=project_id,
            objective=objective,
            autonomy_level=AutonomyLevel.SUPERVISED,  # Default per §16
            deadline=deadline,
            estimated_duration=estimated_duration,
            priority=priority,
            hard_constraints=hard_constraints or [],
            soft_preferences=soft_preferences or [],
            contextual_preferences=contextual_preferences or [],
            data_sources=data_sources or [],
            status=TaskStatus.DRAFT
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self.db.query(Task).filter(Task.id == task_id).first()
    
    def list_tasks(
        self,
        project_id: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        limit: int = 50
    ) -> List[Task]:
        """List tasks with optional filters"""
        query = self.db.query(Task)
        
        if project_id:
            query = query.filter(Task.project_id == project_id)
        if status:
            query = query.filter(Task.status == status)
        
        return query.order_by(Task.created_at.desc()).limit(limit).all()
    
    def update_task_readiness(
        self,
        task_id: str,
        dimension_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Update task readiness and transition to CLARIFICATION if needed.
        Returns readiness info and any clarification questions.
        """
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Calculate readiness
        readiness_global, is_ready, missing_critical = \
            self.readiness_engine.calculate_readiness(task, dimension_scores)
        
        task.readiness_score = readiness_global
        
        # Transition based on readiness
        if not is_ready:
            task.status = TaskStatus.CLARIFICATION
            questions = self.readiness_engine.get_clarification_questions(
                task, dimension_scores, missing_critical
            )
        else:
            task.status = TaskStatus.CONTEXTUALIZATION
            questions = []
        
        self.db.commit()
        self.db.refresh(task)
        
        return {
            "task_id": task.id,
            "readiness_score": readiness_global,
            "is_ready": is_ready,
            "missing_critical_dimensions": missing_critical,
            "clarification_questions": questions,
            "new_status": task.status.value
        }
    
    def answer_clarification(
        self,
        task_id: str,
        answers: Dict[str, str]
    ) -> Task:
        """Record answers to clarification questions"""
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Store answers in missing_info or context
        # For MVP, we'll just transition to CONTEXTUALIZATION
        task.status = TaskStatus.CONTEXTUALIZATION
        
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def propose_plan(self, task_id: str) -> Dict[str, Any]:
        """
        Generate a plan proposal for the task.
        In MVP, this is simplified - full LLM-based planning in Phase 3.
        """
        from ..models import Plan
        
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Check if plan already exists
        existing_plan = self.db.query(Plan).filter(Plan.task_id == task_id).first()
        if existing_plan:
            return {"plan": existing_plan, "created": False}
        
        # Create a basic plan structure based on task type
        plan_steps = self._generate_basic_plan_steps(task)
        
        # Propose autonomy level
        proposed_autonomy = self.orchestrator.propose_autonomy_level(task)
        
        # Get checkpoints based on autonomy
        checkpoints = self.orchestrator.get_checkpoints_for_autonomy(
            proposed_autonomy,
            plan_steps
        )
        
        plan = Plan(
            task_id=task_id,
            steps=plan_steps,
            checkpoints=checkpoints,
            estimated_effort=task.estimated_duration or 60,
            status="draft"
        )
        
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        
        return {
            "plan": plan,
            "created": True,
            "proposed_autonomy": proposed_autonomy.value,
            "checkpoints": checkpoints
        }
    
    def _generate_basic_plan_steps(self, task: Task) -> List[Dict]:
        """Generate basic plan steps based on task type"""
        
        base_steps = {
            TaskType.ANALYSE_DONNEES: [
                {"type": "comprehension", "name": "Comprendre la demande", "is_critical": False},
                {"type": "nettoyage", "name": "Nettoyer les données", "is_critical": True},
                {"type": "analyse", "name": "Analyser les données", "is_critical": True},
                {"type": "redaction", "name": "Rédiger le rapport", "is_critical": False},
                {"type": "presentation", "name": "Créer la présentation", "is_critical": False},
                {"type": "validation", "name": "Contrôle qualité", "is_critical": True}
            ],
            TaskType.REDACTION: [
                {"type": "comprehension", "name": "Comprendre la demande", "is_critical": False},
                {"type": "recherche", "name": "Rechercher les sources", "is_critical": True},
                {"type": "redaction", "name": "Rédiger le contenu", "is_critical": True},
                {"type": "validation", "name": "Contrôle qualité", "is_critical": True}
            ],
            TaskType.RECHERCHE: [
                {"type": "comprehension", "name": "Comprendre la demande", "is_critical": False},
                {"type": "recherche", "name": "Rechercher les sources", "is_critical": True},
                {"type": "analyse", "name": "Analyser les résultats", "is_critical": True},
                {"type": "redaction", "name": "Synthétiser", "is_critical": False},
                {"type": "validation", "name": "Contrôle qualité", "is_critical": True}
            ]
        }
        
        return base_steps.get(task.type, [
            {"type": "comprehension", "name": "Comprendre la demande", "is_critical": False},
            {"type": "execution", "name": "Exécuter la tâche", "is_critical": True},
            {"type": "validation", "name": "Contrôle qualité", "is_critical": True}
        ])
    
    def validate_plan(self, plan_id: str, approved: bool):
        """Validate or reject a plan"""
        from ..models import Plan
        
        plan = self.db.query(Plan).filter(Plan.id == plan_id).first()
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        
        if approved:
            plan.status = "validated"
            # Transition task to TOOL_SELECTION
            task = plan.task
            if task:
                task.status = TaskStatus.TOOL_SELECTION
        else:
            plan.status = "rejected"
            # Return task to PLANNING
            task = plan.task
            if task:
                task.status = TaskStatus.PLANNING
        
        self.db.commit()
        self.db.refresh(plan)
        
        return plan
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        task = self.get_task(task_id)
        if not task:
            return False
        
        self.db.delete(task)
        self.db.commit()
        return True
