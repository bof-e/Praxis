"""
Praxis v0.3 - Core Data Models

Implements the object model from §3 of the conception document:
- Project (§3.1)
- Task (§3.2)
- Context (§3.4)
- Plan (§3.8)
- Artifact & Deliverable (§3.12, §3.15)
- Source & Evidence (§3.13)
- Dependency (§3.17)
- UserMemory, ProjectMemory, KnowledgeBase (§3.6)
- Learning objects (§3.7)
- Execution, Job, ErrorEvent (§3.10, §3.11, §3.16)
- Validation (§3.14)
"""

from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, 
    ForeignKey, Enum, JSON, Table
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum
import uuid


Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class TaskStatus(enum.Enum):
    DRAFT = "draft"
    UNDERSTANDING = "understanding"
    CLARIFICATION = "clarification"
    CONTEXTUALIZATION = "contextualization"
    PLANNING = "planning"
    PLAN_VALIDATION = "plan_validation"
    TOOL_SELECTION = "tool_selection"
    EXECUTION = "execution"
    ERROR_RECOVERY = "error_recovery"
    VALIDATION = "validation"
    DELIVERABLE = "deliverable"
    FINAL_VALIDATION = "final_validation"
    DEPLOYED = "deployed"
    LEARNING = "learning"
    ABANDONED = "abandoned"


class TaskType(enum.Enum):
    ANALYSE_DONNEES = "analyse_donnees"
    REPONSE_AO = "reponse_ao"
    RAPPORT_EVALUATION = "rapport_evaluation"
    PLANIFICATION = "planification"
    RECHERCHE = "recherche"
    REDACTION = "redaction"
    AUTRE = "autre"


class AutonomyLevel(enum.Enum):
    """Four levels of autonomy as per §4"""
    ASSISTANCE = 0  # Praxis proposes, user executes
    SUPERVISED = 1  # Praxis executes after plan validation
    CONTROLLED = 2  # Praxis executes non-critical steps alone
    ADVANCED = 3  # Full autonomy, final validation only


class ArtifactKind(enum.Enum):
    RAW_DATA = "raw_data"
    PROCESSED_DATA = "processed_data"
    ANALYSIS = "analysis"
    CHART = "chart"
    TABLE = "table"
    DRAFT = "draft"
    DELIVERABLE = "deliverable"


class ProjectStatus(enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class DependencyType(enum.Enum):
    BLOCKING = "blocking"
    INFORMATIONAL = "informational"


class SkillConfidence(enum.Enum):
    """Three levels of confidence as per §7"""
    KNOWN_SKILL = "known_skill"
    TRAINING_EXPOSURE = "training_exposure"
    UNVERIFIED = "unverified"


class ConstraintLevel(enum.Enum):
    HARD = "hard"
    SOFT = "soft"
    CONTEXTUAL = "contextual"


class JobStatus(enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ErrorType(enum.Enum):
    TECHNICAL = "technical"
    DATA = "data"
    PERMISSION = "permission"
    METHODOLOGICAL = "methodological"


class RecoveryStrategy(enum.Enum):
    RETRY = "retry"
    CHANGE_STRATEGY = "change_strategy"
    ASK_USER = "ask_user"
    ESCALATE = "escalate"
    ABORT = "abort"


class LearningStatus(enum.Enum):
    OBSERVATION = "observation"
    CANDIDATE = "candidate"
    VALIDATED = "validated"
    REJECTED = "rejected"


class SourceType(enum.Enum):
    WEB = "web"
    DOCUMENT = "document"
    DATABASE = "database"
    USER_INPUT = "user_input"
    KNOWLEDGE_BASE = "knowledge_base"


class KBContentType(enum.Enum):
    METHOD = "method"
    NORM = "norm"
    TEMPLATE = "template"
    REFERENCE = "reference"
    COURSE = "course"
    ARTICLE = "article"


class KBConfidence(enum.Enum):
    VALIDATED = "validated"
    EXPLORATORY = "exploratory"


# ============================================================================
# ASSOCIATION TABLES
# ============================================================================

task_dependencies = Table(
    'task_dependencies', Base.metadata,
    Column('from_task_id', String, ForeignKey('tasks.id'), primary_key=True),
    Column('to_task_id', String, ForeignKey('tasks.id'), primary_key=True),
    Column('type', Enum(DependencyType), nullable=False)
)


project_stakeholders = Table(
    'project_stakeholders', Base.metadata,
    Column('project_id', String, ForeignKey('projects.id'), primary_key=True),
    Column('stakeholder', String, primary_key=True)
)


project_objectives = Table(
    'project_objectives', Base.metadata,
    Column('project_id', String, ForeignKey('projects.id'), primary_key=True),
    Column('objective', Text, primary_key=True)
)


task_success_criteria = Table(
    'task_success_criteria', Base.metadata,
    Column('task_id', String, ForeignKey('tasks.id'), primary_key=True),
    Column('criterion', Text, primary_key=True)
)


task_missing_info = Table(
    'task_missing_info', Base.metadata,
    Column('task_id', String, ForeignKey('tasks.id'), primary_key=True),
    Column('info', Text, primary_key=True)
)


# ============================================================================
# CORE MODELS
# ============================================================================

class Project(Base):
    """§3.1 - Project: first-class container for related tasks"""
    __tablename__ = 'projects'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    deadline = Column(DateTime)
    
    # Relationships
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="project", cascade="all, delete-orphan")
    decisions = relationship("ProjectDecision", back_populates="project", cascade="all, delete-orphan")
    deliverables = relationship("Deliverable", back_populates="project", cascade="all, delete-orphan")
    
    # Memory reference
    project_memory_ref = Column(String, ForeignKey('project_memories.id'))
    project_memory = relationship("ProjectMemory", back_populates="project", foreign_keys=[project_memory_ref])
    
    # Resources & constraints
    budget_calls = Column(Integer)
    global_constraints = Column(JSON)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status={self.status})>"


class Task(Base):
    """§3.2 - Task: unit of work, enriched with new fields from v0.3"""
    __tablename__ = 'tasks'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    raw_request = Column(Text, nullable=False)
    objective = Column(Text)
    type = Column(Enum(TaskType), default=TaskType.AUTRE)
    domain = Column(String)
    
    # Status & readiness
    status = Column(Enum(TaskStatus), default=TaskStatus.DRAFT)
    readiness_score = Column(Float)
    readiness_model_ref = Column(String, ForeignKey('readiness_models.id'))
    
    # Autonomy (§4)
    autonomy_level = Column(Enum(AutonomyLevel), default=AutonomyLevel.SUPERVISED)
    
    # Timing (new in v0.3)
    deadline = Column(DateTime)
    estimated_duration = Column(Integer)  # minutes
    actual_effort = Column(Integer)  # minutes
    
    # Priority
    priority = Column(Integer, default=5)  # 1-10 scale
    
    # References
    project_id = Column(String, ForeignKey('projects.id'))
    parent_task_id = Column(String, ForeignKey('tasks.id'))
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    plan = relationship("Plan", uselist=False, back_populates="task", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="task", cascade="all, delete-orphan")
    deliverables_list = relationship("Deliverable", back_populates="task", cascade="all, delete-orphan")
    executions = relationship("Execution", back_populates="task", cascade="all, delete-orphan")
    learning_logs = relationship("LearningLog", back_populates="task", cascade="all, delete-orphan")
    
    # Constraints (§3.18 - three levels)
    hard_constraints = Column(JSON, default=list)
    soft_preferences = Column(JSON, default=list)
    contextual_preferences = Column(JSON, default=list)
    
    # Data sources
    data_sources = Column(JSON, default=list)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status={self.status})>"


class ReadinessModel(Base):
    """§3.3 - Readiness model dependent on task type"""
    __tablename__ = 'readiness_models'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_type = Column(Enum(TaskType), unique=True, nullable=False)
    
    # Dimensions and thresholds
    dimensions = Column(JSON, nullable=False)  # List of dimension names
    critical_dimensions = Column(JSON, default=list)  # Critical dimension names
    threshold_global = Column(Float, default=0.75)
    threshold_critical = Column(Float, default=0.50)
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<ReadinessModel(task_type={self.task_type}, threshold={self.threshold_global})>"


class Context(Base):
    """§3.4 - Context: assembled information for task execution"""
    __tablename__ = 'contexts'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey('tasks.id'), unique=True, nullable=False)
    
    # Assembled context components
    user_memory_excerpt = Column(JSON)
    project_memory_excerpt = Column(JSON)
    knowledge_base_excerpt = Column(JSON)
    external_resources = Column(JSON)
    
    created_at = Column(DateTime, server_default=func.now())
    
    task = relationship("Task", backref="context")
    
    def __repr__(self):
        return f"<Context(task_id={self.task_id})>"


class Plan(Base):
    """§3.8 - Plan: decomposition of task into steps"""
    __tablename__ = 'plans'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey('tasks.id'), unique=True, nullable=False)
    version = Column(Integer, default=1)
    
    # Plan content
    steps = Column(JSON, nullable=False)  # List of step definitions
    checkpoints = Column(JSON, default=list)  # Checkpoint definitions
    estimated_effort = Column(Integer)  # minutes
    dependencies = Column(JSON, default=list)
    risks = Column(JSON, default=list)
    
    status = Column(String, default="draft")  # draft, validated, in_progress, completed
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    task = relationship("Task", back_populates="plan")
    
    def __repr__(self):
        return f"<Plan(id={self.id}, task_id={self.task_id}, version={self.version})>"


class Artifact(Base):
    """§3.12 - Artifact: any produced file with provenance"""
    __tablename__ = 'artifacts'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey('tasks.id'))
    project_id = Column(String, ForeignKey('projects.id'))
    
    # Type and format
    kind = Column(Enum(ArtifactKind), nullable=False)
    format = Column(String, nullable=False)  # xlsx, docx, pptx, pdf, png, csv...
    
    # Storage
    file_ref = Column(String, nullable=False)  # Path or URL
    file_size = Column(Integer)  # bytes
    
    # Versioning (§3.19)
    version = Column(Integer, default=1)
    previous_version_id = Column(String, ForeignKey('artifacts.id'))
    
    # Provenance
    produced_by_agent = Column(String)
    produced_by_execution = Column(String, ForeignKey('executions.id'))
    derived_from = Column(JSON, default=list)  # List of parent artifact IDs
    
    # Metadata
    extra_metadata = Column(JSON, default=dict)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    task = relationship("Task", back_populates="artifacts")
    project = relationship("Project", back_populates="artifacts")
    execution = relationship("Execution", backref="artifacts_produced")
    previous_version = relationship("Artifact", remote_side=[id])
    
    def __repr__(self):
        return f"<Artifact(id={self.id}, kind={self.kind}, format={self.format})>"


class Deliverable(Base):
    """§3.15 - Deliverable: special Artifact marked for delivery
    
    Rule from §3.12: A Deliverable is an Artifact with kind=deliverable,
    produced in exact correspondence with an entry in Task.deliverables[]
    """
    __tablename__ = 'deliverables'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artifact_id = Column(String, ForeignKey('artifacts.id'), unique=True, nullable=False)
    task_id = Column(String, ForeignKey('tasks.id'))
    project_id = Column(String, ForeignKey('projects.id'))
    
    # Delivery tracking
    validated = Column(Boolean, default=False)
    delivered_at = Column(DateTime)
    delivery_method = Column(String)  # email, download, api...
    
    # References
    task = relationship("Task", back_populates="deliverables_list")
    project = relationship("Project", back_populates="deliverables")
    artifact = relationship("Artifact", backref="deliverable")
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<Deliverable(id={self.id}, artifact_id={self.artifact_id})>"


class Source(Base):
    """§3.13 - Source: origin of information"""
    __tablename__ = 'sources'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(Enum(SourceType), nullable=False)
    reference = Column(Text, nullable=False)  # URL, DOI, citation...
    retrieved_at = Column(DateTime, server_default=func.now())
    source_metadata = Column(JSON, default=dict)
    
    # Relationships
    evidences = relationship("Evidence", back_populates="source", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Source(id={self.id}, type={self.type})>"


class Evidence(Base):
    """§3.13 - Evidence: traceable support for claims"""
    __tablename__ = 'evidences'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String, ForeignKey('sources.id'), nullable=False)
    
    # Content
    excerpt_or_data_point = Column(Text, nullable=False)
    location = Column(String)  # Page number, timestamp, cell reference...
    
    # Link to deliverable content
    deliverable_section = Column(String)  # Which section this supports
    claim_type = Column(String)  # fact, deduction, hypothesis
    
    created_at = Column(DateTime, server_default=func.now())
    
    source = relationship("Source", back_populates="evidences")
    
    def __repr__(self):
        return f"<Evidence(id={self.id}, source_id={self.source_id})>"


class Dependency(Base):
    """§3.17 - Dependency: graph relationship between tasks"""
    __tablename__ = 'dependencies'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    from_task_id = Column(String, ForeignKey('tasks.id'), nullable=False)
    to_task_id = Column(String, ForeignKey('tasks.id'), nullable=False)
    type = Column(Enum(DependencyType), nullable=False)
    
    # Metadata
    description = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    
    from_task = relationship("Task", foreign_keys=[from_task_id])
    to_task = relationship("Task", foreign_keys=[to_task_id])
    
    def __repr__(self):
        return f"<Dependency({self.from_task_id} -> {self.to_task_id}, {self.type})>"


# ============================================================================
# MEMORY MODELS (§3.6)
# ============================================================================

class UserMemory(Base):
    """§3.6 - UserMemory: persistent knowledge about the user"""
    __tablename__ = 'user_memories'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Profile (enriched as per review point 21)
    profile = Column(JSON, nullable=False)  # identity, role, training level, objectives
    skills = Column(JSON, default=list)  # List with confidence levels (§7)
    preferred_methods = Column(JSON, default=list)
    tools_mastered = Column(JSON, default=list)
    templates = Column(JSON, default=list)
    writing_style = Column(JSON, default=dict)  # tone, typical length...
    working_habits = Column(JSON, default=dict)  # preferred hours...
    
    # Learning history
    decisions_log = Column(JSON, default=list)
    preferences = Column(JSON, default=list)
    learning_log = Column(JSON, default=list)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserMemory(id={self.id})>"


class ProjectMemory(Base):
    """§3.6 - ProjectMemory: scoped knowledge about a project"""
    __tablename__ = 'project_memories'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey('projects.id'), unique=True)
    
    # Scoped content
    context = Column(JSON, default=dict)
    decisions = Column(JSON, default=list)
    lessons_learned = Column(JSON, default=list)
    stakeholder_notes = Column(JSON, default=list)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    project = relationship("Project", back_populates="project_memory")
    
    def __repr__(self):
        return f"<ProjectMemory(project_id={self.project_id})>"


class KnowledgeBase(Base):
    """§3.6 - KnowledgeBase: domain knowledge (NEW in v0.3)"""
    __tablename__ = 'knowledge_bases'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    domain = Column(String, nullable=False)
    title = Column(String, nullable=False)
    
    # Content type
    content_type = Column(Enum(KBContentType), nullable=False)
    
    # Source and content
    source_ref = Column(String)  # Reference to original source
    content_ref = Column(String)  # Path or URL to content
    
    # Quality
    confidence = Column(Enum(KBConfidence), default=KBConfidence.EXPLORATORY)
    tags = Column(JSON, default=list)
    
    # Full content (for smaller items) or summary
    content = Column(Text)
    summary = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, domain={self.domain})>"


# ============================================================================
# LEARNING MODELS (§3.7)
# ============================================================================

class LearningLog(Base):
    """§3.7 - Learning: controlled chain Observation → Candidate → Validated"""
    __tablename__ = 'learning_logs'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey('tasks.id'))
    
    # Chain progression
    status = Column(Enum(LearningStatus), default=LearningStatus.OBSERVATION)
    
    # Observation
    observation = Column(Text, nullable=False)
    what_was_observed = Column(JSON, nullable=False)
    
    # Candidate (if progressed)
    hypothesis = Column(Text)
    confidence = Column(Float)
    
    # Validation (if progressed)
    validated_preference = Column(JSON)
    validated_at = Column(DateTime)
    validated_by_user = Column(Boolean)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    task = relationship("Task", back_populates="learning_logs")
    
    def __repr__(self):
        return f"<LearningLog(id={self.id}, status={self.status})>"


# ============================================================================
# EXECUTION MODELS (§3.10, §3.11, §3.16)
# ============================================================================

class Job(Base):
    """§3.10 - Job: async execution unit (deferred to Phase 3, but model ready)"""
    __tablename__ = 'jobs'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_ref = Column(String, ForeignKey('executions.id'), unique=True)
    
    status = Column(Enum(JobStatus), default=JobStatus.QUEUED)
    progress = Column(Float, default=0.0)
    worker_id = Column(String)
    
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    
    created_at = Column(DateTime, server_default=func.now())
    
    execution = relationship("Execution", backref="job")
    
    def __repr__(self):
        return f"<Job(id={self.id}, status={self.status})>"


class Execution(Base):
    """§3.11 - Execution: record of step execution"""
    __tablename__ = 'executions'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey('tasks.id'), nullable=False)
    plan_id = Column(String, ForeignKey('plans.id'))
    step_index = Column(Integer)
    
    # Tool used
    agent_assigned = Column(String)
    tool_used = Column(String)
    
    # Timing
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    
    # Result
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING)
    logs = Column(JSON, default=list)
    outputs_produced = Column(JSON, default=list)  # Artifact IDs
    
    created_at = Column(DateTime, server_default=func.now())
    
    task = relationship("Task", back_populates="executions")
    
    def __repr__(self):
        return f"<Execution(id={self.id}, task_id={self.task_id}, status={self.status})>"


class ErrorEvent(Base):
    """§3.16 - ErrorEvent: formalized error and recovery"""
    __tablename__ = 'error_events'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String, ForeignKey('executions.id'), nullable=False)
    
    # Error details
    error_type = Column(Enum(ErrorType), nullable=False)
    error_message = Column(Text, nullable=False)
    error_context = Column(JSON, default=dict)
    
    # Recovery attempts
    attempted_recoveries = Column(JSON, default=list)
    recovery_strategy = Column(Enum(RecoveryStrategy))
    retry_count = Column(Integer, default=0)
    
    # Resolution
    resolved = Column(Boolean, default=False)
    resolution_notes = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime)
    
    execution = relationship("Execution", backref="error_events")
    
    def __repr__(self):
        return f"<ErrorEvent(id={self.id}, type={self.error_type})>"


# ============================================================================
# VALIDATION MODEL (§3.14)
# ============================================================================

class Validation(Base):
    """§3.14 - Validation: quality control record"""
    __tablename__ = 'validations'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String, ForeignKey('executions.id'))
    
    # Checks performed
    checks_run = Column(JSON, nullable=False)
    corrections_applied = Column(JSON, default=list)
    
    # Result
    overall_verdict = Column(String, nullable=False)  # pass, pass_with_corrections, fail
    score = Column(Float)
    
    # Traceability check (§3.13)
    traceability_warnings = Column(JSON, default=list)
    
    created_at = Column(DateTime, server_default=func.now())
    
    execution = relationship("Execution", backref="validations")
    
    def __repr__(self):
        return f"<Validation(id={self.id}, verdict={self.overall_verdict})>"


# ============================================================================
# PROJECT DECISIONS
# ============================================================================

class ProjectDecision(Base):
    """Decisions made at project level"""
    __tablename__ = 'project_decisions'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey('projects.id'), nullable=False)
    
    decision = Column(Text, nullable=False)
    rationale = Column(Text)
    made_at = Column(DateTime, server_default=func.now())
    made_by = Column(String)  # 'user' or 'system'
    
    project = relationship("Project", back_populates="decisions")
    
    def __repr__(self):
        return f"<ProjectDecision(id={self.id}, project_id={self.project_id})>"


# ============================================================================
# METRICS (§14)
# ============================================================================

class SystemMetric(Base):
    """§14 - Metrics for measuring Praxis itself"""
    __tablename__ = 'system_metrics'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name = Column(String, nullable=False)
    
    # Value
    value = Column(Float, nullable=False)
    target = Column(Float)
    
    # Context
    task_id = Column(String, ForeignKey('tasks.id'))
    project_id = Column(String, ForeignKey('projects.id'))
    
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<SystemMetric(name={self.metric_name}, value={self.value})>"
