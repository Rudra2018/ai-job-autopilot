#!/usr/bin/env python3
"""
Resume Processing Pipeline
Unified pipeline that coordinates PDF extraction -> Resume parsing -> AI enhancement
for maximum accuracy and reliability
"""

import logging
import time
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum

# Import our pipeline components
from src.core.pdf_text_extractor import EnhancedPDFExtractor, ExtractionConfig, ExtractionResult
from src.core.enhanced_resume_parser import EnhancedResumeParser, ParsedResume
from src.ml.ai_resume_enhancer import AIResumeEnhancer, EnhancedResumeData, JobMatchScore

class ProcessingStage(Enum):
    """Pipeline processing stages"""
    INITIALIZATION = "initialization"
    PDF_EXTRACTION = "pdf_extraction"
    TEXT_PARSING = "text_parsing"
    AI_ENHANCEMENT = "ai_enhancement"
    JOB_MATCHING = "job_matching"
    VALIDATION = "validation"
    COMPLETION = "completion"

class ProcessingStatus(Enum):
    """Processing status codes"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class StageResult:
    """Result of a processing stage"""
    stage: ProcessingStage
    status: ProcessingStatus
    start_time: float = 0.0
    end_time: float = 0.0
    processing_time: float = 0.0
    success: bool = False
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PipelineConfig:
    """Configuration for the resume processing pipeline"""
    # PDF extraction settings
    pdf_extraction_method: str = "auto"
    use_ocr_fallback: bool = True
    ocr_languages: List[str] = field(default_factory=lambda: ['eng'])
    clean_extracted_text: bool = True
    max_pages: Optional[int] = None
    
    # Resume parsing settings
    enable_ai_enhancement: bool = True
    openai_api_key: Optional[str] = None
    
    # Job matching settings
    enable_job_matching: bool = False
    target_job_description: Optional[str] = None
    
    # Output settings
    save_intermediate_results: bool = False
    output_format: str = "json"  # json, yaml, pickle
    include_raw_text: bool = False
    
    # Performance settings
    timeout_seconds: int = 300
    retry_attempts: int = 2
    parallel_processing: bool = False
    
    # Quality assurance
    min_confidence_threshold: float = 0.3
    enable_validation: bool = True

@dataclass
class PipelineResult:
    """Complete result of resume processing pipeline"""
    # Input information
    input_file: str = ""
    processing_id: str = ""
    
    # Stage results
    stage_results: Dict[str, StageResult] = field(default_factory=dict)
    
    # Core results
    extraction_result: Optional[ExtractionResult] = None
    parsed_resume: Optional[ParsedResume] = None
    enhanced_data: Optional[EnhancedResumeData] = None
    job_match_score: Optional[JobMatchScore] = None
    
    # Overall metrics
    total_processing_time: float = 0.0
    overall_success: bool = False
    confidence_score: float = 0.0
    
    # Quality metrics
    quality_score: float = 0.0
    completeness_score: float = 0.0
    accuracy_indicators: Dict[str, Any] = field(default_factory=dict)
    
    # Errors and warnings
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Metadata
    pipeline_version: str = "1.0"
    processing_timestamp: str = ""
    config_used: Optional[PipelineConfig] = None

class ResumeProcessingPipeline:
    """Unified resume processing pipeline orchestrator"""
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize pipeline components
        self._initialize_components()
        
        # Processing state
        self.current_stage = ProcessingStage.INITIALIZATION
        self.processing_id = None
        
    def _initialize_components(self):
        """Initialize all pipeline components"""
        try:
            # PDF Extractor
            extraction_config = ExtractionConfig(
                prefer_method=self.config.pdf_extraction_method,
                use_ocr_fallback=self.config.use_ocr_fallback,
                ocr_languages=self.config.ocr_languages,
                clean_text=self.config.clean_extracted_text,
                max_pages=self.config.max_pages
            )
            self.pdf_extractor = EnhancedPDFExtractor(extraction_config)
            
            # Resume Parser
            self.resume_parser = EnhancedResumeParser()
            
            # AI Enhancer (if enabled)
            if self.config.enable_ai_enhancement:
                self.ai_enhancer = AIResumeEnhancer(self.config.openai_api_key)
            else:
                self.ai_enhancer = None
                
            self.logger.info("Pipeline components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize pipeline components: {e}")
            raise
    
    def process_resume(self, file_path: Union[str, Path]) -> PipelineResult:
        """Process a resume through the complete pipeline"""
        start_time = time.time()
        processing_id = f"resume_{int(start_time)}"
        self.processing_id = processing_id
        
        result = PipelineResult(
            input_file=str(file_path),
            processing_id=processing_id,
            processing_timestamp=datetime.now().isoformat(),
            config_used=self.config
        )
        
        self.logger.info(f"Starting resume processing pipeline for: {file_path}")
        
        try:
            # Stage 1: PDF Text Extraction
            extraction_stage = self._execute_stage(
                ProcessingStage.PDF_EXTRACTION,
                self._extract_pdf_text,
                file_path
            )
            result.stage_results[ProcessingStage.PDF_EXTRACTION.value] = extraction_stage
            
            if not extraction_stage.success:
                result.overall_success = False
                result.errors.append("PDF extraction failed")
                return self._finalize_result(result, start_time)
            
            result.extraction_result = extraction_stage.metadata.get('result')
            
            # Stage 2: Resume Text Parsing
            parsing_stage = self._execute_stage(
                ProcessingStage.TEXT_PARSING,
                self._parse_resume_text,
                result.extraction_result.text
            )
            result.stage_results[ProcessingStage.TEXT_PARSING.value] = parsing_stage
            
            if not parsing_stage.success:
                result.overall_success = False
                result.errors.append("Resume parsing failed")
                return self._finalize_result(result, start_time)
            
            result.parsed_resume = parsing_stage.metadata.get('result')
            
            # Stage 3: AI Enhancement (optional)
            if self.config.enable_ai_enhancement and self.ai_enhancer:
                enhancement_stage = self._execute_stage(
                    ProcessingStage.AI_ENHANCEMENT,
                    self._enhance_resume,
                    result.parsed_resume
                )
                result.stage_results[ProcessingStage.AI_ENHANCEMENT.value] = enhancement_stage
                
                if enhancement_stage.success:
                    result.enhanced_data = enhancement_stage.metadata.get('result')
                else:
                    result.warnings.append("AI enhancement failed, proceeding without enhancement")
            
            # Stage 4: Job Matching (optional)
            if self.config.enable_job_matching and self.config.target_job_description:
                matching_stage = self._execute_stage(
                    ProcessingStage.JOB_MATCHING,
                    self._calculate_job_match,
                    (result.parsed_resume, self.config.target_job_description)
                )
                result.stage_results[ProcessingStage.JOB_MATCHING.value] = matching_stage
                
                if matching_stage.success:
                    result.job_match_score = matching_stage.metadata.get('result')
            
            # Stage 5: Validation
            if self.config.enable_validation:
                validation_stage = self._execute_stage(
                    ProcessingStage.VALIDATION,
                    self._validate_results,
                    result
                )
                result.stage_results[ProcessingStage.VALIDATION.value] = validation_stage
                
                if not validation_stage.success:
                    result.warnings.extend(validation_stage.warnings)
            
            # Calculate overall success and metrics
            result.overall_success = self._calculate_overall_success(result)
            result.confidence_score = self._calculate_confidence_score(result)
            result.quality_score = self._calculate_quality_score(result)
            result.completeness_score = self._calculate_completeness_score(result)
            
            self.logger.info(f"Pipeline completed successfully. Confidence: {result.confidence_score:.2f}")
            
        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {e}")
            result.overall_success = False
            result.errors.append(f"Pipeline execution error: {str(e)}")
        
        return self._finalize_result(result, start_time)
    
    def _execute_stage(self, stage: ProcessingStage, func, *args) -> StageResult:
        """Execute a pipeline stage with error handling and timing"""
        stage_result = StageResult(stage=stage, status=ProcessingStatus.IN_PROGRESS)
        stage_result.start_time = time.time()
        self.current_stage = stage
        
        self.logger.debug(f"Executing stage: {stage.value}")
        
        try:
            result = func(*args)
            stage_result.success = True
            stage_result.status = ProcessingStatus.COMPLETED
            stage_result.metadata['result'] = result
            
        except Exception as e:
            self.logger.error(f"Stage {stage.value} failed: {e}")
            stage_result.success = False
            stage_result.status = ProcessingStatus.FAILED
            stage_result.error = str(e)
        
        stage_result.end_time = time.time()
        stage_result.processing_time = stage_result.end_time - stage_result.start_time
        
        return stage_result
    
    def _extract_pdf_text(self, file_path: Union[str, Path]) -> ExtractionResult:
        """Extract text from PDF file"""
        return self.pdf_extractor.extract_text(file_path)
    
    def _parse_resume_text(self, text: str) -> ParsedResume:
        """Parse resume text into structured data"""
        return self.resume_parser.parse_text(text)
    
    def _enhance_resume(self, parsed_resume: ParsedResume) -> EnhancedResumeData:
        """Enhance resume with AI analysis"""
        return self.ai_enhancer.enhance_resume(
            parsed_resume, 
            self.config.target_job_description
        )
    
    def _calculate_job_match(self, data: Tuple[ParsedResume, str]) -> JobMatchScore:
        """Calculate job match score"""
        parsed_resume, job_description = data
        return self.ai_enhancer.calculate_job_match(parsed_resume, job_description)
    
    def _validate_results(self, result: PipelineResult) -> bool:
        """Validate pipeline results"""
        warnings = []
        
        # Check extraction quality
        if result.extraction_result:
            if result.extraction_result.confidence < 0.5:
                warnings.append("Low PDF extraction confidence")
            
            if len(result.extraction_result.text) < 100:
                warnings.append("Very little text extracted from PDF")
        
        # Check parsing quality
        if result.parsed_resume:
            if result.parsed_resume.parsing_confidence < self.config.min_confidence_threshold:
                warnings.append(f"Parsing confidence below threshold: {result.parsed_resume.parsing_confidence:.2f}")
            
            if not result.parsed_resume.contact_info.email:
                warnings.append("No email found in resume")
            
            if not result.parsed_resume.work_experience:
                warnings.append("No work experience found")
        
        # Store warnings in stage result
        validation_result = StageResult(
            stage=ProcessingStage.VALIDATION,
            status=ProcessingStatus.COMPLETED,
            success=len(warnings) == 0,
            warnings=warnings
        )
        
        return len(warnings) == 0
    
    def _calculate_overall_success(self, result: PipelineResult) -> bool:
        """Calculate overall pipeline success"""
        critical_stages = [ProcessingStage.PDF_EXTRACTION, ProcessingStage.TEXT_PARSING]
        
        for stage in critical_stages:
            stage_result = result.stage_results.get(stage.value)
            if not stage_result or not stage_result.success:
                return False
        
        return True
    
    def _calculate_confidence_score(self, result: PipelineResult) -> float:
        """Calculate overall confidence score"""
        confidence = 0.0
        
        if result.extraction_result:
            confidence += result.extraction_result.confidence * 0.3
        
        if result.parsed_resume:
            confidence += result.parsed_resume.parsing_confidence * 0.4
        
        if result.enhanced_data:
            confidence += result.enhanced_data.analysis.overall_score * 0.3
        else:
            confidence += 0.2  # Base score if no AI enhancement
        
        return min(confidence, 1.0)
    
    def _calculate_quality_score(self, result: PipelineResult) -> float:
        """Calculate result quality score"""
        if not result.parsed_resume:
            return 0.0
        
        quality = 0.0
        
        # Contact information completeness
        contact = result.parsed_resume.contact_info
        contact_fields = [contact.name, contact.email, contact.phone]
        contact_score = sum(1 for field in contact_fields if field) / len(contact_fields)
        quality += contact_score * 0.2
        
        # Content richness
        if result.parsed_resume.work_experience:
            quality += 0.3
        if result.parsed_resume.education:
            quality += 0.2
        if result.parsed_resume.skills:
            quality += 0.2
        if result.parsed_resume.summary:
            quality += 0.1
        
        return quality
    
    def _calculate_completeness_score(self, result: PipelineResult) -> float:
        """Calculate data completeness score"""
        if not result.parsed_resume:
            return 0.0
        
        sections_found = len(result.parsed_resume.sections_found)
        total_sections = 7  # Expected number of main resume sections
        
        return min(sections_found / total_sections, 1.0)
    
    def _finalize_result(self, result: PipelineResult, start_time: float) -> PipelineResult:
        """Finalize pipeline result"""
        result.total_processing_time = time.time() - start_time
        
        # Clean up result if requested
        if not self.config.include_raw_text and result.parsed_resume:
            result.parsed_resume.raw_text = ""
        
        self.logger.info(f"Pipeline completed in {result.total_processing_time:.2f}s")
        
        return result
    
    def process_multiple_resumes(self, file_paths: List[Union[str, Path]]) -> List[PipelineResult]:
        """Process multiple resumes"""
        results = []
        
        for file_path in file_paths:
            try:
                result = self.process_resume(file_path)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to process {file_path}: {e}")
                # Create error result
                error_result = PipelineResult(
                    input_file=str(file_path),
                    overall_success=False,
                    errors=[str(e)],
                    processing_timestamp=datetime.now().isoformat()
                )
                results.append(error_result)
        
        return results
    
    async def process_resume_async(self, file_path: Union[str, Path]) -> PipelineResult:
        """Asynchronous resume processing"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process_resume, file_path)
    
    def export_result(self, result: PipelineResult, output_path: Optional[Union[str, Path]] = None) -> str:
        """Export pipeline result to file"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"resume_analysis_{timestamp}.json"
        
        output_path = Path(output_path)
        
        # Convert result to serializable format
        result_dict = asdict(result)
        
        # Handle non-serializable objects
        if result_dict.get('extraction_result'):
            if hasattr(result.extraction_result, '__dict__'):
                result_dict['extraction_result'] = asdict(result.extraction_result)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, indent=2, default=str)
        
        self.logger.info(f"Results exported to: {output_path}")
        return str(output_path)
    
    def get_performance_metrics(self, results: List[PipelineResult]) -> Dict[str, Any]:
        """Calculate performance metrics for multiple results"""
        if not results:
            return {}
        
        metrics = {
            "total_processed": len(results),
            "successful": sum(1 for r in results if r.overall_success),
            "failed": sum(1 for r in results if not r.overall_success),
            "average_processing_time": sum(r.total_processing_time for r in results) / len(results),
            "average_confidence": sum(r.confidence_score for r in results) / len(results),
            "average_quality": sum(r.quality_score for r in results) / len(results),
            "success_rate": sum(1 for r in results if r.overall_success) / len(results)
        }
        
        return metrics

# Convenience functions for direct usage
def process_resume_complete(
    pdf_path: Union[str, Path],
    config: Optional[PipelineConfig] = None
) -> PipelineResult:
    """Complete resume processing with default configuration"""
    pipeline = ResumeProcessingPipeline(config)
    return pipeline.process_resume(pdf_path)

def process_resume_for_job(
    pdf_path: Union[str, Path],
    job_description: str,
    openai_api_key: Optional[str] = None
) -> PipelineResult:
    """Process resume with job matching"""
    config = PipelineConfig(
        enable_ai_enhancement=True,
        enable_job_matching=True,
        target_job_description=job_description,
        openai_api_key=openai_api_key
    )
    
    pipeline = ResumeProcessingPipeline(config)
    return pipeline.process_resume(pdf_path)

def batch_process_resumes(
    pdf_paths: List[Union[str, Path]],
    config: Optional[PipelineConfig] = None
) -> List[PipelineResult]:
    """Batch process multiple resumes"""
    pipeline = ResumeProcessingPipeline(config)
    return pipeline.process_multiple_resumes(pdf_paths)

if __name__ == "__main__":
    # Example usage and CLI interface
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Resume Processing Pipeline")
    parser.add_argument("resume_file", help="Path to resume PDF file")
    parser.add_argument("--job-description", help="Job description for matching")
    parser.add_argument("--openai-key", help="OpenAI API key for AI features")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create configuration
    config = PipelineConfig()
    if args.openai_key:
        config.openai_api_key = args.openai_key
        config.enable_ai_enhancement = True
    
    if args.job_description:
        config.enable_job_matching = True
        config.target_job_description = args.job_description
    
    # Process resume
    try:
        pipeline = ResumeProcessingPipeline(config)
        result = pipeline.process_resume(args.resume_file)
        
        # Display summary
        print(f"\n{'='*60}")
        print(f"RESUME PROCESSING RESULTS")
        print(f"{'='*60}")
        print(f"File: {result.input_file}")
        print(f"Success: {result.overall_success}")
        print(f"Processing Time: {result.total_processing_time:.2f}s")
        print(f"Confidence Score: {result.confidence_score:.2f}")
        print(f"Quality Score: {result.quality_score:.2f}")
        
        if result.parsed_resume:
            print(f"\nExtracted Information:")
            print(f"• Name: {result.parsed_resume.contact_info.name}")
            print(f"• Email: {result.parsed_resume.contact_info.email}")
            print(f"• Skills: {len(result.parsed_resume.skills)} found")
            print(f"• Experience: {len(result.parsed_resume.work_experience)} positions")
            print(f"• Education: {len(result.parsed_resume.education)} entries")
        
        if result.enhanced_data:
            print(f"\nAI Analysis:")
            print(f"• Overall Score: {result.enhanced_data.analysis.overall_score:.2f}")
            print(f"• Experience Level: {result.enhanced_data.analysis.estimated_experience_level}")
            print(f"• ATS Compatibility: {result.enhanced_data.analysis.ats_compatibility:.2f}")
        
        if result.job_match_score:
            print(f"\nJob Match Analysis:")
            print(f"• Overall Match: {result.job_match_score.overall_match:.2f}")
            print(f"• Skill Match: {result.job_match_score.skill_match:.2f}")
            print(f"• Matched Skills: {len(result.job_match_score.matched_skills)}")
            print(f"• Missing Skills: {len(result.job_match_score.missing_skills)}")
        
        if result.errors:
            print(f"\nErrors:")
            for error in result.errors:
                print(f"• {error}")
        
        if result.warnings:
            print(f"\nWarnings:")
            for warning in result.warnings:
                print(f"• {warning}")
        
        # Export results if requested
        if args.output:
            pipeline.export_result(result, args.output)
            print(f"\nResults exported to: {args.output}")
            
    except Exception as e:
        print(f"Pipeline execution failed: {e}")
        sys.exit(1)