"""
AI Job Autopilot - Orchestration Module
Multi-agent orchestration system for AI-powered job application automation.
"""

# Import available components with error handling
__version__ = "1.0.0"
__all__ = []

# Try to import full orchestrator
try:
    from .agent_orchestrator import AIJobAutopilotOrchestrator, WorkflowConfig
    __all__.extend(['AIJobAutopilotOrchestrator', 'WorkflowConfig'])
except ImportError:
    AIJobAutopilotOrchestrator = None
    WorkflowConfig = None

# Always available - IntegratedOrchestrator doesn't depend on missing agents
from .integrated_orchestrator import IntegratedOrchestrator
__all__.append('IntegratedOrchestrator')

# Try to import Streamlit integration
try:
    from .streamlit_integration import StreamlitOrchestrationUI, add_orchestration_to_main_app
    __all__.extend(['StreamlitOrchestrationUI', 'add_orchestration_to_main_app'])
except ImportError:
    StreamlitOrchestrationUI = None
    add_orchestration_to_main_app = None