"""
Orchestrator - §3.5

The central decision-making component that connects all other objects.
Does not store data itself - reads Task, Context, memories, and registry
of Agent/Tool to make decisions.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session

from ..models import (
    Task, TaskStatus, Plan, Context, Execution, Artifact, 
    Deliverable, Project, Dependency, LearningLog, ErrorEvent,
    AutonomyLevel, TaskType
)
from ..config import settings
from .readiness_engine import ReadinessEngine


class Orchestrator:
    """
    §3.5 - Orchestrator: decision layer (not a data store)
    
    Responsibilities:
    - Transition tasks between states based on readiness
    - Choose default autonomy level per task type
    - Assign Agents to Plan steps
    - Decide recovery strategy after errors
    - Decide if observation becomes LearningCandidate
    - Arbitrate dependencies in Projects
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.readiness_engine = ReadinessEngine(db_session)
    
    # ========================================================================
    # STATE TRANSITIONS (§5)
    # ========================================================================
    
    def transition_to_understanding(self, task: Task) -> Task:
        """Transition from DRAFT to UNDERSTANDING"""
        task.status = TaskStatus.UNDERSTANDING
        return task
    
    def transition_to_clarification(
        self, 
        task: Task, 
        dimension_scores: Dict[str, float]
    ) -> tuple[Task, List[str]]:
        """
        Transition to CLARIFICATION if critical dimensions are insufficient.
        Returns task and list of clarification questions.
        """
        readiness_global, is_ready, missing_critical = \
            self.readiness_engine.calculate_readiness(task, dimension_scores)
        
        if not is_ready:
            task.status = TaskStatus.CLARIFICATION
            questions = self.readiness_engine.get_clarification_questions(
                task, dimension_scores, missing_critical
            )
            return task, questions
        
        # If ready, skip to contextualization
        task.status = TaskStatus.CONTEXTUALIZATION
        return task, []
    
    def transition_to_planning(self, task: Task) -> Task:
        """Transition from CONTEXTUALIZATION to PLANNING"""
        task.status = TaskStatus.PLANNING
        return task
    
    def transition_to_execution(self, plan: Plan) -> Plan:
        """Transition from PLAN_VALIDATION/TOOL_SELECTION to EXECUTION"""
        plan.status = "in_progress"
        return plan
    
    def transition_to_validation(self, execution: Execution) -> Execution:
        """Transition from EXECUTION to VALIDATION"""
        execution.status = "completed"
        return execution
    
    def transition_to_deliverable(self, task: Task) -> Task:
        """Transition from VALIDATION to DELIVERABLE"""
        task.status = TaskStatus.DELIVERABLE
        return task
    
    def transition_to_final_validation(self, task: Task) -> Task:
        """Transition from DELIVERABLE to FINAL_VALIDATION"""
        task.status = TaskStatus.FINAL_VALIDATION
        return task
    
    def transition_to_deployed(self, task: Task) -> Task:
        """Transition from FINAL_VALIDATION to DEPLOYED"""
        task.status = TaskStatus.DEPLOYED
        return task
    
    def transition_to_learning(self, task: Task) -> Task:
        """Transition to LEARNING after completion or abandonment"""
        task.status = TaskStatus.LEARNING
        return task
    
    # ========================================================================
    # AUTONOMY DECISIONS (§4)
    # ========================================================================
    
    def propose_autonomy_level(self, task: Task) -> AutonomyLevel:
        """
        Propose autonomy level based on task type and history.
        Never imposes - only proposes. MVP defaults to level 1.
        """
        # MVP: always propose level 1 until types are proven
        # Future: analyze UserMemory for successful completions
        return AutonomyLevel.SUPERVISED
    
    def get_checkpoints_for_autonomy(
        self, 
        autonomy_level: AutonomyLevel,
        plan_steps: List[Dict]
    ) -> List[int]:
        """
        Get checkpoint indices based on autonomy level.
        
        Level 0: checkpoint at every step
        Level 1: end of PLANNING + end of DELIVERABLE
        Level 2: end of PLANNING + critical steps + end of DELIVERABLE
        Level 3: end of DELIVERABLE only
        """
        checkpoints = []
        
        if autonomy_level == AutonomyLevel.ASSISTANCE:
            # Checkpoint at every step
            checkpoints = list(range(len(plan_steps)))
        
        elif autonomy_level == AutonomyLevel.SUPERVISED:
            # End of planning (step 0) and final deliverable
            checkpoints = [0, len(plan_steps) - 1]
        
        elif autonomy_level == AutonomyLevel.CONTROLLED:
            # End of planning, critical steps, and final
            checkpoints = [0]
            for i, step in enumerate(plan_steps):
                if step.get("is_critical", False):
                    checkpoints.append(i)
            checkpoints.append(len(plan_steps) - 1)
        
        elif autonomy_level == AutonomyLevel.ADVANCED:
            # Only final validation
            checkpoints = [len(plan_steps) - 1]
        
        return sorted(set(checkpoints))
    
    # ========================================================================
    # AGENT ASSIGNMENT (§9)
    # ========================================================================
    
    def assign_agent_to_step(
        self, 
        step: Dict, 
        user_memory: Optional[Any] = None
    ) -> str:
        """
        Assign an Agent to a plan step based on capabilities.
        
        Agent registry (§9):
        - Understanding Agent: reformulate, calculate readiness
        - Planning Agent: build Plan, propose autonomy
        - Data Analysis Agent: clean, analyze, test
        - Document Agent: write and format
        - Presentation Agent: visual supports
        - Research Agent: search, source, populate Evidence
        - Validation Agent: quality control
        - Error Recovery Agent: handle ErrorEvents
        """
        step_type = step.get("type", "").lower()
        
        agent_mapping = {
            "analyse": "DataAnalysisAgent",
            "nettoyage": "DataAnalysisAgent",
            "statistique": "DataAnalysisAgent",
            "redaction": "DocumentAgent",
            "rapport": "DocumentAgent",
            "presentation": "PresentationAgent",
            "diapositive": "PresentationAgent",
            "recherche": "ResearchAgent",
            "sourcing": "ResearchAgent",
            "validation": "ValidationAgent",
            "controle": "ValidationAgent",
            "planification": "PlanningAgent",
            "comprehension": "UnderstandingAgent",
            "clarification": "UnderstandingAgent"
        }
        
        # Check user's mastered tools first (if available)
        if user_memory and hasattr(user_memory, 'tools_mastered'):
            # Prefer agents whose tools the user has mastered
            pass
        
        # Default mapping
        for keyword, agent in agent_mapping.items():
            if keyword in step_type:
                return agent
        
        # Default to PlanningAgent for unknown steps
        return "PlanningAgent"
    
    # ========================================================================
    # DEPENDENCY ARBITRATION (§3.17)
    # ========================================================================
    
    def resolve_task_order(self, project: Project) -> List[Task]:
        """
        Resolve execution order based on dependency graph.
        Respects blocking dependencies strictly.
        """
        tasks = project.tasks
        if not tasks:
            return []
        
        # Build adjacency list
        graph = {task.id: [] for task in tasks}
        in_degree = {task.id: 0 for task in tasks}
        
        deps = self.db.query(Dependency).filter(
            Dependency.from_task_id.in_([t.id for t in tasks])
        ).all()
        
        for dep in deps:
            if dep.type == "blocking":
                graph[dep.from_task_id].append(dep.to_task_id)
                in_degree[dep.to_task_id] += 1
        
        # Topological sort (Kahn's algorithm)
        queue = [tid for tid, deg in in_degree.items() if deg == 0]
        ordered = []
        
        while queue:
            current = queue.pop(0)
            task = next((t for t in tasks if t.id == current), None)
            if task:
                ordered.append(task)
            
            for neighbor in graph.get(current, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Handle cycles: add remaining tasks
        if len(ordered) < len(tasks):
            remaining = [t for t in tasks if t not in ordered]
            ordered.extend(remaining)
        
        return ordered
    
    # ========================================================================
    # ERROR RECOVERY DECISIONS (§3.16)
    # ========================================================================
    
    def decide_recovery_strategy(
        self, 
        error_event: ErrorEvent
    ) -> str:
        """
        Decide recovery strategy based on error type and history.
        
        Strategies:
        - RETRY: transient technical error
        - CHANGE_STRATEGY: methodological failure
        - ASK_USER: missing information
        - ESCALATE: beyond retry limit
        - ABORT: unrecoverable
        """
        error_type = error_event.error_type
        retry_count = error_event.retry_count
        
        # Check retry limit
        if retry_count >= settings.MAX_RETRY_ATTEMPTS:
            return "escalate"
        
        # Technical errors: retry
        if error_type == "technical":
            return "retry"
        
        # Data errors: ask user or change strategy
        if error_type == "data":
            return "ask_user"
        
        # Permission errors: ask user
        if error_type == "permission":
            return "ask_user"
        
        # Methodological errors: change strategy
        if error_type == "methodological":
            return "change_strategy"
        
        # Default: retry once
        return "retry" if retry_count == 0 else "ask_user"
    
    # ========================================================================
    # LEARNING DECISIONS (§3.7)
    # ========================================================================
    
    def should_create_learning_candidate(
        self, 
        observation: Dict[str, Any],
        task_history: List[Task]
    ) -> bool:
        """
        Decide if an observation should become a LearningCandidate.
        
        Rule: single occurrence doesn't suffice unless explicit user correction.
        For MVP: log observations, candidates require explicit user trigger.
        """
        # MVP: never auto-promote to candidate
        # Requires explicit user validation
        return False
    
    def create_learning_log(
        self, 
        task: Task, 
        observation: str,
        what_was_observed: Dict[str, Any]
    ) -> LearningLog:
        """Create a learning observation log"""
        log = LearningLog(
            task_id=task.id,
            observation=observation,
            what_was_observed=what_was_observed,
            status="observation"
        )
        self.db.add(log)
        return log
    
    # ========================================================================
    # MAIN ORCHESTRATION FLOW
    # ========================================================================
    
    def process_task_lifecycle(self, task: Task) -> Dict[str, Any]:
        """
        Main orchestration method - processes a task through its lifecycle.
        Returns status and any required user actions.
        """
        result = {
            "task_id": task.id,
            "current_status": task.status.value,
            "requires_user_action": False,
            "user_actions": [],
            "next_state": None
        }
        
        # State machine
        if task.status == TaskStatus.DRAFT:
            task = self.transition_to_understanding(task)
            result["next_state"] = "understanding"
        
        elif task.status == TaskStatus.UNDERSTANDING:
            # Would need dimension scores here - simplified for MVP
            result["next_state"] = "contextualization"
        
        elif task.status == TaskStatus.CLARIFICATION:
            result["requires_user_action"] = True
            result["user_actions"].append("answer_clarification_questions")
        
        elif task.status == TaskStatus.CONTEXTUALIZATION:
            task = self.transition_to_planning(task)
            result["next_state"] = "planning"
        
        elif task.status == TaskStatus.PLANNING:
            # Propose autonomy level
            proposed_autonomy = self.propose_autonomy_level(task)
            result["proposed_autonomy"] = proposed_autonomy.value
            result["requires_user_action"] = True
            result["user_actions"].append("validate_plan_and_autonomy")
        
        elif task.status == TaskStatus.PLAN_VALIDATION:
            result["requires_user_action"] = True
            result["user_actions"].append("approve_plan")
        
        elif task.status == TaskStatus.TOOL_SELECTION:
            result["next_state"] = "execution"
        
        elif task.status == TaskStatus.EXECUTION:
            result["next_state"] = "validation"
        
        elif task.status == TaskStatus.ERROR_RECOVERY:
            result["requires_user_action"] = True
            result["user_actions"].append("decide_recovery")
        
        elif task.status == TaskStatus.VALIDATION:
            task = self.transition_to_deliverable(task)
            result["next_state"] = "deliverable"
        
        elif task.status == TaskStatus.DELIVERABLE:
            task = self.transition_to_final_validation(task)
            result["requires_user_action"] = True
            result["user_actions"].append("validate_deliverable")
        
        elif task.status == TaskStatus.FINAL_VALIDATION:
            if result.get("deliverable_approved"):
                task = self.transition_to_deployed(task)
                task = self.transition_to_learning(task)
                result["next_state"] = "deployed"
        
        self.db.commit()
        
        return result
