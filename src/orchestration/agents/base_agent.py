"""
Base Agent Class for AI Job Autopilot System
Defines the common interface and functionality for all specialized agents.
"""

import asyncio
import json
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class AgentConfig:
    """Configuration for agent initialization."""
    name: str
    timeout_seconds: int = 300
    max_retries: int = 3
    confidence_threshold: float = 0.7
    debug_mode: bool = False
    custom_settings: Dict[str, Any] = None

@dataclass
class ProcessingResult:
    """Standard result format for agent processing."""
    success: bool
    result: Any
    confidence: float
    processing_time: float
    metadata: Dict[str, Any]
    errors: List[str] = None
    warnings: List[str] = None

class BaseAgent(ABC):
    """
    Abstract base class for all AI Job Autopilot agents.
    Provides common functionality and enforces consistent interfaces.
    """
    
    def __init__(self, name: str, system_prompt: str, config: Dict[str, Any] = None):
        self.name = name
        self.system_prompt = system_prompt
        self.config = AgentConfig(
            name=name,
            **(config or {})
        )
        
        # Initialize logging
        self.logger = logging.getLogger(f"agent.{name}")
        
        # Agent state
        self.is_initialized = False
        self.last_processing_time = None
        self.total_processing_count = 0
        self.success_count = 0
        self.error_count = 0
        
        # Initialize the agent
        self._initialize()
    
    def _initialize(self):
        """Initialize the agent with specific configurations."""
        try:
            self._setup_agent_specific_config()
            self.is_initialized = True
            self.logger.info(f"Agent {self.name} initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize agent {self.name}: {str(e)}")
            raise
    
    @abstractmethod
    def _setup_agent_specific_config(self):
        """Setup agent-specific configurations. Override in subclasses."""
        pass
    
    @abstractmethod
    async def _process_internal(self, input_data: Any) -> ProcessingResult:
        """
        Internal processing method to be implemented by each agent.
        
        Args:
            input_data: Input data specific to the agent
            
        Returns:
            ProcessingResult containing the processed output
        """
        pass
    
    async def process(self, input_data: Any) -> ProcessingResult:
        """
        Main processing method with error handling, validation, and metrics.
        
        Args:
            input_data: Input data for processing
            
        Returns:
            ProcessingResult with processed data or error information
        """
        
        if not self.is_initialized:
            return ProcessingResult(
                success=False,
                result=None,
                confidence=0.0,
                processing_time=0.0,
                metadata={'error': 'Agent not initialized'},
                errors=['Agent not initialized']
            )
        
        start_time = time.time()
        self.total_processing_count += 1
        
        try:
            # Validate input
            validation_result = await self._validate_input(input_data)
            if not validation_result['valid']:
                return ProcessingResult(
                    success=False,
                    result=None,
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    metadata={'validation_errors': validation_result['errors']},
                    errors=validation_result['errors']
                )
            
            # Pre-processing hooks
            processed_input = await self._pre_process_input(input_data)
            
            # Main processing
            result = await asyncio.wait_for(
                self._process_internal(processed_input),
                timeout=self.config.timeout_seconds
            )
            
            # Post-processing hooks
            final_result = await self._post_process_result(result)
            
            # Update success metrics
            if final_result.success:
                self.success_count += 1
            else:
                self.error_count += 1
            
            self.last_processing_time = time.time() - start_time
            
            # Add metadata
            final_result.metadata.update({
                'agent_name': self.name,
                'processing_timestamp': datetime.utcnow().isoformat(),
                'total_processing_count': self.total_processing_count,
                'success_rate': self.success_count / self.total_processing_count
            })
            
            self.logger.info(
                f"Agent {self.name} processed successfully in {final_result.processing_time:.2f}s"
            )
            
            return final_result
            
        except asyncio.TimeoutError:
            self.error_count += 1
            self.logger.error(f"Agent {self.name} timed out after {self.config.timeout_seconds}s")
            
            return ProcessingResult(
                success=False,
                result=None,
                confidence=0.0,
                processing_time=time.time() - start_time,
                metadata={'error': 'Processing timeout'},
                errors=[f'Processing timeout after {self.config.timeout_seconds}s']
            )
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Agent {self.name} processing failed: {str(e)}")
            
            return ProcessingResult(
                success=False,
                result=None,
                confidence=0.0,
                processing_time=time.time() - start_time,
                metadata={'error': str(e)},
                errors=[str(e)]
            )
    
    async def _validate_input(self, input_data: Any) -> Dict[str, Any]:
        """
        Validate input data format and content.
        Override in subclasses for specific validation logic.
        """
        
        if input_data is None:
            return {'valid': False, 'errors': ['Input data is None']}
        
        return {'valid': True, 'errors': []}
    
    async def _pre_process_input(self, input_data: Any) -> Any:
        """
        Pre-process input data before main processing.
        Override in subclasses for specific pre-processing logic.
        """
        return input_data
    
    async def _post_process_result(self, result: ProcessingResult) -> ProcessingResult:
        """
        Post-process result after main processing.
        Override in subclasses for specific post-processing logic.
        """
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics."""
        
        return {
            'name': self.name,
            'initialized': self.is_initialized,
            'total_processed': self.total_processing_count,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'success_rate': self.success_count / self.total_processing_count if self.total_processing_count > 0 else 0,
            'last_processing_time': self.last_processing_time,
            'config': {
                'timeout_seconds': self.config.timeout_seconds,
                'confidence_threshold': self.config.confidence_threshold
            }
        }
    
    def get_health_check(self) -> Dict[str, Any]:
        """Perform health check on the agent."""
        
        health_status = {
            'healthy': True,
            'status': 'operational',
            'checks': []
        }
        
        # Check initialization
        if not self.is_initialized:
            health_status['healthy'] = False
            health_status['status'] = 'not_initialized'
            health_status['checks'].append({
                'check': 'initialization',
                'passed': False,
                'message': 'Agent not properly initialized'
            })
        else:
            health_status['checks'].append({
                'check': 'initialization',
                'passed': True,
                'message': 'Agent initialized successfully'
            })
        
        # Check success rate
        success_rate = self.success_count / self.total_processing_count if self.total_processing_count > 0 else 1.0
        success_rate_healthy = success_rate >= 0.8
        
        health_status['checks'].append({
            'check': 'success_rate',
            'passed': success_rate_healthy,
            'message': f'Success rate: {success_rate:.2%}',
            'value': success_rate
        })
        
        if not success_rate_healthy:
            health_status['healthy'] = False
            if health_status['status'] == 'operational':
                health_status['status'] = 'degraded'
        
        return health_status
    
    async def handle_system_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Handle system-wide events.
        Override in subclasses for specific event handling.
        """
        
        self.logger.info(f"Agent {self.name} received system event: {event_type}")
        
        if event_type == 'shutdown':
            await self._cleanup()
        elif event_type == 'configuration_update':
            await self._update_configuration(event_data)
    
    async def _cleanup(self):
        """Cleanup resources when shutting down."""
        self.logger.info(f"Agent {self.name} cleaning up resources")
    
    async def _update_configuration(self, new_config: Dict[str, Any]):
        """Update agent configuration."""
        self.logger.info(f"Agent {self.name} updating configuration")
        
        # Update basic config
        if 'timeout_seconds' in new_config:
            self.config.timeout_seconds = new_config['timeout_seconds']
        
        if 'confidence_threshold' in new_config:
            self.config.confidence_threshold = new_config['confidence_threshold']
    
    def __str__(self) -> str:
        return f"Agent({self.name})"
    
    def __repr__(self) -> str:
        return f"Agent(name='{self.name}', initialized={self.is_initialized})"