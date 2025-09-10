"""
AI Job Autopilot - Agent Orchestration System
This module orchestrates the complete multi-agent workflow for AI-powered job applications.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import traceback

# Import all specialized agents
from .agents.ocr_agent import OCRAgent
from .agents.parser_agent import ParserAgent
from .agents.skill_agent import SkillAgent
from .agents.discovery_agent import DiscoveryAgent
from .agents.ui_agent import UIAgent
from .agents.automation_agent import AutomationAgent
from .agents.coordinator_agent import CoordinatorAgent

# Utilities and validation
from .utils.data_validator import DataValidator
from .utils.quality_gates import QualityGateManager
from .utils.error_handler import WorkflowErrorHandler
from .utils.notification_manager import NotificationManager
from .utils.state_manager import WorkflowStateManager
from .utils.logger import WorkflowLogger

class AgentStatus(Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"

class WorkflowStatus(Enum):
    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class WorkflowConfig:
    workflow_id: str
    user_id: str
    execution_mode: str = "sequential"  # sequential, parallel, hybrid
    quality_threshold: float = 0.8
    max_retries: int = 3
    timeout_seconds: int = 300
    enable_stealth_mode: bool = True
    notification_enabled: bool = True
    auto_recovery: bool = True

@dataclass
class AgentResult:
    agent_name: str
    status: str
    result: Any
    confidence: float
    processing_time: float
    metadata: Dict[str, Any]
    errors: List[str] = None

class AIJobAutopilotOrchestrator:
    """
    Main orchestrator class that manages the complete AI job application workflow
    across all specialized agents.
    """
    
    def __init__(self, config: WorkflowConfig = None):
        self.config = config or WorkflowConfig(
            workflow_id=str(uuid.uuid4()),
            user_id="default_user"
        )
        
        # Initialize core systems
        self.logger = WorkflowLogger()
        self.state_manager = WorkflowStateManager()
        self.error_handler = WorkflowErrorHandler()
        self.notification_manager = NotificationManager()
        self.quality_gate_manager = QualityGateManager()
        self.data_validator = DataValidator()
        
        # Initialize agents
        self.agents = {}
        self.agent_status = {}
        self.agent_communication_hub = {}
        self.agent_performance_metrics = {}
        self._initialize_agents()
        
        # Enhanced workflow state
        self.workflow_state = None
        self.execution_results = {}
        self.inter_agent_messages = []
        
        # Load balancing and resource management
        self.agent_pool = asyncio.Queue()
        self.resource_monitor = {}
        
        # Circuit breaker pattern
        self.circuit_breakers = {}
        self._initialize_circuit_breakers()
        
    def _initialize_agents(self):
        """Initialize all specialized agents with their system prompts and configurations."""
        
        try:
            # OCR Agent - Handles document text extraction
            self.agents['OCRAgent'] = OCRAgent(
                name="OCRAgent",
                system_prompt=self._get_ocr_agent_prompt(),
                config={
                    'engines': ['google_vision', 'tesseract', 'easyocr', 'paddleocr'],
                    'fallback_enabled': True,
                    'quality_threshold': 0.7
                }
            )
            
            # Parser Agent - Parses resume content into structured data
            self.agents['ParserAgent'] = ParserAgent(
                name="ParserAgent",
                system_prompt=self._get_parser_agent_prompt(),
                config={
                    'ai_models': ['gpt-4o', 'claude-3.5-sonnet'],
                    'parsing_confidence_threshold': 0.8,
                    'structured_output': True
                }
            )
            
            # Skill Agent - Extracts and analyzes skills
            self.agents['SkillAgent'] = SkillAgent(
                name="SkillAgent",
                system_prompt=self._get_skill_agent_prompt(),
                config={
                    'nlp_models': ['spacy', 'bert', 'transformers'],
                    'skill_taxonomy': 'comprehensive',
                    'experience_calculation': True
                }
            )
            
            # Discovery Agent - Finds and matches jobs
            self.agents['DiscoveryAgent'] = DiscoveryAgent(
                name="DiscoveryAgent", 
                system_prompt=self._get_discovery_agent_prompt(),
                config={
                    'job_sources': ['linkedin', 'indeed', 'glassdoor', 'company_portals'],
                    'semantic_matching': True,
                    'salary_estimation': True,
                    'max_jobs_per_search': 100
                }
            )
            
            # UI Agent - Generates user interface components
            self.agents['UIAgent'] = UIAgent(
                name="UIAgent",
                system_prompt=self._get_ui_agent_prompt(),
                config={
                    'frameworks': ['react', 'vue', 'vanilla'],
                    'design_system': 'glassmorphism',
                    'responsive_design': True,
                    'accessibility_compliance': 'WCAG_2.1_AA'
                }
            )
            
            # Automation Agent - Handles job applications
            self.agents['AutomationAgent'] = AutomationAgent(
                name="AutomationAgent",
                system_prompt=self._get_automation_agent_prompt(),
                config={
                    'platforms': ['linkedin', 'indeed', 'company_portals'],
                    'stealth_mode': self.config.enable_stealth_mode,
                    'success_tracking': True,
                    'human_behavior_simulation': True
                }
            )
            
            # Coordinator Agent - Manages workflow
            self.agents['CoordinatorAgent'] = CoordinatorAgent(
                name="CoordinatorAgent",
                system_prompt=self._get_coordinator_agent_prompt(),
                config={
                    'orchestration_mode': 'intelligent',
                    'error_recovery': True,
                    'quality_enforcement': True
                }
            )
            
            # Set all agents as available initially and initialize communication hub
            for agent_name in self.agents.keys():
                self.agent_status[agent_name] = AgentStatus.AVAILABLE
                self.agent_communication_hub[agent_name] = {
                    'inbox': asyncio.Queue(),
                    'outbox': asyncio.Queue(),
                    'message_history': [],
                    'collaboration_partners': []
                }
                self.agent_performance_metrics[agent_name] = {
                    'success_count': 0,
                    'failure_count': 0,
                    'avg_processing_time': 0.0,
                    'quality_scores': [],
                    'last_execution': None
                }
                
            self.logger.info(f"Successfully initialized {len(self.agents)} agents with communication hub")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {str(e)}")
            raise
    
    def _initialize_circuit_breakers(self):
        """Initialize circuit breakers for each agent to prevent cascade failures."""
        for agent_name in ['OCRAgent', 'ParserAgent', 'SkillAgent', 'DiscoveryAgent', 'UIAgent', 'AutomationAgent']:
            self.circuit_breakers[agent_name] = {
                'state': 'CLOSED',  # CLOSED, OPEN, HALF_OPEN
                'failure_count': 0,
                'last_failure_time': None,
                'threshold': 3,  # failures before opening
                'timeout': 60,  # seconds before trying HALF_OPEN
                'success_count': 0
            }
    
    async def _check_circuit_breaker(self, agent_name: str) -> bool:
        """Check if agent circuit breaker allows execution."""
        breaker = self.circuit_breakers[agent_name]
        current_time = time.time()
        
        if breaker['state'] == 'OPEN':
            # Check if timeout has passed for HALF_OPEN
            if current_time - breaker['last_failure_time'] > breaker['timeout']:
                breaker['state'] = 'HALF_OPEN'
                await self.logger.info(f"Circuit breaker for {agent_name} moved to HALF_OPEN")
                return True
            return False
        
        return True  # CLOSED or HALF_OPEN allows execution
    
    async def _update_circuit_breaker(self, agent_name: str, success: bool):
        """Update circuit breaker state based on execution result."""
        breaker = self.circuit_breakers[agent_name]
        
        if success:
            breaker['success_count'] += 1
            if breaker['state'] == 'HALF_OPEN':
                breaker['state'] = 'CLOSED'
                breaker['failure_count'] = 0
                await self.logger.info(f"Circuit breaker for {agent_name} closed after successful execution")
        else:
            breaker['failure_count'] += 1
            breaker['last_failure_time'] = time.time()
            
            if breaker['failure_count'] >= breaker['threshold']:
                breaker['state'] = 'OPEN'
                await self.logger.warning(f"Circuit breaker for {agent_name} opened due to failures")
    
    async def send_inter_agent_message(self, from_agent: str, to_agent: str, message: Dict[str, Any]):
        """Send message between agents for collaboration."""
        message_obj = {
            'id': str(uuid.uuid4()),
            'from': from_agent,
            'to': to_agent,
            'timestamp': datetime.utcnow().isoformat(),
            'content': message,
            'type': message.get('type', 'data_exchange')
        }
        
        # Add to recipient's inbox
        await self.agent_communication_hub[to_agent]['inbox'].put(message_obj)
        
        # Add to sender's outbox history
        self.agent_communication_hub[from_agent]['outbox'].put_nowait(message_obj.copy())
        
        # Track message in global history
        self.inter_agent_messages.append(message_obj)
        
        await self.logger.info(f"Message sent from {from_agent} to {to_agent}: {message.get('type', 'data')}")
    
    async def get_agent_messages(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get pending messages for an agent."""
        messages = []
        inbox = self.agent_communication_hub[agent_name]['inbox']
        
        while not inbox.empty():
            try:
                message = await asyncio.wait_for(inbox.get(), timeout=0.1)
                messages.append(message)
            except asyncio.TimeoutError:
                break
        
        return messages

    async def execute_full_pipeline(self, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the complete AI job application pipeline.
        
        Args:
            initial_input: Dictionary containing user documents, preferences, and credentials
            
        Returns:
            Complete workflow results including UI components and automation results
        """
        
        workflow_start_time = time.time()
        
        try:
            # Initialize workflow
            self.workflow_state = await self._initialize_workflow(initial_input)
            
            await self.logger.info(
                f"Starting workflow {self.config.workflow_id} for user {self.config.user_id}"
            )
            
            # Execute the sequential pipeline
            pipeline_results = await self._execute_sequential_pipeline()
            
            # Collect and validate final results
            final_results = await self._collect_and_validate_results(pipeline_results)
            
            # Generate final outputs
            final_outputs = await self._generate_final_outputs(final_results)
            
            # Update workflow state
            workflow_duration = time.time() - workflow_start_time
            self.workflow_state['status'] = WorkflowStatus.COMPLETED.value
            self.workflow_state['completion_time'] = datetime.utcnow().isoformat()
            self.workflow_state['total_duration'] = workflow_duration
            
            await self.notification_manager.notify_completion(
                self.config.user_id, final_outputs
            )
            
            await self.logger.info(
                f"Workflow {self.config.workflow_id} completed successfully in {workflow_duration:.2f}s"
            )
            
            return final_outputs
            
        except Exception as e:
            await self._handle_workflow_failure(e)
            raise

    async def _execute_sequential_pipeline(self) -> Dict[str, AgentResult]:
        """Execute agents in the correct sequential order with dependency management."""
        
        pipeline_results = {}
        
        # Define the execution sequence with dependencies
        execution_sequence = [
            ('OCRAgent', None),  # No dependencies
            ('ParserAgent', ['OCRAgent']),  # Depends on OCR results
            ('SkillAgent', ['ParserAgent']),  # Depends on parsed data
            ('DiscoveryAgent', ['ParserAgent', 'SkillAgent']),  # Depends on profile and skills
            ('UIAgent', ['DiscoveryAgent']),  # Depends on job matches
            ('AutomationAgent', ['DiscoveryAgent', 'ParserAgent'])  # Depends on jobs and profile
        ]
        
        for agent_name, dependencies in execution_sequence:
            try:
                # Check dependencies
                if dependencies:
                    await self._validate_dependencies(dependencies, pipeline_results)
                
                # Prepare input for current agent
                agent_input = await self._prepare_agent_input(agent_name, pipeline_results)
                
                # Execute agent with retry logic
                agent_result = await self._execute_agent_with_retry(agent_name, agent_input)
                
                # Validate result quality
                await self._validate_agent_result(agent_name, agent_result)
                
                # Store result
                pipeline_results[agent_name] = agent_result
                
                # Update workflow state
                await self._update_workflow_progress(agent_name, agent_result)
                
                # Send progress notification
                await self.notification_manager.notify_progress(
                    self.config.user_id, agent_name, len(pipeline_results), len(execution_sequence)
                )
                
            except Exception as e:
                await self._handle_agent_failure(agent_name, e)
                
                # Decide whether to continue or abort
                if await self._should_abort_workflow(agent_name, e):
                    raise
                
        return pipeline_results

    async def _execute_agent_with_retry(self, agent_name: str, input_data: Any) -> AgentResult:
        """Execute an agent with retry logic, circuit breaker, and performance tracking."""
        
        # Check circuit breaker
        if not await self._check_circuit_breaker(agent_name):
            raise Exception(f"Agent {agent_name} circuit breaker is OPEN")
        
        agent = self.agents[agent_name]
        max_retries = self.config.max_retries
        last_error = None
        
        # Get any pending messages for this agent
        pending_messages = await self.get_agent_messages(agent_name)
        if pending_messages:
            input_data = await self._merge_messages_with_input(agent_name, input_data, pending_messages)
        
        for attempt in range(max_retries + 1):
            try:
                # Mark agent as busy
                self.agent_status[agent_name] = AgentStatus.BUSY
                
                start_time = time.time()
                
                # Execute agent with enhanced input
                result = await agent.process(input_data)
                
                processing_time = time.time() - start_time
                
                # Update performance metrics
                await self._update_agent_metrics(agent_name, processing_time, True, getattr(result, 'confidence', 1.0))
                
                # Update circuit breaker (success)
                await self._update_circuit_breaker(agent_name, True)
                
                # Create agent result
                agent_result = AgentResult(
                    agent_name=agent_name,
                    status="completed",
                    result=result,
                    confidence=getattr(result, 'confidence', 1.0),
                    processing_time=processing_time,
                    metadata={
                        'attempt_number': attempt + 1,
                        'input_size': len(str(input_data)),
                        'output_size': len(str(result)),
                        'messages_processed': len(pending_messages),
                        'circuit_breaker_state': self.circuit_breakers[agent_name]['state']
                    }
                )
                
                # Mark agent as available
                self.agent_status[agent_name] = AgentStatus.AVAILABLE
                
                # Send collaboration messages if needed
                await self._send_collaboration_messages(agent_name, result)
                
                await self.logger.info(
                    f"Agent {agent_name} completed successfully (attempt {attempt + 1})"
                )
                
                return agent_result
                
            except Exception as e:
                last_error = e
                
                # Update performance metrics (failure)
                await self._update_agent_metrics(agent_name, time.time() - start_time, False, 0.0)
                
                await self.logger.warning(
                    f"Agent {agent_name} failed (attempt {attempt + 1}): {str(e)}"
                )
                
                if attempt < max_retries:
                    # Wait before retry with exponential backoff
                    wait_time = (2 ** attempt) * 1.0  # 1s, 2s, 4s, 8s...
                    await asyncio.sleep(wait_time)
                    
                    # Apply error recovery if possible
                    input_data = await self.error_handler.recover_input_data(
                        agent_name, input_data, e
                    )
        
        # All retries exhausted - update circuit breaker
        await self._update_circuit_breaker(agent_name, False)
        self.agent_status[agent_name] = AgentStatus.ERROR
        raise Exception(f"Agent {agent_name} failed after {max_retries} retries: {last_error}")
    
    async def _update_agent_metrics(self, agent_name: str, processing_time: float, success: bool, quality_score: float):
        """Update performance metrics for an agent."""
        metrics = self.agent_performance_metrics[agent_name]
        
        if success:
            metrics['success_count'] += 1
        else:
            metrics['failure_count'] += 1
        
        # Update average processing time
        total_executions = metrics['success_count'] + metrics['failure_count']
        current_avg = metrics['avg_processing_time']
        metrics['avg_processing_time'] = ((current_avg * (total_executions - 1)) + processing_time) / total_executions
        
        # Track quality scores
        metrics['quality_scores'].append(quality_score)
        if len(metrics['quality_scores']) > 100:  # Keep only last 100 scores
            metrics['quality_scores'] = metrics['quality_scores'][-100:]
        
        metrics['last_execution'] = datetime.utcnow().isoformat()
    
    async def _merge_messages_with_input(self, agent_name: str, input_data: Any, messages: List[Dict[str, Any]]) -> Any:
        """Merge inter-agent messages with input data."""
        if not messages:
            return input_data
        
        # Create enhanced input with collaboration data
        enhanced_input = {
            'original_input': input_data,
            'collaboration_data': {},
            'agent_feedback': []
        }
        
        for message in messages:
            message_type = message.get('type', 'data_exchange')
            from_agent = message['from']
            
            if message_type == 'data_exchange':
                enhanced_input['collaboration_data'][from_agent] = message['content']
            elif message_type == 'feedback':
                enhanced_input['agent_feedback'].append({
                    'from': from_agent,
                    'feedback': message['content']
                })
        
        return enhanced_input
    
    async def _send_collaboration_messages(self, agent_name: str, result: Any):
        """Send collaboration messages based on agent results."""
        
        # Define collaboration patterns
        collaboration_rules = {
            'OCRAgent': ['ParserAgent'],  # OCR sends to Parser
            'ParserAgent': ['SkillAgent', 'DiscoveryAgent'],  # Parser sends to Skill and Discovery
            'SkillAgent': ['DiscoveryAgent'],  # Skill sends to Discovery
            'DiscoveryAgent': ['UIAgent', 'AutomationAgent'],  # Discovery sends to UI and Automation
            'UIAgent': [],  # UI doesn't send collaboration messages
            'AutomationAgent': []  # Automation doesn't send collaboration messages
        }
        
        target_agents = collaboration_rules.get(agent_name, [])
        
        for target_agent in target_agents:
            collaboration_message = {
                'type': 'data_exchange',
                'result_summary': {
                    'confidence': getattr(result, 'confidence', 1.0),
                    'processing_time': getattr(result, 'processing_time', 0.0),
                    'key_insights': self._extract_key_insights(agent_name, result)
                }
            }
            
            await self.send_inter_agent_message(agent_name, target_agent, collaboration_message)
    
    def _extract_key_insights(self, agent_name: str, result: Any) -> Dict[str, Any]:
        """Extract key insights from agent results for collaboration."""
        
        if agent_name == 'OCRAgent':
            return {
                'text_quality': getattr(result, 'text_quality', 'high'),
                'document_type': getattr(result, 'document_type', 'resume'),
                'extraction_confidence': getattr(result, 'confidence', 1.0)
            }
        elif agent_name == 'ParserAgent':
            return {
                'profile_completeness': getattr(result, 'profile_completeness', 0.8),
                'key_sections': getattr(result, 'identified_sections', []),
                'parsing_confidence': getattr(result, 'confidence', 1.0)
            }
        elif agent_name == 'SkillAgent':
            return {
                'skill_count': len(getattr(result, 'extracted_skills', [])),
                'technical_skills': getattr(result, 'technical_skills', []),
                'experience_level': getattr(result, 'experience_level', 'mid')
            }
        
        return {}

    async def _prepare_agent_input(self, agent_name: str, previous_results: Dict[str, AgentResult]) -> Any:
        """Prepare input data for each agent based on previous results."""
        
        if agent_name == 'OCRAgent':
            return {
                'documents': self.workflow_state['initial_input']['documents'],
                'processing_options': {
                    'engines': ['google_vision', 'tesseract', 'easyocr', 'paddleocr'],
                    'fallback_enabled': True,
                    'quality_priority': 'accuracy'
                }
            }
            
        elif agent_name == 'ParserAgent':
            ocr_result = previous_results['OCRAgent'].result
            return {
                'extracted_text': ocr_result['extracted_text'],
                'document_metadata': ocr_result.get('metadata', {}),
                'parsing_config': {
                    'ai_models': ['gpt-4o', 'claude-3.5-sonnet'],
                    'structured_output': True,
                    'confidence_threshold': 0.8
                }
            }
            
        elif agent_name == 'SkillAgent':
            parser_result = previous_results['ParserAgent'].result
            return {
                'resume_data': parser_result['structured_resume'],
                'extraction_config': {
                    'skill_domains': ['technical', 'soft_skills', 'industry_terms'],
                    'experience_calculation': True,
                    'strength_assessment': True
                }
            }
            
        elif agent_name == 'DiscoveryAgent':
            parser_result = previous_results['ParserAgent'].result
            skill_result = previous_results['SkillAgent'].result
            
            return {
                'candidate_profile': {
                    **parser_result['structured_resume'],
                    'skills_analysis': skill_result['extracted_skills']
                },
                'search_configuration': {
                    'target_companies': [
                        'google', 'meta', 'openai', 'anthropic', 'microsoft', 
                        'amazon', 'apple', 'netflix'
                    ],
                    'max_results': 50,
                    'include_salary_estimates': True
                },
                'user_preferences': self.workflow_state['initial_input'].get('preferences', {})
            }
            
        elif agent_name == 'UIAgent':
            discovery_result = previous_results['DiscoveryAgent'].result
            return {
                'job_matches': discovery_result['ranked_jobs'],
                'candidate_profile': discovery_result['candidate_profile'],
                'ui_specifications': {
                    'framework': 'react',
                    'design_system': 'glassmorphism',
                    'components': ['dashboard', 'job_cards', 'application_tracker'],
                    'responsive': True,
                    'accessibility': 'WCAG_2.1_AA'
                }
            }
            
        elif agent_name == 'AutomationAgent':
            discovery_result = previous_results['DiscoveryAgent'].result
            parser_result = previous_results['ParserAgent'].result
            
            return {
                'job_application_queue': discovery_result['ranked_jobs'][:10],  # Top 10 matches
                'candidate_profile': parser_result['structured_resume'],
                'automation_config': {
                    'platforms': ['linkedin', 'indeed', 'company_portals'],
                    'stealth_mode': self.config.enable_stealth_mode,
                    'max_applications_per_day': 20,
                    'human_behavior_simulation': True
                },
                'credentials': self.workflow_state['initial_input'].get('credentials', {})
            }
            
        else:
            raise ValueError(f"Unknown agent: {agent_name}")

    async def _validate_dependencies(self, dependencies: List[str], results: Dict[str, AgentResult]):
        """Validate that all required dependencies are available and valid."""
        
        for dep_agent in dependencies:
            if dep_agent not in results:
                raise Exception(f"Missing dependency: {dep_agent}")
                
            dep_result = results[dep_agent]
            if dep_result.status != "completed":
                raise Exception(f"Dependency {dep_agent} failed: {dep_result.status}")
                
            if dep_result.confidence < self.config.quality_threshold:
                await self.logger.warning(
                    f"Dependency {dep_agent} has low confidence: {dep_result.confidence}"
                )

    async def _validate_agent_result(self, agent_name: str, result: AgentResult):
        """Validate the quality and completeness of agent results."""
        
        # Quality gate validation
        quality_gate_result = await self.quality_gate_manager.evaluate_quality_gate(
            f"{agent_name}_quality_gate", result, self.workflow_state
        )
        
        if not quality_gate_result['passed']:
            await self.logger.warning(
                f"Agent {agent_name} failed quality gate: {quality_gate_result['overall_score']}"
            )
            
            if quality_gate_result['overall_score'] < 0.5:  # Critical failure threshold
                raise Exception(
                    f"Agent {agent_name} quality too low: {quality_gate_result['overall_score']}"
                )
        
        # Data validation
        validation_result = await self.data_validator.validate_agent_output(
            agent_name, result.result
        )
        
        if not validation_result['valid']:
            raise Exception(
                f"Agent {agent_name} output validation failed: {validation_result['errors']}"
            )

    async def _collect_and_validate_results(self, pipeline_results: Dict[str, AgentResult]) -> Dict[str, Any]:
        """Collect and validate all pipeline results."""
        
        collected_results = {}
        
        for agent_name, agent_result in pipeline_results.items():
            collected_results[agent_name] = {
                'result': agent_result.result,
                'confidence': agent_result.confidence,
                'processing_time': agent_result.processing_time,
                'metadata': agent_result.metadata
            }
        
        # Cross-validate results for consistency
        validation_results = await self.data_validator.cross_validate_results(collected_results)
        
        if not validation_results['consistent']:
            await self.logger.warning(
                f"Cross-validation issues detected: {validation_results['issues']}"
            )
        
        return collected_results

    async def _generate_final_outputs(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the final combined outputs for the user."""
        
        # Extract key results
        extracted_text = pipeline_results['OCRAgent']['result']['extracted_text']
        parsed_profile = pipeline_results['ParserAgent']['result']['structured_resume']
        skills_analysis = pipeline_results['SkillAgent']['result']['extracted_skills']
        job_matches = pipeline_results['DiscoveryAgent']['result']['ranked_jobs']
        ui_components = pipeline_results['UIAgent']['result']['generated_components']
        automation_results = pipeline_results['AutomationAgent']['result']['application_results']
        
        # Combine into final output
        final_output = {
            'workflow_id': self.config.workflow_id,
            'user_id': self.config.user_id,
            'completion_timestamp': datetime.utcnow().isoformat(),
            'pipeline_summary': {
                'total_processing_time': sum(
                    result['processing_time'] for result in pipeline_results.values()
                ),
                'overall_confidence': sum(
                    result['confidence'] for result in pipeline_results.values()
                ) / len(pipeline_results),
                'agents_executed': list(pipeline_results.keys())
            },
            'candidate_profile': {
                'extracted_text_summary': {
                    'total_characters': len(extracted_text),
                    'confidence': pipeline_results['OCRAgent']['confidence']
                },
                'structured_profile': parsed_profile,
                'skills_analysis': skills_analysis,
                'profile_completeness': self._calculate_profile_completeness(parsed_profile)
            },
            'job_discovery': {
                'total_jobs_found': len(job_matches),
                'top_matches': job_matches[:10],  # Top 10 matches
                'average_match_score': sum(
                    job.get('match_percentage', 0) for job in job_matches
                ) / len(job_matches) if job_matches else 0,
                'salary_insights': self._extract_salary_insights(job_matches)
            },
            'user_interface': {
                'generated_components': ui_components,
                'dashboard_ready': True,
                'responsive_design': ui_components.get('responsive', True),
                'accessibility_compliant': ui_components.get('accessibility', True)
            },
            'automation_execution': {
                'applications_submitted': automation_results.get('successful_applications', 0),
                'success_rate': automation_results.get('success_rate', 0),
                'platforms_used': automation_results.get('platforms_used', []),
                'next_actions': automation_results.get('recommendations', [])
            },
            'recommendations': {
                'profile_improvements': self._generate_profile_recommendations(
                    parsed_profile, skills_analysis
                ),
                'job_search_strategy': self._generate_job_search_recommendations(job_matches),
                'application_optimization': self._generate_application_recommendations(
                    automation_results
                )
            },
            'metadata': {
                'workflow_version': '1.0',
                'execution_environment': 'production',
                'quality_metrics': self._calculate_overall_quality_metrics(pipeline_results)
            }
        }
        
        return final_output

    async def _initialize_workflow(self, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize workflow state and validate initial input."""
        
        workflow_state = {
            'workflow_id': self.config.workflow_id,
            'user_id': self.config.user_id,
            'status': WorkflowStatus.INITIALIZED.value,
            'created_timestamp': datetime.utcnow().isoformat(),
            'initial_input': initial_input,
            'configuration': asdict(self.config),
            'agent_results': {},
            'quality_gates': {},
            'errors': [],
            'progress': {
                'completed_agents': 0,
                'total_agents': len(self.agents),
                'current_agent': None
            }
        }
        
        # Validate initial input
        input_validation = await self.data_validator.validate_initial_input(initial_input)
        if not input_validation['valid']:
            raise ValueError(f"Invalid initial input: {input_validation['errors']}")
        
        # Save initial state
        await self.state_manager.save_workflow_state(workflow_state)
        
        return workflow_state

    def _calculate_profile_completeness(self, profile: Dict[str, Any]) -> float:
        """Calculate the completeness score of the candidate profile."""
        
        required_sections = [
            'personal_information', 'professional_summary', 'work_experience',
            'education', 'skills_section'
        ]
        
        completed_sections = sum(
            1 for section in required_sections 
            if section in profile and profile[section]
        )
        
        return completed_sections / len(required_sections)

    def _extract_salary_insights(self, job_matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract salary insights from job matches."""
        
        salaries = []
        for job in job_matches:
            compensation = job.get('compensation_analysis', {})
            if compensation.get('base_salary_min'):
                salaries.append(compensation['base_salary_min'])
        
        if not salaries:
            return {'available': False}
        
        return {
            'available': True,
            'min_salary': min(salaries),
            'max_salary': max(salaries),
            'average_salary': sum(salaries) / len(salaries),
            'salary_distribution': {
                'below_100k': sum(1 for s in salaries if s < 100000),
                '100k_150k': sum(1 for s in salaries if 100000 <= s < 150000),
                '150k_200k': sum(1 for s in salaries if 150000 <= s < 200000),
                'above_200k': sum(1 for s in salaries if s >= 200000)
            }
        }

    def _generate_profile_recommendations(self, profile: Dict[str, Any], skills: Dict[str, Any]) -> List[str]:
        """Generate recommendations for profile improvement."""
        
        recommendations = []
        
        # Check profile completeness
        if not profile.get('professional_summary'):
            recommendations.append("Add a compelling professional summary")
        
        if not profile.get('certifications'):
            recommendations.append("Consider adding relevant certifications")
        
        # Check skills analysis
        technical_skills = skills.get('technical_skills', [])
        if len(technical_skills) < 10:
            recommendations.append("Expand technical skills section with more technologies")
        
        # Check experience
        work_experience = profile.get('work_experience', [])
        if len(work_experience) < 3:
            recommendations.append("Add more detailed work experience entries")
        
        return recommendations

    def _generate_job_search_recommendations(self, job_matches: List[Dict[str, Any]]) -> List[str]:
        """Generate job search strategy recommendations."""
        
        recommendations = []
        
        if not job_matches:
            recommendations.append("Expand search criteria - no matches found")
            return recommendations
        
        # Analyze match scores
        high_matches = sum(1 for job in job_matches if job.get('match_percentage', 0) > 80)
        
        if high_matches < 5:
            recommendations.append("Consider broadening your search criteria")
        
        # Analyze location preferences
        remote_jobs = sum(1 for job in job_matches if job.get('location_details', {}).get('work_arrangement') == 'remote')
        
        if remote_jobs > len(job_matches) * 0.5:
            recommendations.append("Many remote opportunities available - prioritize remote-first companies")
        
        return recommendations

    def _generate_application_recommendations(self, automation_results: Dict[str, Any]) -> List[str]:
        """Generate application optimization recommendations."""
        
        recommendations = []
        success_rate = automation_results.get('success_rate', 0)
        
        if success_rate < 0.8:
            recommendations.append("Improve application success rate by updating credentials")
        
        if automation_results.get('captcha_encounters', 0) > 5:
            recommendations.append("Consider using premium proxy services to reduce CAPTCHA challenges")
        
        return recommendations

    def _calculate_overall_quality_metrics(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall quality metrics for the workflow."""
        
        return {
            'overall_confidence': sum(
                result['confidence'] for result in pipeline_results.values()
            ) / len(pipeline_results),
            'processing_efficiency': sum(
                result['processing_time'] for result in pipeline_results.values()
            ),
            'success_rate': sum(
                1 for result in pipeline_results.values() 
                if result['confidence'] > 0.8
            ) / len(pipeline_results),
            'data_completeness': self._calculate_data_completeness(pipeline_results)
        }

    def _calculate_data_completeness(self, pipeline_results: Dict[str, Any]) -> float:
        """Calculate overall data completeness score."""
        
        # This would be implemented based on specific requirements
        # for now, return a basic calculation
        return 0.85

    async def _handle_agent_failure(self, agent_name: str, error: Exception):
        """Handle agent execution failures."""
        
        error_info = {
            'agent': agent_name,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.utcnow().isoformat(),
            'stack_trace': traceback.format_exc()
        }
        
        self.workflow_state['errors'].append(error_info)
        
        await self.logger.error(
            f"Agent {agent_name} failed: {str(error)}"
        )
        
        await self.notification_manager.notify_error(
            self.config.user_id, agent_name, error_info
        )

    async def _should_abort_workflow(self, failed_agent: str, error: Exception) -> bool:
        """Determine whether to abort the workflow based on the failure."""
        
        # Critical agents that must succeed
        critical_agents = ['OCRAgent', 'ParserAgent']
        
        if failed_agent in critical_agents:
            return True
        
        # Check error type
        critical_errors = ['AuthenticationError', 'PermissionError', 'InvalidInputError']
        
        if type(error).__name__ in critical_errors:
            return True
        
        return False

    async def _handle_workflow_failure(self, error: Exception):
        """Handle complete workflow failures."""
        
        self.workflow_state['status'] = WorkflowStatus.FAILED.value
        self.workflow_state['failure_reason'] = str(error)
        self.workflow_state['failure_timestamp'] = datetime.utcnow().isoformat()
        
        await self.logger.error(f"Workflow {self.config.workflow_id} failed: {str(error)}")
        
        await self.notification_manager.notify_workflow_failure(
            self.config.user_id, self.workflow_state
        )

    async def _update_workflow_progress(self, agent_name: str, result: AgentResult):
        """Update workflow progress after each agent completion."""
        
        self.workflow_state['agent_results'][agent_name] = asdict(result)
        self.workflow_state['progress']['completed_agents'] += 1
        self.workflow_state['progress']['current_agent'] = agent_name
        self.workflow_state['last_updated'] = datetime.utcnow().isoformat()
        
        await self.state_manager.save_workflow_state(self.workflow_state)

    # System prompt getters for each agent
    def _get_ocr_agent_prompt(self) -> str:
        return """
        You are the OCR Agent, responsible for extracting text from visual sources using multiple OCR engines.
        Use Google Vision, Tesseract, EasyOCR, and PaddleOCR with intelligent fallback strategies.
        Accept image or PDF input and return high-accuracy plain text extraction.
        Implement multi-engine fallback strategy if one fails.
        """
    
    def _get_parser_agent_prompt(self) -> str:
        return """
        You are the Parser Agent, responsible for parsing resume content into structured JSON format.
        Use GPT-4o and Claude 3.5 Sonnet to extract personal information, work experience, education, skills, and achievements.
        Return structured data with confidence scores and field validation.
        Handle multiple resume formats and maintain high parsing accuracy.
        """
    
    def _get_skill_agent_prompt(self) -> str:
        return """
        You are the Skill Agent, responsible for extracting and analyzing skills from parsed resume data.
        Use spaCy, BERT, and Transformers to identify technical skills, soft skills, and industry terms.
        Calculate years of experience per skill and assess skill strength.
        Return JSON structure linking skills to context, strength, and years of experience.
        """
    
    def _get_discovery_agent_prompt(self) -> str:
        return """
        You are the Discovery Agent, responsible for finding and matching job opportunities.
        Search real job data from top tech companies and perform semantic relevance scoring.
        Estimate salary based on location and experience, and filter by user preferences.
        Return ranked job list with match percentage and detailed notes.
        """
    
    def _get_ui_agent_prompt(self) -> str:
        return """
        You are the UI Agent, responsible for generating modern user interface components.
        Create React/Vue/HTML components with glassmorphism design and responsive layouts.
        Support dark/light mode and animate transitions with clean layouts.
        Generate HTML/CSS/JS or React code snippets from JSON/YAML specifications.
        """
    
    def _get_automation_agent_prompt(self) -> str:
        return """
        You are the Automation Agent, responsible for automating job applications across platforms.
        Handle LinkedIn, Indeed, and company portals with human-like interactions and stealth mode.
        Track application history, success/failure, and timestamps with credential management.
        Avoid detection while maintaining high application success rates.
        """
    
    def _get_coordinator_agent_prompt(self) -> str:
        return """
        You are the Coordinator Agent, responsible for managing workflow across all agents.
        Route input/output between agents, retry and validate outputs, maintain logs and metadata.
        Notify on errors or incomplete data without processing data directly.
        Orchestrate the complete pipeline: OCR → Parser → Skill → Discovery → UI → Automation.
        """

# Example usage and testing
async def main():
    """Example usage of the AI Job Autopilot Orchestrator."""
    
    # Configure workflow
    config = WorkflowConfig(
        workflow_id="test-workflow-001",
        user_id="ankit-thakur", 
        execution_mode="sequential",
        quality_threshold=0.8,
        enable_stealth_mode=True,
        notification_enabled=True
    )
    
    # Initialize orchestrator
    orchestrator = AIJobAutopilotOrchestrator(config)
    
    # Example initial input
    initial_input = {
        'documents': [
            {
                'document_id': 'resume-001',
                'document_type': 'resume',
                'file_path': '/path/to/resume.pdf',
                'file_format': 'pdf'
            }
        ],
        'preferences': {
            'desired_roles': ['Senior Software Engineer', 'Lead Developer'],
            'preferred_locations': ['San Francisco', 'Remote'],
            'minimum_salary': 150000,
            'remote_only': False
        },
        'credentials': {
            'linkedin': {
                'email': 'user@example.com',
                'password': 'secure_password'
            },
            'indeed': {
                'email': 'user@example.com',
                'password': 'secure_password'
            }
        }
    }
    
    try:
        # Execute full pipeline
        results = await orchestrator.execute_full_pipeline(initial_input)
        
        print("="*80)
        print("AI JOB AUTOPILOT - WORKFLOW COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f"Workflow ID: {results['workflow_id']}")
        print(f"Total Processing Time: {results['pipeline_summary']['total_processing_time']:.2f}s")
        print(f"Overall Confidence: {results['pipeline_summary']['overall_confidence']:.2%}")
        print(f"Jobs Found: {results['job_discovery']['total_jobs_found']}")
        print(f"Applications Submitted: {results['automation_execution']['applications_submitted']}")
        print(f"Success Rate: {results['automation_execution']['success_rate']:.2%}")
        print("="*80)
        
        return results
        
    except Exception as e:
        print(f"Workflow failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())