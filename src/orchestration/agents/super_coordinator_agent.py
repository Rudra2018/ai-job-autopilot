#!/usr/bin/env python3
"""
🎯 SuperCoordinatorAgent: Master Orchestration & Multi-Agent Management System
Advanced coordination agent with circuit breaker patterns, load balancing, and intelligent routing.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import uuid
import logging
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import aiofiles

# Circuit breaker pattern imports
from functools import wraps
import statistics

class AgentType(Enum):
    """Types of agents in the system."""
    OCR_AGENT = "ocr_agent"
    PARSER_AGENT = "parser_agent"
    SKILL_AGENT = "skill_agent" 
    VALIDATION_AGENT = "validation_agent"
    COVER_LETTER_AGENT = "cover_letter_agent"
    COMPLIANCE_AGENT = "compliance_agent"
    TRACKING_AGENT = "tracking_agent"
    OPTIMIZATION_AGENT = "optimization_agent"
    SECURITY_AGENT = "security_agent"
    DISCOVERY_AGENT = "discovery_agent"
    AUTOMATION_AGENT = "automation_agent"
    UI_AGENT = "ui_agent"

class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class Priority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class WorkflowStep:
    """Individual step in a workflow."""
    step_id: str
    agent_type: AgentType
    operation: str
    input_data: Dict[str, Any]
    dependencies: List[str]
    timeout: float
    retry_count: int
    max_retries: int
    priority: Priority
    metadata: Dict[str, Any]

@dataclass
class WorkflowDefinition:
    """Complete workflow definition."""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    global_timeout: float
    retry_policy: Dict[str, Any]
    error_handling: Dict[str, Any]
    success_criteria: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class ExecutionResult:
    """Result of a workflow execution."""
    workflow_id: str
    execution_id: str
    status: WorkflowStatus
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[float]
    steps_completed: int
    steps_total: int
    success_rate: float
    results: Dict[str, Any]
    errors: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]

@dataclass
class AgentHealth:
    """Health status of an agent."""
    agent_type: AgentType
    status: str
    last_heartbeat: datetime
    response_time: float
    error_rate: float
    throughput: float
    resource_usage: Dict[str, float]
    alerts: List[str]

class CircuitBreaker:
    """Circuit breaker for protecting agents from cascading failures."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, expected_exception: Exception = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        self._lock = threading.Lock()
    
    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitBreakerState.HALF_OPEN
                else:
                    raise Exception("Circuit breaker is OPEN")
            
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
    
    def _on_success(self):
        with self._lock:
            self.failure_count = 0
            self.state = CircuitBreakerState.CLOSED
    
    def _on_failure(self):
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN

class SuperCoordinatorAgent:
    """
    Master coordination agent for managing all other agents and workflows.
    
    Features:
    - Multi-agent workflow orchestration
    - Circuit breaker patterns for fault tolerance
    - Load balancing and intelligent routing
    - Real-time performance monitoring
    - Adaptive retry mechanisms
    - Resource optimization
    - Comprehensive logging and analytics
    - Auto-scaling capabilities
    """
    
    def __init__(self,
                 max_concurrent_workflows: int = 10,
                 agent_timeout: float = 30.0,
                 circuit_breaker_enabled: bool = True,
                 auto_scaling_enabled: bool = True):
        """Initialize the super coordinator agent."""
        self.max_concurrent_workflows = max_concurrent_workflows
        self.agent_timeout = agent_timeout
        self.circuit_breaker_enabled = circuit_breaker_enabled
        self.auto_scaling_enabled = auto_scaling_enabled
        
        self.logger = self._setup_logging()
        
        # Agent registry and health monitoring
        self.agents: Dict[AgentType, Any] = {}
        self.agent_health: Dict[AgentType, AgentHealth] = {}
        self.circuit_breakers: Dict[AgentType, CircuitBreaker] = {}
        
        # Workflow management
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.active_executions: Dict[str, ExecutionResult] = {}
        self.execution_queue = asyncio.Queue()
        self.execution_history = deque(maxlen=1000)
        
        # Performance monitoring
        self.performance_metrics = defaultdict(list)
        self.system_metrics = {
            'total_workflows': 0,
            'successful_workflows': 0,
            'failed_workflows': 0,
            'average_execution_time': 0.0,
            'throughput': 0.0
        }
        
        # Load balancing
        self.agent_load: Dict[AgentType, float] = defaultdict(float)
        self.load_balancing_strategy = "round_robin"  # round_robin, least_loaded, weighted
        
        # Initialize components
        asyncio.create_task(self._initialize_system())
        
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging system."""
        logger = logging.getLogger("SuperCoordinatorAgent")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s] - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def _initialize_system(self):
        """Initialize the coordination system."""
        try:
            # Initialize circuit breakers
            if self.circuit_breaker_enabled:
                for agent_type in AgentType:
                    self.circuit_breakers[agent_type] = CircuitBreaker(
                        failure_threshold=5,
                        recovery_timeout=60
                    )
            
            # Start background tasks
            asyncio.create_task(self._workflow_executor())
            asyncio.create_task(self._health_monitor())
            asyncio.create_task(self._performance_collector())
            asyncio.create_task(self._auto_scaler())
            
            self.logger.info("SuperCoordinatorAgent initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize system: {e}")
            raise
    
    async def register_agent(self, 
                           agent_type: AgentType, 
                           agent_instance: Any,
                           health_check_endpoint: Optional[str] = None) -> bool:
        """
        Register an agent with the coordinator.
        
        Args:
            agent_type: Type of agent to register
            agent_instance: The agent instance
            health_check_endpoint: Optional health check endpoint
            
        Returns:
            bool: Registration success status
        """
        try:
            self.agents[agent_type] = agent_instance
            
            # Initialize health status
            self.agent_health[agent_type] = AgentHealth(
                agent_type=agent_type,
                status="healthy",
                last_heartbeat=datetime.now(timezone.utc),
                response_time=0.0,
                error_rate=0.0,
                throughput=0.0,
                resource_usage={},
                alerts=[]
            )
            
            self.logger.info(f"Registered agent: {agent_type.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register agent {agent_type.value}: {e}")
            return False
    
    async def create_workflow(self, 
                            name: str,
                            description: str,
                            workflow_definition: Dict[str, Any]) -> str:
        """
        Create a new workflow definition.
        
        Args:
            name: Workflow name
            description: Workflow description
            workflow_definition: Workflow configuration
            
        Returns:
            str: Workflow ID
        """
        try:
            workflow_id = str(uuid.uuid4())
            
            # Parse workflow steps
            steps = []
            for step_config in workflow_definition.get('steps', []):
                step = WorkflowStep(
                    step_id=step_config['step_id'],
                    agent_type=AgentType(step_config['agent_type']),
                    operation=step_config['operation'],
                    input_data=step_config.get('input_data', {}),
                    dependencies=step_config.get('dependencies', []),
                    timeout=step_config.get('timeout', 30.0),
                    retry_count=0,
                    max_retries=step_config.get('max_retries', 3),
                    priority=Priority(step_config.get('priority', 2)),
                    metadata=step_config.get('metadata', {})
                )
                steps.append(step)
            
            workflow = WorkflowDefinition(
                workflow_id=workflow_id,
                name=name,
                description=description,
                steps=steps,
                global_timeout=workflow_definition.get('global_timeout', 300.0),
                retry_policy=workflow_definition.get('retry_policy', {}),
                error_handling=workflow_definition.get('error_handling', {}),
                success_criteria=workflow_definition.get('success_criteria', {}),
                metadata=workflow_definition.get('metadata', {})
            )
            
            self.workflows[workflow_id] = workflow
            
            self.logger.info(f"Created workflow: {name} ({workflow_id})")
            return workflow_id
            
        except Exception as e:
            self.logger.error(f"Failed to create workflow: {e}")
            raise
    
    async def execute_workflow(self, 
                             workflow_id: str,
                             input_data: Optional[Dict[str, Any]] = None,
                             priority: Priority = Priority.MEDIUM) -> str:
        """
        Execute a workflow asynchronously.
        
        Args:
            workflow_id: ID of workflow to execute
            input_data: Input data for the workflow
            priority: Execution priority
            
        Returns:
            str: Execution ID
        """
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            execution_id = str(uuid.uuid4())
            workflow = self.workflows[workflow_id]
            
            # Create execution result tracker
            execution = ExecutionResult(
                workflow_id=workflow_id,
                execution_id=execution_id,
                status=WorkflowStatus.PENDING,
                start_time=datetime.now(timezone.utc),
                end_time=None,
                duration=None,
                steps_completed=0,
                steps_total=len(workflow.steps),
                success_rate=0.0,
                results={},
                errors=[],
                performance_metrics={}
            )
            
            self.active_executions[execution_id] = execution
            
            # Queue for execution
            await self.execution_queue.put({
                'execution_id': execution_id,
                'workflow': workflow,
                'input_data': input_data or {},
                'priority': priority
            })
            
            self.logger.info(f"Queued workflow execution: {execution_id}")
            return execution_id
            
        except Exception as e:
            self.logger.error(f"Failed to queue workflow execution: {e}")
            raise
    
    async def _workflow_executor(self):
        """Background task for executing workflows."""
        while True:
            try:
                # Get next workflow to execute
                workflow_task = await self.execution_queue.get()
                
                # Check if we're at capacity
                active_count = len([e for e in self.active_executions.values() 
                                  if e.status == WorkflowStatus.RUNNING])
                
                if active_count >= self.max_concurrent_workflows:
                    # Put back in queue and wait
                    await self.execution_queue.put(workflow_task)
                    await asyncio.sleep(1.0)
                    continue
                
                # Execute the workflow
                asyncio.create_task(self._execute_workflow_steps(workflow_task))
                
            except Exception as e:
                self.logger.error(f"Error in workflow executor: {e}")
                await asyncio.sleep(1.0)
    
    async def _execute_workflow_steps(self, workflow_task: Dict[str, Any]):
        """Execute individual workflow steps."""
        execution_id = workflow_task['execution_id']
        workflow = workflow_task['workflow']
        input_data = workflow_task['input_data']
        
        execution = self.active_executions[execution_id]
        execution.status = WorkflowStatus.RUNNING
        
        try:
            # Build dependency graph
            dependency_graph = self._build_dependency_graph(workflow.steps)
            
            # Execute steps in correct order
            completed_steps = set()
            step_results = {}
            
            while len(completed_steps) < len(workflow.steps):
                # Find steps ready to execute
                ready_steps = [
                    step for step in workflow.steps 
                    if step.step_id not in completed_steps and 
                    all(dep in completed_steps for dep in step.dependencies)
                ]
                
                if not ready_steps:
                    # Circular dependency or other issue
                    raise Exception("No steps ready to execute - possible circular dependency")
                
                # Execute ready steps concurrently
                step_tasks = []
                for step in ready_steps:
                    task = asyncio.create_task(
                        self._execute_single_step(step, step_results, input_data)
                    )
                    step_tasks.append((step, task))
                
                # Wait for completion
                for step, task in step_tasks:
                    try:
                        result = await task
                        step_results[step.step_id] = result
                        completed_steps.add(step.step_id)
                        execution.steps_completed += 1
                        
                        self.logger.info(f"Step completed: {step.step_id} in workflow {execution_id}")
                        
                    except Exception as e:
                        execution.errors.append({
                            'step_id': step.step_id,
                            'error': str(e),
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        })
                        
                        # Check error handling policy
                        if workflow.error_handling.get('stop_on_error', True):
                            raise e
                        else:
                            # Mark step as failed but continue
                            step_results[step.step_id] = {'error': str(e)}
                            completed_steps.add(step.step_id)
                            execution.steps_completed += 1
            
            # Workflow completed successfully
            execution.status = WorkflowStatus.COMPLETED
            execution.results = step_results
            execution.success_rate = 1.0 - (len(execution.errors) / len(workflow.steps))
            
            self.system_metrics['successful_workflows'] += 1
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.errors.append({
                'workflow_error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            self.system_metrics['failed_workflows'] += 1
            self.logger.error(f"Workflow execution failed: {execution_id} - {e}")
        
        finally:
            # Update execution metrics
            execution.end_time = datetime.now(timezone.utc)
            execution.duration = (execution.end_time - execution.start_time).total_seconds()
            
            # Move to history
            self.execution_history.append(execution)
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
            
            self.system_metrics['total_workflows'] += 1
            self._update_system_metrics()
    
    async def _execute_single_step(self, 
                                  step: WorkflowStep,
                                  step_results: Dict[str, Any],
                                  global_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step."""
        start_time = time.time()
        
        try:
            # Get agent for this step
            if step.agent_type not in self.agents:
                raise Exception(f"Agent not registered: {step.agent_type.value}")
            
            agent = self.agents[step.agent_type]
            
            # Apply circuit breaker if enabled
            if self.circuit_breaker_enabled and step.agent_type in self.circuit_breakers:
                circuit_breaker = self.circuit_breakers[step.agent_type]
                
                @circuit_breaker
                async def protected_call():
                    return await self._call_agent_operation(agent, step, step_results, global_input)
                
                result = await protected_call()
            else:
                result = await self._call_agent_operation(agent, step, step_results, global_input)
            
            # Update agent metrics
            execution_time = time.time() - start_time
            self._update_agent_metrics(step.agent_type, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._update_agent_metrics(step.agent_type, execution_time, False)
            
            # Retry logic
            if step.retry_count < step.max_retries:
                step.retry_count += 1
                await asyncio.sleep(2 ** step.retry_count)  # Exponential backoff
                return await self._execute_single_step(step, step_results, global_input)
            
            raise e
    
    async def _call_agent_operation(self,
                                   agent: Any,
                                   step: WorkflowStep,
                                   step_results: Dict[str, Any],
                                   global_input: Dict[str, Any]) -> Dict[str, Any]:
        """Call the specific operation on an agent."""
        # Prepare input data by merging step input, previous results, and global input
        input_data = {**global_input, **step.input_data}
        
        # Add results from dependencies
        for dep_id in step.dependencies:
            if dep_id in step_results:
                input_data[f"{dep_id}_result"] = step_results[dep_id]
        
        # Call the appropriate method based on the operation
        try:
            if hasattr(agent, step.operation):
                method = getattr(agent, step.operation)
                
                # Handle different calling patterns
                if asyncio.iscoroutinefunction(method):
                    result = await asyncio.wait_for(method(input_data), timeout=step.timeout)
                else:
                    result = await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(None, method, input_data),
                        timeout=step.timeout
                    )
            else:
                # Generic operation call
                if hasattr(agent, 'execute_operation'):
                    result = await asyncio.wait_for(
                        agent.execute_operation(step.operation, input_data),
                        timeout=step.timeout
                    )
                else:
                    raise Exception(f"Agent {step.agent_type.value} does not support operation: {step.operation}")
            
            return result if result is not None else {}
            
        except asyncio.TimeoutError:
            raise Exception(f"Operation {step.operation} timed out after {step.timeout}s")
        except Exception as e:
            raise Exception(f"Operation {step.operation} failed: {str(e)}")
    
    def _build_dependency_graph(self, steps: List[WorkflowStep]) -> Dict[str, List[str]]:
        """Build dependency graph for workflow steps."""
        graph = {}
        for step in steps:
            graph[step.step_id] = step.dependencies
        return graph
    
    def _update_agent_metrics(self, agent_type: AgentType, execution_time: float, success: bool):
        """Update agent performance metrics."""
        if agent_type in self.agent_health:
            health = self.agent_health[agent_type]
            
            # Update response time (moving average)
            health.response_time = (health.response_time * 0.9) + (execution_time * 0.1)
            
            # Update error rate
            if hasattr(health, '_total_calls'):
                health._total_calls += 1
                if not success:
                    health._error_count = getattr(health, '_error_count', 0) + 1
            else:
                health._total_calls = 1
                health._error_count = 0 if success else 1
            
            health.error_rate = health._error_count / health._total_calls
            
            # Update load
            self.agent_load[agent_type] = max(0, self.agent_load[agent_type] - 0.1)
            if not success:
                self.agent_load[agent_type] += 0.5
    
    def _update_system_metrics(self):
        """Update overall system metrics."""
        if self.system_metrics['total_workflows'] > 0:
            success_rate = self.system_metrics['successful_workflows'] / self.system_metrics['total_workflows']
            
            # Calculate average execution time
            if self.execution_history:
                durations = [e.duration for e in self.execution_history if e.duration]
                if durations:
                    self.system_metrics['average_execution_time'] = statistics.mean(durations)
        
        # Calculate throughput (workflows per minute)
        recent_executions = [
            e for e in self.execution_history 
            if e.end_time and e.end_time > datetime.now(timezone.utc) - timedelta(minutes=1)
        ]
        self.system_metrics['throughput'] = len(recent_executions)
    
    async def _health_monitor(self):
        """Background task for monitoring agent health."""
        while True:
            try:
                for agent_type, agent in self.agents.items():
                    # Basic health check
                    try:
                        start_time = time.time()
                        
                        # Try to call a health check method
                        if hasattr(agent, 'health_check'):
                            health_status = await asyncio.wait_for(agent.health_check(), timeout=5.0)
                        else:
                            health_status = {'status': 'healthy'}  # Assume healthy if no check
                        
                        response_time = time.time() - start_time
                        
                        # Update health record
                        if agent_type in self.agent_health:
                            health = self.agent_health[agent_type]
                            health.status = health_status.get('status', 'healthy')
                            health.last_heartbeat = datetime.now(timezone.utc)
                            health.response_time = response_time
                            health.resource_usage = health_status.get('resource_usage', {})
                    
                    except Exception as e:
                        if agent_type in self.agent_health:
                            health = self.agent_health[agent_type]
                            health.status = 'unhealthy'
                            health.alerts.append(f"Health check failed: {str(e)}")
                            
                            # Limit alerts list size
                            health.alerts = health.alerts[-10:]
                
                await asyncio.sleep(30)  # Health check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in health monitor: {e}")
                await asyncio.sleep(30)
    
    async def _performance_collector(self):
        """Background task for collecting performance metrics."""
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                
                # Collect system-wide metrics
                metrics = {
                    'timestamp': current_time.isoformat(),
                    'active_workflows': len(self.active_executions),
                    'queue_size': self.execution_queue.qsize(),
                    'system_metrics': self.system_metrics.copy(),
                    'agent_health': {
                        agent_type.value: {
                            'status': health.status,
                            'response_time': health.response_time,
                            'error_rate': health.error_rate,
                            'throughput': health.throughput
                        }
                        for agent_type, health in self.agent_health.items()
                    }
                }
                
                self.performance_metrics['system'].append(metrics)
                
                # Limit metrics history
                if len(self.performance_metrics['system']) > 1000:
                    self.performance_metrics['system'] = self.performance_metrics['system'][-1000:]
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                self.logger.error(f"Error in performance collector: {e}")
                await asyncio.sleep(60)
    
    async def _auto_scaler(self):
        """Background task for auto-scaling based on load."""
        if not self.auto_scaling_enabled:
            return
        
        while True:
            try:
                # Check if scaling is needed
                queue_size = self.execution_queue.qsize()
                active_workflows = len(self.active_executions)
                
                # Scale up if queue is growing or system is at capacity
                if queue_size > 5 and active_workflows >= self.max_concurrent_workflows:
                    # Increase capacity (in a real system, this would spawn new agent instances)
                    self.max_concurrent_workflows = min(self.max_concurrent_workflows + 2, 50)
                    self.logger.info(f"Scaled up: max concurrent workflows = {self.max_concurrent_workflows}")
                
                # Scale down if system is underutilized
                elif queue_size == 0 and active_workflows < self.max_concurrent_workflows // 2:
                    self.max_concurrent_workflows = max(self.max_concurrent_workflows - 1, 5)
                    self.logger.info(f"Scaled down: max concurrent workflows = {self.max_concurrent_workflows}")
                
                await asyncio.sleep(120)  # Check every 2 minutes
                
            except Exception as e:
                self.logger.error(f"Error in auto-scaler: {e}")
                await asyncio.sleep(120)
    
    async def get_workflow_status(self, execution_id: str) -> Optional[ExecutionResult]:
        """Get the current status of a workflow execution."""
        if execution_id in self.active_executions:
            return self.active_executions[execution_id]
        
        # Check execution history
        for execution in self.execution_history:
            if execution.execution_id == execution_id:
                return execution
        
        return None
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel a running workflow."""
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
            execution.status = WorkflowStatus.CANCELLED
            execution.end_time = datetime.now(timezone.utc)
            execution.duration = (execution.end_time - execution.start_time).total_seconds()
            
            # Move to history
            self.execution_history.append(execution)
            del self.active_executions[execution_id]
            
            self.logger.info(f"Cancelled workflow execution: {execution_id}")
            return True
        
        return False
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics."""
        return {
            'system_overview': self.system_metrics,
            'agent_health': {
                agent_type.value: asdict(health)
                for agent_type, health in self.agent_health.items()
            },
            'active_workflows': len(self.active_executions),
            'queue_size': self.execution_queue.qsize(),
            'capacity_utilization': len(self.active_executions) / self.max_concurrent_workflows,
            'circuit_breaker_status': {
                agent_type.value: cb.state.value
                for agent_type, cb in self.circuit_breakers.items()
            } if self.circuit_breaker_enabled else {},
            'performance_trends': self.performance_metrics.get('system', [])[-10:]  # Last 10 samples
        }
    
    async def create_job_application_workflow(self,
                                            job_posting: Dict[str, Any],
                                            resume_data: Dict[str, Any],
                                            user_preferences: Dict[str, Any]) -> str:
        """
        Create a complete job application workflow.
        
        Args:
            job_posting: Job posting information
            resume_data: Resume and profile data
            user_preferences: User configuration and preferences
            
        Returns:
            str: Workflow ID
        """
        workflow_definition = {
            'steps': [
                # Step 1: Parse and validate job posting
                {
                    'step_id': 'parse_job_posting',
                    'agent_type': 'parser_agent',
                    'operation': 'parse_job_posting',
                    'input_data': {'job_posting': job_posting},
                    'dependencies': [],
                    'timeout': 30.0,
                    'max_retries': 2,
                    'priority': 3
                },
                
                # Step 2: Analyze skills and requirements
                {
                    'step_id': 'analyze_skills',
                    'agent_type': 'skill_agent',
                    'operation': 'analyze_job_skills',
                    'input_data': {},
                    'dependencies': ['parse_job_posting'],
                    'timeout': 45.0,
                    'max_retries': 2,
                    'priority': 3
                },
                
                # Step 3: Validate application eligibility
                {
                    'step_id': 'validate_eligibility',
                    'agent_type': 'validation_agent',
                    'operation': 'validate_application',
                    'input_data': {'resume_data': resume_data},
                    'dependencies': ['parse_job_posting', 'analyze_skills'],
                    'timeout': 20.0,
                    'max_retries': 1,
                    'priority': 3
                },
                
                # Step 4: Generate personalized cover letter
                {
                    'step_id': 'generate_cover_letter',
                    'agent_type': 'cover_letter_agent',
                    'operation': 'generate_cover_letter',
                    'input_data': {'user_preferences': user_preferences},
                    'dependencies': ['parse_job_posting', 'analyze_skills'],
                    'timeout': 60.0,
                    'max_retries': 2,
                    'priority': 2
                },
                
                # Step 5: Compliance and legal check
                {
                    'step_id': 'compliance_check',
                    'agent_type': 'compliance_agent',
                    'operation': 'verify_compliance',
                    'input_data': {},
                    'dependencies': ['validate_eligibility'],
                    'timeout': 30.0,
                    'max_retries': 1,
                    'priority': 3
                },
                
                # Step 6: Submit application (if automated)
                {
                    'step_id': 'submit_application',
                    'agent_type': 'automation_agent',
                    'operation': 'submit_application',
                    'input_data': {'user_preferences': user_preferences},
                    'dependencies': ['generate_cover_letter', 'compliance_check'],
                    'timeout': 120.0,
                    'max_retries': 3,
                    'priority': 4
                },
                
                # Step 7: Track and record application
                {
                    'step_id': 'track_application',
                    'agent_type': 'tracking_agent',
                    'operation': 'track_application',
                    'input_data': {},
                    'dependencies': ['submit_application'],
                    'timeout': 15.0,
                    'max_retries': 1,
                    'priority': 1
                }
            ],
            'global_timeout': 600.0,  # 10 minutes total
            'retry_policy': {
                'max_workflow_retries': 1,
                'retry_delay': 30.0
            },
            'error_handling': {
                'stop_on_error': False,
                'critical_steps': ['compliance_check', 'submit_application']
            },
            'success_criteria': {
                'min_steps_completed': 5,
                'required_steps': ['parse_job_posting', 'analyze_skills', 'compliance_check']
            }
        }
        
        workflow_id = await self.create_workflow(
            name=f"Job Application: {job_posting.get('title', 'Unknown Position')}",
            description=f"Complete job application workflow for {job_posting.get('company', 'Unknown Company')}",
            workflow_definition=workflow_definition
        )
        
        return workflow_id

if __name__ == "__main__":
    async def demo():
        coordinator = SuperCoordinatorAgent()
        
        # Mock agents for demonstration
        class MockAgent:
            def __init__(self, name):
                self.name = name
            
            async def health_check(self):
                return {'status': 'healthy', 'resource_usage': {'cpu': 0.3, 'memory': 0.5}}
            
            async def execute_operation(self, operation, input_data):
                # Simulate work
                await asyncio.sleep(0.5)
                return {
                    'operation': operation,
                    'status': 'completed',
                    'result': f"Mock result from {self.name}",
                    'input_received': len(str(input_data))
                }
        
        # Register mock agents
        for agent_type in [AgentType.PARSER_AGENT, AgentType.SKILL_AGENT, AgentType.VALIDATION_AGENT]:
            mock_agent = MockAgent(agent_type.value)
            await coordinator.register_agent(agent_type, mock_agent)
        
        print(f"✅ Registered {len(coordinator.agents)} agents")
        
        # Create a simple workflow
        simple_workflow = {
            'steps': [
                {
                    'step_id': 'parse_data',
                    'agent_type': 'parser_agent',
                    'operation': 'parse_text',
                    'input_data': {'text': 'Sample job posting text'},
                    'dependencies': [],
                    'timeout': 10.0,
                    'max_retries': 2,
                    'priority': 2
                },
                {
                    'step_id': 'analyze_skills',
                    'agent_type': 'skill_agent',
                    'operation': 'extract_skills',
                    'input_data': {},
                    'dependencies': ['parse_data'],
                    'timeout': 10.0,
                    'max_retries': 2,
                    'priority': 2
                },
                {
                    'step_id': 'validate_result',
                    'agent_type': 'validation_agent',
                    'operation': 'validate_output',
                    'input_data': {},
                    'dependencies': ['analyze_skills'],
                    'timeout': 5.0,
                    'max_retries': 1,
                    'priority': 1
                }
            ]
        }
        
        workflow_id = await coordinator.create_workflow(
            "Demo Workflow",
            "Simple demonstration workflow",
            simple_workflow
        )
        print(f"📋 Created workflow: {workflow_id}")
        
        # Execute the workflow
        execution_id = await coordinator.execute_workflow(
            workflow_id,
            {'demo_input': 'test data'},
            Priority.HIGH
        )
        print(f"🚀 Started execution: {execution_id}")
        
        # Monitor execution
        for i in range(10):  # Wait up to 10 seconds
            status = await coordinator.get_workflow_status(execution_id)
            if status:
                print(f"📊 Status: {status.status.value} - Steps: {status.steps_completed}/{status.steps_total}")
                
                if status.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
                    break
            
            await asyncio.sleep(1)
        
        # Get final results
        final_status = await coordinator.get_workflow_status(execution_id)
        if final_status:
            print(f"🎯 Final Status: {final_status.status.value}")
            print(f"⏱️  Duration: {final_status.duration:.2f}s")
            print(f"✅ Success Rate: {final_status.success_rate:.1%}")
        
        # Get system metrics
        metrics = await coordinator.get_system_metrics()
        print(f"📈 System Metrics:")
        print(f"   • Total Workflows: {metrics['system_overview']['total_workflows']}")
        print(f"   • Success Rate: {metrics['system_overview']['successful_workflows']}/{metrics['system_overview']['total_workflows']}")
        print(f"   • Average Duration: {metrics['system_overview']['average_execution_time']:.2f}s")
        print(f"   • Active Workflows: {metrics['active_workflows']}")
    
    asyncio.run(demo())