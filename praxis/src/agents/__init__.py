"""
Praxis v0.3 - Agents Package

Implements the Agent registry from §9:
- Understanding Agent
- Planning Agent  
- Data Analysis Agent
- Document Agent
- Presentation Agent
- Research Agent
- Validation Agent
- Error Recovery Agent

Each Agent is responsible for a specific step type and uses appropriate Tools.
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Base class for all Praxis agents"""
    
    name: str = "BaseAgent"
    description: str = "Base agent"
    
    @abstractmethod
    def execute(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's task"""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this agent provides"""
        return []


class UnderstandingAgent(BaseAgent):
    """
    §9 - Understanding Agent
    
    Responsibilities:
    - Reformulate user request
    - Calculate readiness score
    - Identify missing information
    """
    
    name = "UnderstandingAgent"
    description = "Reformulates requests and calculates readiness"
    
    def execute(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process understanding step"""
        raw_request = step_data.get("raw_request", "")
        
        # MVP: simple reformulation
        # Full implementation would use LLM
        result = {
            "reformulated_request": f"Reformulation: {raw_request[:100]}...",
            "identified_type": step_data.get("task_type"),
            "readiness_dimensions": self._assess_dimensions(step_data)
        }
        
        return result
    
    def _assess_dimensions(self, data: Dict) -> Dict[str, float]:
        """Assess readiness dimensions (MVP placeholder)"""
        return {
            "objectif": 0.8,
            "contexte": 0.7,
            "donnees": 0.5,
            "livrables": 0.6
        }
    
    def get_capabilities(self) -> List[str]:
        return ["request_reformulation", "readiness_assessment", "gap_identification"]


class PlanningAgent(BaseAgent):
    """
    §9 - Planning Agent
    
    Responsibilities:
    - Build Plan with steps
    - Propose autonomy level
    - Identify dependencies
    """
    
    name = "PlanningAgent"
    description = "Creates execution plans"
    
    def execute(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a plan for the task"""
        task_type = step_data.get("task_type", "autre")
        
        # Generate plan steps based on type
        steps = self._generate_steps(task_type)
        
        result = {
            "steps": steps,
            "estimated_effort": sum(s.get("duration", 30) for s in steps),
            "proposed_autonomy": 1,  # Level 1 per §16
            "checkpoints": self._get_checkpoints(steps)
        }
        
        return result
    
    def _generate_steps(self, task_type: str) -> List[Dict]:
        """Generate plan steps based on task type"""
        # Simplified for MVP - full version uses LLM
        base_steps = [
            {"type": "comprehension", "name": "Comprendre", "duration": 15},
            {"type": "execution", "name": "Exécuter", "duration": 60},
            {"type": "validation", "name": "Valider", "duration": 20}
        ]
        return base_steps
    
    def _get_checkpoints(self, steps: List[Dict]) -> List[int]:
        """Get checkpoint indices for autonomy level 1"""
        return [0, len(steps) - 1]
    
    def get_capabilities(self) -> List[str]:
        return ["plan_generation", "autonomy_proposal", "dependency_mapping"]


class DataAnalysisAgent(BaseAgent):
    """
    §9 - Data Analysis Agent
    
    Responsibilities:
    - Clean data
    - Perform statistical analysis
    - Generate visualizations
    
    Tools: pandas, numpy, scipy, statsmodels, matplotlib, seaborn
    """
    
    name = "DataAnalysisAgent"
    description = "Analyzes and processes data"
    
    def execute(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data analysis step"""
        # MVP: placeholder for actual analysis
        # Full implementation would use pandas, numpy, etc.
        
        result = {
            "status": "completed",
            "artifacts_produced": [],
            "analysis_summary": "Data analysis completed"
        }
        
        return result
    
    def get_capabilities(self) -> List[str]:
        return [
            "data_cleaning",
            "statistical_analysis",
            "visualization",
            "hypothesis_testing"
        ]


class DocumentAgent(BaseAgent):
    """
    §9 - Document Agent
    
    Responsibilities:
    - Write reports
    - Format documents
    
    Tools: python-docx, Pandoc
    """
    
    name = "DocumentAgent"
    description = "Writes and formats documents"
    
    def execute(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute document generation step"""
        # MVP: placeholder
        # Full implementation would use python-docx
        
        result = {
            "status": "completed",
            "document_generated": True,
            "format": step_data.get("format", "docx")
        }
        
        return result
    
    def get_capabilities(self) -> List[str]:
        return ["report_writing", "document_formatting", "template_application"]


class PresentationAgent(BaseAgent):
    """
    §9 - Presentation Agent
    
    Responsibilities:
    - Create slides
    - Design visual supports
    
    Tools: python-pptx, matplotlib
    """
    
    name = "PresentationAgent"
    description = "Creates presentations"
    
    def execute(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute presentation creation step"""
        # MVP: placeholder
        # Full implementation would use python-pptx
        
        result = {
            "status": "completed",
            "slides_created": step_data.get("slide_count", 10),
            "format": "pptx"
        }
        
        return result
    
    def get_capabilities(self) -> List[str]:
        return ["slide_creation", "visual_design", "chart_integration"]


class ResearchAgent(BaseAgent):
    """
    §9 - Research Agent
    
    Responsibilities:
    - Search for sources
    - Populate Evidence
    - Query KnowledgeBase
    
    Tools: Web search, KB queries
    """
    
    name = "ResearchAgent"
    description = "Searches and sources information"
    
    def execute(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research step"""
        # MVP: placeholder
        # Full implementation would search web and KB
        
        result = {
            "status": "completed",
            "sources_found": [],
            "evidence_items": []
        }
        
        return result
    
    def get_capabilities(self) -> List[str]:
        return ["web_search", "source_evaluation", "evidence_collection"]


class ValidationAgent(BaseAgent):
    """
    §9 - Validation Agent / §10 - Quality Control
    
    Responsibilities:
    - Run quality checks
    - Verify traceability
    
    Tools: Programmatic rules, LLM-judge
    """
    
    name = "ValidationAgent"
    description = "Performs quality control"
    
    def execute(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validation step"""
        from ..services.validation_service import ValidationService
        
        # Would call ValidationService in full implementation
        result = {
            "status": "completed",
            "checks_passed": True,
            "verdict": "pass",
            "score": 0.85
        }
        
        return result
    
    def get_capabilities(self) -> List[str]:
        return [
            "consistency_check",
            "factual_accuracy",
            "methodological_validity",
            "constraint_compliance"
        ]


class ErrorRecoveryAgent(BaseAgent):
    """
    §9 - Error Recovery Agent / §3.16
    
    Responsibilities:
    - Handle ErrorEvents
    - Decide recovery strategy
    
    Tools: Decision logic only
    """
    
    name = "ErrorRecoveryAgent"
    description = "Manages error recovery"
    
    def execute(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute error recovery step"""
        from ..services.error_recovery import ErrorRecoveryService
        
        # Would call ErrorRecoveryService in full implementation
        result = {
            "status": "recovery_attempted",
            "strategy": step_data.get("strategy", "retry"),
            "success": True
        }
        
        return result
    
    def get_capabilities(self) -> List[str]:
        return ["error_diagnosis", "recovery_strategy", "escalation"]


# ============================================================================
# AGENT REGISTRY
# ============================================================================

AGENT_REGISTRY = {
    "UnderstandingAgent": UnderstandingAgent,
    "PlanningAgent": PlanningAgent,
    "DataAnalysisAgent": DataAnalysisAgent,
    "DocumentAgent": DocumentAgent,
    "PresentationAgent": PresentationAgent,
    "ResearchAgent": ResearchAgent,
    "ValidationAgent": ValidationAgent,
    "ErrorRecoveryAgent": ErrorRecoveryAgent
}


def get_agent(agent_name: str) -> Optional[BaseAgent]:
    """Get an agent instance by name"""
    agent_class = AGENT_REGISTRY.get(agent_name)
    if agent_class:
        return agent_class()
    return None


def list_available_agents() -> List[Dict[str, str]]:
    """List all available agents with their descriptions"""
    return [
        {"name": name, "description": cls.description}
        for name, cls in AGENT_REGISTRY.items()
    ]
