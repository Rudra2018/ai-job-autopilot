"""
OCR Agent Implementation
Handles text extraction from images and PDFs using multiple OCR engines.
"""

import asyncio
import base64
import io
import json
import os
import tempfile
from typing import Any, Dict, List, Optional
from PIL import Image
import pdf2image

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    from google.cloud import vision
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False

from .base_agent import BaseAgent, ProcessingResult

class OCRAgent(BaseAgent):
    """
    OCR Agent responsible for extracting text from visual sources using multiple OCR engines.
    Implements intelligent fallback strategies and quality assessment.
    """
    
    def _setup_agent_specific_config(self):
        """Setup OCR-specific configurations."""
        
        self.available_engines = []
        self.engine_priorities = ['google_vision', 'easyocr', 'tesseract', 'paddleocr']
        
        # Check available OCR engines
        if GOOGLE_VISION_AVAILABLE and os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            self.available_engines.append('google_vision')
            self.vision_client = vision.ImageAnnotatorClient()
        
        if EASYOCR_AVAILABLE:
            self.available_engines.append('easyocr')
            self.easyocr_reader = easyocr.Reader(['en'])
        
        if TESSERACT_AVAILABLE:
            self.available_engines.append('tesseract')
        
        self.logger.info(f"Available OCR engines: {self.available_engines}")
        
        if not self.available_engines:
            raise RuntimeError("No OCR engines available. Please install at least one OCR library.")
    
    async def _validate_input(self, input_data: Any) -> Dict[str, Any]:
        """Validate OCR input data."""
        
        if not isinstance(input_data, dict):
            return {'valid': False, 'errors': ['Input must be a dictionary']}
        
        if 'documents' not in input_data:
            return {'valid': False, 'errors': ['Missing documents field']}
        
        documents = input_data['documents']
        if not isinstance(documents, list) or not documents:
            return {'valid': False, 'errors': ['Documents must be a non-empty list']}
        
        # Validate each document
        for i, doc in enumerate(documents):
            if not isinstance(doc, dict):
                return {'valid': False, 'errors': [f'Document {i} must be a dictionary']}
            
            if 'file_path' not in doc and 'file_data' not in doc:
                return {'valid': False, 'errors': [f'Document {i} must have file_path or file_data']}
            
            if 'file_format' not in doc:
                return {'valid': False, 'errors': [f'Document {i} must specify file_format']}
            
            if doc['file_format'] not in ['pdf', 'jpg', 'jpeg', 'png', 'tiff', 'bmp']:
                return {'valid': False, 'errors': [f'Document {i} has unsupported format: {doc["file_format"]}']}
        
        return {'valid': True, 'errors': []}
    
    async def _process_internal(self, input_data: Dict[str, Any]) -> ProcessingResult:
        """Process documents through OCR engines."""
        
        documents = input_data['documents']
        processing_options = input_data.get('processing_options', {})
        
        results = {
            'extraction_id': f"ocr_{int(time.time())}",
            'documents_processed': 0,
            'successful_extractions': 0,
            'extracted_documents': [],
            'engine_performance': {},
            'overall_confidence': 0.0
        }
        
        total_confidence = 0.0
        
        for doc_index, document in enumerate(documents):
            try:
                # Extract text from document
                doc_result = await self._extract_from_document(document, processing_options)
                
                results['extracted_documents'].append(doc_result)
                results['documents_processed'] += 1
                
                if doc_result['success']:
                    results['successful_extractions'] += 1
                    total_confidence += doc_result['confidence']
                
            except Exception as e:
                self.logger.error(f"Failed to process document {doc_index}: {str(e)}")
                
                error_result = {
                    'document_id': document.get('document_id', f'doc_{doc_index}'),
                    'success': False,
                    'confidence': 0.0,
                    'extracted_text': '',
                    'error': str(e),
                    'engine_used': None
                }
                
                results['extracted_documents'].append(error_result)
                results['documents_processed'] += 1
        
        # Calculate overall confidence
        if results['successful_extractions'] > 0:
            results['overall_confidence'] = total_confidence / results['successful_extractions']
        
        # Combine all extracted text
        combined_text = '\n\n'.join([
            doc['extracted_text'] for doc in results['extracted_documents']
            if doc['success'] and doc['extracted_text']
        ])
        
        results['combined_extracted_text'] = combined_text
        results['total_characters'] = len(combined_text)
        
        success = results['successful_extractions'] > 0
        confidence = results['overall_confidence']
        
        return ProcessingResult(
            success=success,
            result=results,
            confidence=confidence,
            processing_time=0.0,  # Will be set by base class
            metadata={
                'documents_processed': results['documents_processed'],
                'successful_extractions': results['successful_extractions'],
                'engines_used': list(results['engine_performance'].keys())
            }
        )
    
    async def _extract_from_document(self, document: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text from a single document using multiple OCR engines."""
        
        document_id = document.get('document_id', 'unknown')
        file_format = document['file_format'].lower()
        
        # Get image data
        if 'file_path' in document:
            image_data = await self._load_image_from_path(document['file_path'], file_format)
        else:
            image_data = await self._load_image_from_data(document['file_data'], file_format)
        
        if not image_data:
            raise ValueError("Could not load image data")
        
        # Try OCR engines in priority order
        preferred_engines = options.get('engines', self.engine_priorities)
        fallback_enabled = options.get('fallback_enabled', True)
        
        last_error = None
        
        for engine in preferred_engines:
            if engine not in self.available_engines:
                continue
            
            try:
                result = await self._extract_with_engine(engine, image_data)
                
                # Return successful result
                return {
                    'document_id': document_id,
                    'success': True,
                    'confidence': result['confidence'],
                    'extracted_text': result['text'],
                    'engine_used': engine,
                    'processing_time': result['processing_time'],
                    'metadata': result.get('metadata', {})
                }
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"OCR engine {engine} failed for document {document_id}: {str(e)}")
                
                if not fallback_enabled:
                    break
        
        # All engines failed
        raise Exception(f"All OCR engines failed. Last error: {last_error}")
    
    async def _load_image_from_path(self, file_path: str, file_format: str) -> Optional[bytes]:
        """Load image data from file path."""
        
        try:
            if file_format == 'pdf':
                # Convert PDF to images
                images = pdf2image.convert_from_path(file_path)
                if not images:
                    return None
                
                # Use first page for now (could be extended to handle multiple pages)
                image = images[0]
                
                # Convert to bytes
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                return img_byte_arr.getvalue()
            
            else:
                # Load image file
                with open(file_path, 'rb') as f:
                    return f.read()
        
        except Exception as e:
            self.logger.error(f"Failed to load image from {file_path}: {str(e)}")
            return None
    
    async def _load_image_from_data(self, file_data: str, file_format: str) -> Optional[bytes]:
        """Load image data from base64 encoded string."""
        
        try:
            # Decode base64 data
            image_bytes = base64.b64decode(file_data)
            
            if file_format == 'pdf':
                # Save to temp file and convert
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                    temp_file.write(image_bytes)
                    temp_path = temp_file.name
                
                try:
                    images = pdf2image.convert_from_path(temp_path)
                    if not images:
                        return None
                    
                    # Convert first page to bytes
                    image = images[0]
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    return img_byte_arr.getvalue()
                
                finally:
                    os.unlink(temp_path)
            
            else:
                return image_bytes
        
        except Exception as e:
            self.logger.error(f"Failed to load image from data: {str(e)}")
            return None
    
    async def _extract_with_engine(self, engine: str, image_data: bytes) -> Dict[str, Any]:
        """Extract text using a specific OCR engine."""
        
        if engine == 'google_vision':
            return await self._extract_with_google_vision(image_data)
        elif engine == 'tesseract':
            return await self._extract_with_tesseract(image_data)
        elif engine == 'easyocr':
            return await self._extract_with_easyocr(image_data)
        else:
            raise ValueError(f"Unsupported OCR engine: {engine}")
    
    async def _extract_with_google_vision(self, image_data: bytes) -> Dict[str, Any]:
        """Extract text using Google Vision OCR."""
        
        import time
        start_time = time.time()
        
        image = vision.Image(content=image_data)
        response = self.vision_client.document_text_detection(image=image)
        
        if response.error.message:
            raise Exception(f"Google Vision error: {response.error.message}")
        
        # Extract text and confidence
        texts = response.text_annotations
        if texts:
            extracted_text = texts[0].description
            confidence = 0.9  # Google Vision doesn't provide confidence scores directly
        else:
            extracted_text = ""
            confidence = 0.0
        
        processing_time = time.time() - start_time
        
        return {
            'text': extracted_text,
            'confidence': confidence,
            'processing_time': processing_time,
            'metadata': {
                'engine': 'google_vision',
                'character_count': len(extracted_text)
            }
        }
    
    async def _extract_with_tesseract(self, image_data: bytes) -> Dict[str, Any]:
        """Extract text using Tesseract OCR."""
        
        import time
        start_time = time.time()
        
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # Extract text
        extracted_text = pytesseract.image_to_string(image)
        
        # Get confidence data
        try:
            confidence_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in confidence_data['conf'] if int(conf) > 0]
            confidence = sum(confidences) / len(confidences) / 100 if confidences else 0.0
        except:
            confidence = 0.7  # Default confidence for Tesseract
        
        processing_time = time.time() - start_time
        
        return {
            'text': extracted_text.strip(),
            'confidence': confidence,
            'processing_time': processing_time,
            'metadata': {
                'engine': 'tesseract',
                'character_count': len(extracted_text)
            }
        }
    
    async def _extract_with_easyocr(self, image_data: bytes) -> Dict[str, Any]:
        """Extract text using EasyOCR."""
        
        import time
        start_time = time.time()
        
        # EasyOCR expects image as numpy array
        import numpy as np
        from PIL import Image
        
        image = Image.open(io.BytesIO(image_data))
        image_np = np.array(image)
        
        # Extract text
        results = self.easyocr_reader.readtext(image_np, detail=1)
        
        # Combine text and calculate confidence
        extracted_text = ""
        total_confidence = 0.0
        
        for (bbox, text, conf) in results:
            extracted_text += text + " "
            total_confidence += conf
        
        extracted_text = extracted_text.strip()
        confidence = total_confidence / len(results) if results else 0.0
        
        processing_time = time.time() - start_time
        
        return {
            'text': extracted_text,
            'confidence': confidence,
            'processing_time': processing_time,
            'metadata': {
                'engine': 'easyocr',
                'character_count': len(extracted_text),
                'text_blocks_found': len(results)
            }
        }