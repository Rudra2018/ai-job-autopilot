"""
Coordinator Agent for AI Job Autopilot System
Manages workflow orchestration, inter-agent communication, and system coordination.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from .base_agent import BaseAgent, ProcessingResult

class WorkflowStage(Enum):
    INITIALIZATION = "initialization"
    OCR_PROCESSING = "ocr_processing" 
    PARSING = "parsing"
    SKILL_ANALYSIS = "skill_analysis"
    JOB_DISCOVERY = "job_discovery"
    UI_GENERATION = "ui_generation"
    AUTOMATION = "automation"
    COMPLETION = "completion"

class AgentPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

@dataclass
class WorkflowTask:
    agent_name: str
    task_id: str
    stage: WorkflowStage
    priority: AgentPriority
    dependencies: List[str]
    input_data: Any
    expected_output: Dict[str, Any]
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class AgentHealthStatus:
    agent_name: str
    status: str
    last_heartbeat: datetime
    performance_score: float
    error_count: int
    success_rate: float

class CoordinatorAgent(BaseAgent):
    """
    Specialized agent for coordinating workflow across all other agents,
    managing inter-agent communication, and ensuring optimal system performance.
    """
    
    def _setup_agent_specific_config(self):
        """Setup Coordinator Agent specific configurations."""
        self.orchestration_mode = self.config.custom_settings.get('orchestration_mode', 'intelligent')
        self.error_recovery = self.config.custom_settings.get('error_recovery', True)
        self.quality_enforcement = self.config.custom_settings.get('quality_enforcement', True)
        
        # Workflow management
        self.active_workflows = {}
        self.workflow_templates = {}
        self.agent_registry = {}
        self.task_queue = asyncio.Queue()
        self.completed_tasks = {}
        self.failed_tasks = {}
        
        # Agent health monitoring
        self.agent_health_status = {}
        self.performance_metrics = {}
        
        # Communication and coordination
        self.message_bus = asyncio.Queue()
        self.coordination_rules = {}
        
        # Quality gates and checkpoints
        self.quality_gates = {
            'ocr_quality_threshold': 0.8,
            'parsing_confidence_threshold': 0.8,
            'skill_analysis_completeness': 0.7,
            'job_match_minimum': 5,
            'ui_component_completeness': 0.9,
            'automation_success_rate': 0.7
        }
        
        self._initialize_workflow_templates()
        self._initialize_coordination_rules()
        
        self.logger.info("Coordinator Agent initialized with intelligent orchestration")
    
    def _initialize_workflow_templates(self):
        """Initialize predefined workflow templates."""
        
        self.workflow_templates['standard_job_search'] = {
            'name': 'Standard Job Search Workflow',
            'description': 'Complete end-to-end job search and application process',
            'stages': [
                {
                    'stage': WorkflowStage.OCR_PROCESSING,
                    'agent': 'OCRAgent',
                    'priority': AgentPriority.CRITICAL,
                    'dependencies': [],
                    'quality_gate': 'ocr_quality_threshold'
                },
                {
                    'stage': WorkflowStage.PARSING,
                    'agent': 'ParserAgent', 
                    'priority': AgentPriority.CRITICAL,
                    'dependencies': ['OCRAgent'],
                    'quality_gate': 'parsing_confidence_threshold'
                },
                {
                    'stage': WorkflowStage.SKILL_ANALYSIS,
                    'agent': 'SkillAgent',
                    'priority': AgentPriority.HIGH,
                    'dependencies': ['ParserAgent'],
                    'quality_gate': 'skill_analysis_completeness'
                },
                {
                    'stage': WorkflowStage.JOB_DISCOVERY,
                    'agent': 'DiscoveryAgent',
                    'priority': AgentPriority.HIGH,
                    'dependencies': ['ParserAgent', 'SkillAgent'],
                    'quality_gate': 'job_match_minimum'
                },
                {
                    'stage': WorkflowStage.UI_GENERATION,
                    'agent': 'UIAgent',
                    'priority': AgentPriority.MEDIUM,
                    'dependencies': ['DiscoveryAgent'],
                    'quality_gate': 'ui_component_completeness'
                },
                {
                    'stage': WorkflowStage.AUTOMATION,
                    'agent': 'AutomationAgent',
                    'priority': AgentPriority.MEDIUM,
                    'dependencies': ['DiscoveryAgent', 'ParserAgent'],
                    'quality_gate': 'automation_success_rate'
                }
            ]
        }
    
    def _initialize_coordination_rules(self):
        """Initialize rules for inter-agent coordination."""
        
        self.coordination_rules = {
            'data_flow': {
                'OCRAgent': {
                    'outputs_to': ['ParserAgent'],
                    'data_format': 'extracted_text',
                    'quality_requirements': {'confidence': 0.8, 'completeness': 0.9}
                },
                'ParserAgent': {
                    'outputs_to': ['SkillAgent', 'DiscoveryAgent', 'AutomationAgent'],
                    'data_format': 'structured_profile',
                    'quality_requirements': {'confidence': 0.8, 'field_completeness': 0.7}
                },
                'SkillAgent': {
                    'outputs_to': ['DiscoveryAgent'],
                    'data_format': 'skill_analysis',
                    'quality_requirements': {'skill_count': 5, 'categorization_confidence': 0.7}
                },
                'DiscoveryAgent': {
                    'outputs_to': ['UIAgent', 'AutomationAgent'],
                    'data_format': 'job_matches',
                    'quality_requirements': {'minimum_matches': 5, 'match_quality': 0.6}
                },
                'UIAgent': {
                    'outputs_to': [],
                    'data_format': 'ui_components',
                    'quality_requirements': {'component_completeness': 0.9, 'accessibility': True}
                },
                'AutomationAgent': {
                    'outputs_to': [],
                    'data_format': 'automation_results',
                    'quality_requirements': {'success_rate': 0.7, 'error_rate': 0.3}
                }
            },
            'error_handling': {
                'OCRAgent': {'fallback_agents': [], 'retry_strategy': 'exponential_backoff'},
                'ParserAgent': {'fallback_agents': [], 'retry_strategy': 'alternative_model'},
                'SkillAgent': {'fallback_agents': [], 'retry_strategy': 'reduced_requirements'},
                'DiscoveryAgent': {'fallback_agents': [], 'retry_strategy': 'broader_search'},
                'UIAgent': {'fallback_agents': [], 'retry_strategy': 'simplified_components'},
                'AutomationAgent': {'fallback_agents': [], 'retry_strategy': 'reduced_volume'}
            },
            'performance_optimization': {
                'parallel_execution': ['SkillAgent', 'UIAgent'],
                'sequential_dependencies': [
                    ['OCRAgent', 'ParserAgent'],
                    ['ParserAgent', 'DiscoveryAgent'],
                    ['DiscoveryAgent', 'AutomationAgent']
                ],
                'resource_sharing': {
                    'high_memory': ['OCRAgent', 'ParserAgent'],
                    'high_cpu': ['SkillAgent', 'DiscoveryAgent'],
                    'network_intensive': ['AutomationAgent', 'DiscoveryAgent']
                }
            }
        }
    
    async def _validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate input data specific to Coordinator Agent."""
        errors = []
        
        if not isinstance(input_data, dict):
            errors.append("Input must be a dictionary")
            return {'valid': False, 'errors': errors}
        
        # Check for workflow specification
        if 'workflow_type' not in input_data:
            errors.append("Missing workflow_type specification")
        
        # Validate workflow exists
        workflow_type = input_data.get('workflow_type', '')
        if workflow_type and workflow_type not in self.workflow_templates:
            errors.append(f"Unknown workflow type: {workflow_type}")
        
        # Check for initial data
        if 'initial_data' not in input_data:
            errors.append("Missing initial_data for workflow")
        
        if errors:
            return {'valid': False, 'errors': errors}
        
        return {'valid': True, 'errors': []}
    
    async def _process_internal(self, input_data: Any) -> ProcessingResult:
        """Internal processing for workflow coordination."""
        
        try:
            workflow_type = input_data['workflow_type']
            initial_data = input_data['initial_data']
            workflow_config = input_data.get('workflow_config', {})
            
            # Initialize workflow
            workflow_id = await self._initialize_workflow(workflow_type, initial_data, workflow_config)
            
            # Execute workflow with coordination
            workflow_results = await self._execute_coordinated_workflow(workflow_id)
            
            # Validate workflow completion
            validation_results = await self._validate_workflow_completion(workflow_id, workflow_results)
            
            # Generate coordination insights
            coordination_insights = await self._generate_coordination_insights(workflow_id, workflow_results)
            
            return ProcessingResult(
                success=True,
                result={
                    'workflow_id': workflow_id,
                    'workflow_type': workflow_type,
                    'coordination_results': workflow_results,
                    'validation_results': validation_results,
                    'coordination_insights': coordination_insights,
                    'quality_metrics': self._calculate_workflow_quality_metrics(workflow_results),
                    'performance_metrics': self._calculate_workflow_performance_metrics(workflow_id)
                },
                confidence=validation_results.get('overall_confidence', 0.8),
                processing_time=0.0,
                metadata={
                    'agents_coordinated': len(workflow_results.get('agent_results', {})),
                    'quality_gates_passed': validation_results.get('quality_gates_passed', 0),
                    'coordination_mode': self.orchestration_mode
                }
            )
            
        except Exception as e:
            self.logger.error(f"Coordination processing failed: {str(e)}")
            return ProcessingResult(
                success=False,
                result=None,
                confidence=0.0,
                processing_time=0.0,
                metadata={'error': str(e)},
                errors=[str(e)]
            )
    
    async def _initialize_workflow(self, workflow_type: str, initial_data: Any, config: Dict[str, Any]) -> str:
        """Initialize a new workflow instance."""
        
        workflow_id = f"workflow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        workflow_template = self.workflow_templates[workflow_type]
        
        workflow_instance = {
            'id': workflow_id,
            'type': workflow_type,
            'template': workflow_template,
            'initial_data': initial_data,
            'config': config,
            'status': 'initialized',
            'created_at': datetime.utcnow().isoformat(),
            'stages': [],
            'agent_results': {},
            'quality_gates': {},
            'errors': [],
            'performance_metrics': {
                'start_time': datetime.utcnow(),
                'stage_timings': {},
                'agent_performance': {}
            }
        }
        
        # Create workflow tasks based on template
        for stage_config in workflow_template['stages']:
            task = WorkflowTask(
                agent_name=stage_config['agent'],
                task_id=f"{workflow_id}_{stage_config['stage'].value}",
                stage=stage_config['stage'],
                priority=stage_config['priority'],
                dependencies=stage_config['dependencies'],
                input_data=None,  # Will be set during execution
                expected_output={}
            )
            
            workflow_instance['stages'].append(task)
        
        self.active_workflows[workflow_id] = workflow_instance
        self.logger.info(f"Initialized workflow {workflow_id} of type {workflow_type}")
        
        return workflow_id
    
    async def _execute_coordinated_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute workflow with intelligent coordination."""
        
        workflow = self.active_workflows[workflow_id]
        workflow['status'] = 'running'
        
        # Sort stages by dependencies and priority
        execution_order = self._calculate_execution_order(workflow['stages'])
        
        agent_results = {}
        
        for stage_group in execution_order:
            # Execute stages in parallel if they have no dependencies on each other
            if len(stage_group) > 1:
                group_results = await self._execute_parallel_stages(workflow_id, stage_group)
            else:
                group_results = await self._execute_single_stage(workflow_id, stage_group[0])
            
            # Merge results
            agent_results.update(group_results)
            
            # Validate quality gates for completed stages
            for stage in stage_group:
                await self._validate_stage_quality_gate(workflow_id, stage, agent_results)
        
        workflow['status'] = 'completed'
        workflow['agent_results'] = agent_results
        workflow['performance_metrics']['end_time'] = datetime.utcnow()
        
        return {
            'workflow_id': workflow_id,
            'agent_results': agent_results,
            'execution_order': execution_order,
            'performance_summary': self._summarize_workflow_performance(workflow_id)
        }
    
    def _calculate_execution_order(self, stages: List[WorkflowTask]) -> List[List[WorkflowTask]]:
        """Calculate optimal execution order based on dependencies and priorities."""
        
        # Group stages that can be executed in parallel
        execution_groups = []
        remaining_stages = stages.copy()
        completed_agents = set()
        
        while remaining_stages:
            current_group = []
            
            # Find stages that can be executed (all dependencies met)
            for stage in remaining_stages:
                dependencies_met = all(dep in completed_agents for dep in stage.dependencies)
                if dependencies_met:
                    current_group.append(stage)
            
            if not current_group:
                # Dependency cycle or error - break it by selecting highest priority
                current_group = [min(remaining_stages, key=lambda x: x.priority.value)]
                self.logger.warning(f"Breaking potential dependency cycle by executing {current_group[0].agent_name}")
            
            # Sort group by priority
            current_group.sort(key=lambda x: x.priority.value)
            execution_groups.append(current_group)
            
            # Update completed agents and remaining stages
            for stage in current_group:
                completed_agents.add(stage.agent_name)
                remaining_stages.remove(stage)
        
        return execution_groups
    
    async def _execute_parallel_stages(self, workflow_id: str, stages: List[WorkflowTask]) -> Dict[str, Any]:
        """Execute multiple stages in parallel."""
        
        self.logger.info(f"Executing parallel stages: {[s.agent_name for s in stages]}")
        
        # Create tasks for parallel execution
        tasks = []
        for stage in stages:
            task = asyncio.create_task(self._execute_single_stage(workflow_id, stage))
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        combined_results = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Parallel stage {stages[i].agent_name} failed: {str(result)}")
                combined_results[stages[i].agent_name] = {
                    'status': 'error',
                    'error': str(result)
                }
            else:
                combined_results.update(result)
        
        return combined_results
    
    async def _execute_single_stage(self, workflow_id: str, stage: WorkflowTask) -> Dict[str, Any]:
        """Execute a single workflow stage."""
        
        workflow = self.active_workflows[workflow_id]
        stage_start_time = datetime.utcnow()
        
        self.logger.info(f"Executing stage {stage.stage.value} with agent {stage.agent_name}")
        
        try:
            # Prepare input data based on dependencies
            input_data = await self._prepare_stage_input_data(workflow_id, stage)
            
            # Mock agent execution (in real implementation, would call actual agent)
            result = await self._mock_agent_execution(stage.agent_name, input_data)
            
            # Record stage timing
            stage_end_time = datetime.utcnow()
            execution_time = (stage_end_time - stage_start_time).total_seconds()
            
            workflow['performance_metrics']['stage_timings'][stage.stage.value] = execution_time
            workflow['performance_metrics']['agent_performance'][stage.agent_name] = {
                'execution_time': execution_time,
                'status': 'success',
                'confidence': result.get('confidence', 0.8)
            }
            
            return {stage.agent_name: result}
            
        except Exception as e:
            self.logger.error(f"Stage {stage.stage.value} failed: {str(e)}")
            
            # Record failure metrics
            stage_end_time = datetime.utcnow()
            execution_time = (stage_end_time - stage_start_time).total_seconds()
            
            workflow['performance_metrics']['agent_performance'][stage.agent_name] = {
                'execution_time': execution_time,
                'status': 'failed',
                'error': str(e)
            }
            
            workflow['errors'].append({
                'stage': stage.stage.value,
                'agent': stage.agent_name,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Apply error recovery if enabled
            if self.error_recovery:
                recovery_result = await self._apply_error_recovery(workflow_id, stage, e)
                if recovery_result:
                    return {stage.agent_name: recovery_result}
            
            raise
    
    async def _prepare_stage_input_data(self, workflow_id: str, stage: WorkflowTask) -> Any:
        """Prepare input data for a stage based on its dependencies."""
        
        workflow = self.active_workflows[workflow_id]
        
        if not stage.dependencies:
            # First stage - use initial workflow data
            return workflow['initial_data']
        
        # Collect outputs from dependency agents
        dependency_outputs = {}
        for dep_agent in stage.dependencies:
            if dep_agent in workflow['agent_results']:
                dependency_outputs[dep_agent] = workflow['agent_results'][dep_agent]
        
        # Create structured input based on agent requirements
        if stage.agent_name == 'ParserAgent':
            return {
                'extracted_text': dependency_outputs.get('OCRAgent', {}).get('extracted_text', ''),
                'document_metadata': dependency_outputs.get('OCRAgent', {}).get('metadata', {}),
                'parsing_config': {'ai_models': ['gpt-4o'], 'structured_output': True}
            }
        elif stage.agent_name == 'SkillAgent':
            return {
                'resume_data': dependency_outputs.get('ParserAgent', {}).get('structured_resume', {}),
                'extraction_config': {'skill_domains': ['technical', 'soft_skills']}
            }
        elif stage.agent_name == 'DiscoveryAgent':
            return {
                'candidate_profile': {
                    **dependency_outputs.get('ParserAgent', {}).get('structured_resume', {}),
                    'skills_analysis': dependency_outputs.get('SkillAgent', {}).get('extracted_skills', {})
                },
                'search_configuration': {'target_companies': ['google', 'microsoft'], 'max_results': 50}
            }
        elif stage.agent_name == 'UIAgent':
            return {
                'job_matches': dependency_outputs.get('DiscoveryAgent', {}).get('ranked_jobs', []),
                'candidate_profile': dependency_outputs.get('ParserAgent', {}).get('structured_resume', {}),
                'ui_specifications': {'framework': 'react', 'components': ['dashboard', 'job_cards']}
            }
        elif stage.agent_name == 'AutomationAgent':
            return {
                'job_application_queue': dependency_outputs.get('DiscoveryAgent', {}).get('ranked_jobs', [])[:10],
                'candidate_profile': dependency_outputs.get('ParserAgent', {}).get('structured_resume', {}),
                'automation_config': {'platforms': ['linkedin'], 'stealth_mode': True}
            }
        
        # Default - pass all dependency outputs
        return dependency_outputs
    
    async def _mock_agent_execution(self, agent_name: str, input_data: Any) -> Dict[str, Any]:
        """Mock agent execution for demonstration purposes."""
        
        # Simulate processing time
        processing_time = random.uniform(1.0, 3.0)
        await asyncio.sleep(processing_time)
        
        # Generate mock results based on agent type
        if agent_name == 'OCRAgent':
            return {
                'extracted_text': 'Mock extracted text from resume document...',
                'confidence': 0.92,
                'metadata': {'pages': 2, 'quality': 'high'},
                'processing_time': processing_time
            }
        elif agent_name == 'ParserAgent':
            return {
                'structured_resume': {
                    'personal_information': {'full_name': 'John Doe', 'email': 'john@example.com'},
                    'work_experience': [{'title': 'Software Engineer', 'company': 'TechCorp'}],
                    'skills_section': ['Python', 'JavaScript', 'React']
                },
                'confidence': 0.88,
                'processing_time': processing_time
            }
        elif agent_name == 'SkillAgent':
            return {
                'extracted_skills': {
                    'technical_skills': ['Python', 'JavaScript', 'React', 'AWS'],
                    'soft_skills': ['Leadership', 'Communication'],
                    'experience_analysis': {'total_years': 5, 'seniority': 'mid'}
                },
                'confidence': 0.85,
                'processing_time': processing_time
            }
        elif agent_name == 'DiscoveryAgent':
            return {
                'ranked_jobs': [
                    {'job_id': 'job_1', 'title': 'Senior Engineer', 'company': 'Google', 'match_percentage': 92},
                    {'job_id': 'job_2', 'title': 'Software Engineer', 'company': 'Microsoft', 'match_percentage': 87}
                ],
                'total_jobs_found': 25,
                'confidence': 0.90,
                'processing_time': processing_time
            }
        elif agent_name == 'UIAgent':
            return {
                'generated_components': {
                    'dashboard': {'component': 'React dashboard', 'styles': 'CSS styles'},
                    'job_cards': {'component': 'React job cards', 'styles': 'CSS styles'}
                },
                'confidence': 0.95,
                'processing_time': processing_time
            }
        elif agent_name == 'AutomationAgent':
            return {
                'application_results': {
                    'successful_applications': 8,
                    'failed_applications': 2,
                    'success_rate': 0.8,
                    'platforms_used': ['linkedin']
                },
                'confidence': 0.80,
                'processing_time': processing_time
            }
        
        return {'status': 'completed', 'confidence': 0.8, 'processing_time': processing_time}
    
    async def _validate_stage_quality_gate(self, workflow_id: str, stage: WorkflowTask, agent_results: Dict[str, Any]):
        """Validate quality gate for a completed stage."""
        
        workflow = self.active_workflows[workflow_id]
        stage_template = None
        
        # Find stage template with quality gate
        for template_stage in workflow['template']['stages']:
            if template_stage['agent'] == stage.agent_name:
                stage_template = template_stage
                break
        
        if not stage_template or 'quality_gate' not in stage_template:
            return True
        
        quality_gate = stage_template['quality_gate']
        threshold = self.quality_gates.get(quality_gate, 0.8)
        
        agent_result = agent_results.get(stage.agent_name, {})
        
        # Apply quality gate validation based on type
        gate_passed = False
        
        if quality_gate == 'ocr_quality_threshold':
            confidence = agent_result.get('confidence', 0.0)
            gate_passed = confidence >= threshold
            
        elif quality_gate == 'parsing_confidence_threshold':
            confidence = agent_result.get('confidence', 0.0)
            gate_passed = confidence >= threshold
            
        elif quality_gate == 'skill_analysis_completeness':
            skills = agent_result.get('extracted_skills', {})
            tech_skills = len(skills.get('technical_skills', []))
            gate_passed = tech_skills >= 5  # Minimum 5 technical skills
            
        elif quality_gate == 'job_match_minimum':
            jobs_found = agent_result.get('total_jobs_found', 0)
            gate_passed = jobs_found >= threshold
            
        elif quality_gate == 'automation_success_rate':
            success_rate = agent_result.get('application_results', {}).get('success_rate', 0.0)
            gate_passed = success_rate >= threshold
        
        # Record quality gate result
        workflow['quality_gates'][stage.stage.value] = {
            'gate_type': quality_gate,
            'threshold': threshold,
            'passed': gate_passed,
            'actual_value': agent_result.get('confidence', 0.0),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if not gate_passed:
            self.logger.warning(f"Quality gate {quality_gate} failed for stage {stage.stage.value}")
            
        return gate_passed
    
    async def _apply_error_recovery(self, workflow_id: str, stage: WorkflowTask, error: Exception) -> Optional[Dict[str, Any]]:
        """Apply error recovery strategies based on agent and error type."""
        
        recovery_strategy = self.coordination_rules['error_handling'].get(stage.agent_name, {}).get('retry_strategy')
        
        if not recovery_strategy or stage.retry_count >= stage.max_retries:
            return None
        
        self.logger.info(f"Applying error recovery strategy '{recovery_strategy}' for {stage.agent_name}")
        
        stage.retry_count += 1
        
        if recovery_strategy == 'exponential_backoff':
            wait_time = 2 ** stage.retry_count
            await asyncio.sleep(wait_time)
            
        elif recovery_strategy == 'alternative_model':
            # Would switch to alternative AI model
            pass
            
        elif recovery_strategy == 'reduced_requirements':
            # Would lower quality thresholds
            pass
        
        # Retry the stage execution
        try:
            input_data = await self._prepare_stage_input_data(workflow_id, stage)
            return await self._mock_agent_execution(stage.agent_name, input_data)
        except Exception as retry_error:
            self.logger.error(f"Error recovery failed for {stage.agent_name}: {str(retry_error)}")
            return None
    
    async def _validate_workflow_completion(self, workflow_id: str, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that workflow completed successfully and meets quality requirements."""
        
        workflow = self.active_workflows[workflow_id]
        validation_results = {
            'workflow_id': workflow_id,
            'overall_success': True,
            'quality_gates_passed': 0,
            'quality_gates_total': len(workflow['quality_gates']),
            'agent_success_rate': 0.0,
            'overall_confidence': 0.0,
            'validation_errors': [],
            'recommendations': []
        }
        
        # Check quality gates
        for gate_name, gate_result in workflow['quality_gates'].items():
            if gate_result['passed']:
                validation_results['quality_gates_passed'] += 1
            else:
                validation_results['validation_errors'].append(f"Quality gate failed: {gate_name}")
        
        # Check agent success rates
        agent_results = workflow_results.get('agent_results', {})
        successful_agents = 0
        total_confidence = 0.0
        
        for agent_name, result in agent_results.items():
            if not result.get('error'):
                successful_agents += 1
            confidence = result.get('confidence', 0.0)
            total_confidence += confidence
        
        validation_results['agent_success_rate'] = successful_agents / len(agent_results) if agent_results else 0
        validation_results['overall_confidence'] = total_confidence / len(agent_results) if agent_results else 0
        
        # Determine overall success
        if validation_results['agent_success_rate'] < 0.8 or validation_results['quality_gates_passed'] < validation_results['quality_gates_total'] * 0.8:
            validation_results['overall_success'] = False
        
        # Generate recommendations
        if validation_results['agent_success_rate'] < 0.9:
            validation_results['recommendations'].append("Consider reviewing agent configurations for improved reliability")
        
        if validation_results['overall_confidence'] < 0.8:
            validation_results['recommendations'].append("Quality could be improved - consider stricter input validation")
        
        return validation_results
    
    async def _generate_coordination_insights(self, workflow_id: str, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights about coordination effectiveness and optimization opportunities."""
        
        workflow = self.active_workflows[workflow_id]
        performance_metrics = workflow['performance_metrics']
        
        insights = {
            'workflow_efficiency': {
                'total_execution_time': (performance_metrics['end_time'] - performance_metrics['start_time']).total_seconds(),
                'stage_breakdown': performance_metrics['stage_timings'],
                'bottleneck_stages': [],
                'optimization_opportunities': []
            },
            'agent_coordination': {
                'parallel_execution_effectiveness': 0.0,
                'dependency_chain_efficiency': 0.0,
                'communication_overhead': 0.0
            },
            'quality_assurance': {
                'quality_gate_effectiveness': len([g for g in workflow['quality_gates'].values() if g['passed']]) / len(workflow['quality_gates']) if workflow['quality_gates'] else 1.0,
                'error_recovery_usage': sum(1 for stage in workflow['stages'] if stage.retry_count > 0),
                'overall_quality_score': workflow_results.get('validation_results', {}).get('overall_confidence', 0.8)
            },
            'resource_utilization': {
                'agent_load_distribution': self._analyze_agent_load_distribution(workflow),
                'peak_resource_usage': 'moderate',  # Would be calculated from actual metrics
                'resource_optimization_suggestions': []
            }
        }
        
        # Identify bottlenecks
        stage_times = performance_metrics['stage_timings']
        if stage_times:
            max_time = max(stage_times.values())
            avg_time = sum(stage_times.values()) / len(stage_times)
            
            for stage, time_taken in stage_times.items():
                if time_taken > avg_time * 1.5:
                    insights['workflow_efficiency']['bottleneck_stages'].append({
                        'stage': stage,
                        'time_taken': time_taken,
                        'impact': 'high' if time_taken == max_time else 'medium'
                    })
        
        # Generate optimization recommendations
        if insights['workflow_efficiency']['bottleneck_stages']:
            insights['workflow_efficiency']['optimization_opportunities'].append(
                "Consider parallel processing for bottleneck stages where dependencies allow"
            )
        
        if insights['quality_assurance']['error_recovery_usage'] > 2:
            insights['workflow_efficiency']['optimization_opportunities'].append(
                "High error recovery usage detected - review agent reliability and input quality"
            )
        
        return insights
    
    def _analyze_agent_load_distribution(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how load was distributed across agents."""
        
        agent_performance = workflow['performance_metrics']['agent_performance']
        
        if not agent_performance:
            return {'distribution': 'unknown', 'balance_score': 0.0}
        
        execution_times = [perf['execution_time'] for perf in agent_performance.values()]
        
        if not execution_times:
            return {'distribution': 'unknown', 'balance_score': 0.0}
        
        avg_time = sum(execution_times) / len(execution_times)
        variance = sum((t - avg_time) ** 2 for t in execution_times) / len(execution_times)
        
        # Lower variance indicates better load distribution
        balance_score = max(0.0, 1.0 - (variance / (avg_time ** 2)))
        
        return {
            'distribution': 'balanced' if balance_score > 0.8 else 'unbalanced' if balance_score < 0.5 else 'moderate',
            'balance_score': balance_score,
            'avg_execution_time': avg_time,
            'execution_variance': variance
        }
    
    def _calculate_workflow_quality_metrics(self, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive quality metrics for the workflow."""
        
        agent_results = workflow_results.get('agent_results', {})
        
        if not agent_results:
            return {'overall_quality': 0.0, 'component_qualities': {}}
        
        component_qualities = {}
        total_confidence = 0.0
        
        for agent_name, result in agent_results.items():
            confidence = result.get('confidence', 0.0)
            component_qualities[agent_name] = confidence
            total_confidence += confidence
        
        overall_quality = total_confidence / len(agent_results)
        
        return {
            'overall_quality': overall_quality,
            'component_qualities': component_qualities,
            'quality_distribution': {
                'excellent': len([c for c in component_qualities.values() if c >= 0.9]),
                'good': len([c for c in component_qualities.values() if 0.8 <= c < 0.9]),
                'acceptable': len([c for c in component_qualities.values() if 0.7 <= c < 0.8]),
                'poor': len([c for c in component_qualities.values() if c < 0.7])
            }
        }
    
    def _calculate_workflow_performance_metrics(self, workflow_id: str) -> Dict[str, Any]:
        """Calculate performance metrics for the workflow execution."""
        
        workflow = self.active_workflows[workflow_id]
        performance = workflow['performance_metrics']
        
        total_time = (performance['end_time'] - performance['start_time']).total_seconds()
        
        return {
            'total_execution_time': total_time,
            'stage_execution_times': performance['stage_timings'],
            'agent_performance_summary': performance['agent_performance'],
            'throughput_metrics': {
                'stages_per_minute': len(performance['stage_timings']) / (total_time / 60) if total_time > 0 else 0,
                'avg_stage_time': sum(performance['stage_timings'].values()) / len(performance['stage_timings']) if performance['stage_timings'] else 0
            },
            'efficiency_score': self._calculate_workflow_efficiency_score(workflow)
        }
    
    def _calculate_workflow_efficiency_score(self, workflow: Dict[str, Any]) -> float:
        """Calculate an overall efficiency score for the workflow."""
        
        performance = workflow['performance_metrics']
        
        # Factors affecting efficiency
        total_time = (performance['end_time'] - performance['start_time']).total_seconds()
        error_count = len(workflow['errors'])
        retry_count = sum(stage.retry_count for stage in workflow['stages'])
        quality_gate_pass_rate = len([g for g in workflow['quality_gates'].values() if g['passed']]) / len(workflow['quality_gates']) if workflow['quality_gates'] else 1.0
        
        # Base efficiency (lower time is better, up to reasonable limits)
        time_efficiency = max(0.0, min(1.0, 300 / total_time)) if total_time > 0 else 0.0
        
        # Error penalties
        error_penalty = max(0.0, 0.1 * error_count)
        retry_penalty = max(0.0, 0.05 * retry_count)
        
        # Quality bonus
        quality_bonus = quality_gate_pass_rate * 0.2
        
        efficiency_score = time_efficiency - error_penalty - retry_penalty + quality_bonus
        
        return max(0.0, min(1.0, efficiency_score))
    
    def _summarize_workflow_performance(self, workflow_id: str) -> Dict[str, Any]:
        """Create a summary of workflow performance."""
        
        workflow = self.active_workflows[workflow_id]
        performance = workflow['performance_metrics']
        
        return {
            'execution_summary': {
                'total_time': (performance['end_time'] - performance['start_time']).total_seconds(),
                'stages_completed': len(performance['stage_timings']),
                'agents_involved': len(performance['agent_performance']),
                'errors_encountered': len(workflow['errors']),
                'quality_gates_passed': len([g for g in workflow['quality_gates'].values() if g['passed']])
            },
            'performance_highlights': {
                'fastest_stage': min(performance['stage_timings'], key=performance['stage_timings'].get) if performance['stage_timings'] else None,
                'slowest_stage': max(performance['stage_timings'], key=performance['stage_timings'].get) if performance['stage_timings'] else None,
                'most_reliable_agent': max(performance['agent_performance'], key=lambda x: performance['agent_performance'][x].get('confidence', 0)) if performance['agent_performance'] else None
            }
        }