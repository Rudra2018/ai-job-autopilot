"""
AI Job Autopilot - Agents Module
Contains all specialized agents for the job application automation system.
"""

# Import available agents only
from .base_agent import BaseAgent, ProcessingResult, AgentConfig
from .ocr_agent import OCRAgent
from .parser_agent import ParserAgent
from .skill_agent import SkillAgent

# Try to import optional agents (may not exist yet)
try:
    from .discovery_agent import DiscoveryAgent
except ImportError:
    DiscoveryAgent = None

try:
    from .ui_agent import UIAgent
except ImportError:
    UIAgent = None

try:
    from .automation_agent import AutomationAgent
except ImportError:
    AutomationAgent = None

try:
    from .coordinator_agent import CoordinatorAgent
except ImportError:
    CoordinatorAgent = None

__all__ = [
    'BaseAgent',
    'ProcessingResult', 
    'AgentConfig',
    'OCRAgent',
    'ParserAgent',
    'SkillAgent'
]

# Add optional agents to __all__ if they exist
if DiscoveryAgent:
    __all__.append('DiscoveryAgent')
if UIAgent:
    __all__.append('UIAgent')
if AutomationAgent:
    __all__.append('AutomationAgent')
if CoordinatorAgent:
    __all__.append('CoordinatorAgent')