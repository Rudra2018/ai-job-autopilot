"""
📖 OCRAgent: Multi-engine text extraction with intelligent ensemble processing
Handles accurate text extraction from images and scanned PDFs using a multi-engine ensemble.
"""

import asyncio
import base64
import io
import json
import os
import tempfile
import logging
import time
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import pdf2image
import numpy as np
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
from datetime import datetime
import concurrent.futures
from difflib import SequenceMatcher

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

try:
    import paddleocr
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False

from .base_agent import BaseAgent, ProcessingResult

class OCRAgent(BaseAgent):
    """
    📖 OCRAgent: Multi-engine text extraction with intelligent ensemble processing
    
    Goals:
    1. Accept image, PDF, or screenshot input
    2. Use Google Vision, Tesseract, EasyOCR, and PaddleOCR in ensemble mode
    3. Run engines in parallel and cross-check outputs
    4. Clean and normalize extracted text with confidence scoring
    5. Handle multilingual text with layout preservation
    6. Implement intelligent fallback strategies
    """
    
    def _setup_agent_specific_config(self):
        """Setup OCR-specific configurations with multi-engine ensemble."""
        
        # Engine availability and initialization
        self.available_engines = []
        self.engine_priorities = ['google_vision', 'paddleocr', 'easyocr', 'tesseract']
        self.engines_initialized = {}
        
        # Text cleaning and normalization settings
        self.confidence_threshold = 0.6
        self.consensus_threshold = 0.7  # Agreement required between engines
        self.multilingual_support = True
        self.layout_preservation = True
        
        # Image preprocessing settings
        self.image_enhancement = {
            'contrast_factor': 1.2,
            'sharpness_factor': 1.1,
            'brightness_factor': 1.0,
            'denoise': True,
            'deskew': True
        }
        
        # Initialize available OCR engines
        self._initialize_ocr_engines()
        
        self.logger.info(f"📖 OCRAgent initialized with {len(self.available_engines)} engines: {self.available_engines}")
    
    def _initialize_ocr_engines(self):
        """Initialize all available OCR engines."""
        
        # Google Vision API
        if GOOGLE_VISION_AVAILABLE and os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            try:
                self.google_client = vision.ImageAnnotatorClient()
                self.available_engines.append('google_vision')
                self.engines_initialized['google_vision'] = True
                self.logger.info("✅ Google Vision API initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Google Vision API failed to initialize: {e}")
        
        # PaddleOCR
        if PADDLEOCR_AVAILABLE:
            try:
                # Initialize with English and common languages
                self.paddle_ocr = paddleocr.PaddleOCR(
                    use_angle_cls=True, 
                    lang='en',
                    show_log=False,
                    use_gpu=False  # Set to True if GPU available
                )
                self.available_engines.append('paddleocr')
                self.engines_initialized['paddleocr'] = True
                self.logger.info("✅ PaddleOCR initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ PaddleOCR failed to initialize: {e}")
        
        # EasyOCR
        if EASYOCR_AVAILABLE:
            try:
                self.easy_reader = easyocr.Reader(['en'], gpu=False)  # Add more languages as needed
                self.available_engines.append('easyocr')
                self.engines_initialized['easyocr'] = True
                self.logger.info("✅ EasyOCR initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ EasyOCR failed to initialize: {e}")
        
        # Tesseract
        if TESSERACT_AVAILABLE:
            try:
                # Test Tesseract availability
                pytesseract.get_tesseract_version()
                self.available_engines.append('tesseract')
                self.engines_initialized['tesseract'] = True
                self.logger.info("✅ Tesseract initialized")
            except Exception as e:
                self.logger.warning(f"⚠️ Tesseract failed to initialize: {e}")
        
        if not self.available_engines:
            raise RuntimeError("No OCR engines available. Please install at least one OCR engine.")
    
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
        """Process documents through OCR engines with ensemble processing."""
        
        documents = input_data['documents']
        processing_options = input_data.get('processing_options', {})
        
        results = {
            'extraction_id': f"ocr_{int(time.time())}",
            'documents_processed': 0,
            'successful_extractions': 0,
            'extracted_documents': [],
            'engine_performance': {},
            'overall_confidence': 0.0,
            'extraction_metadata': {
                'engines_used': self.available_engines.copy(),
                'processing_timestamp': datetime.utcnow().isoformat(),
                'consensus_threshold': self.consensus_threshold
            }
        }
        
        total_confidence = 0.0
        
        for doc_index, document in enumerate(documents):
            try:
                self.logger.info(f"📄 Processing document {doc_index + 1}/{len(documents)}")
                
                # Load and preprocess document
                images = await self._load_document(document)
                if not images:
                    continue
                
                document_result = {
                    'document_id': document.get('document_id', f'doc_{doc_index}'),
                    'document_type': document.get('document_type', 'resume'),
                    'file_format': document['file_format'],
                    'pages': [],
                    'consolidated_text': '',
                    'confidence': 0.0,
                    'engine_results': {}
                }
                
                # Process each page/image
                for page_index, image in enumerate(images):
                    page_result = await self._process_image_ensemble(image, page_index)
                    document_result['pages'].append(page_result)
                
                # Consolidate results across pages
                await self._consolidate_document_results(document_result)
                
                results['extracted_documents'].append(document_result)
                results['documents_processed'] += 1
                
                if document_result['confidence'] >= self.confidence_threshold:
                    results['successful_extractions'] += 1
                
                total_confidence += document_result['confidence']
                
            except Exception as e:
                self.logger.error(f"Failed to process document {doc_index}: {str(e)}")
                results['extraction_metadata']['errors'] = results['extraction_metadata'].get('errors', [])
                results['extraction_metadata']['errors'].append(f"Document {doc_index}: {str(e)}")
        
        # Calculate overall confidence
        if results['documents_processed'] > 0:
            results['overall_confidence'] = total_confidence / results['documents_processed']
        
        # Update engine performance statistics
        results['engine_performance'] = self._calculate_engine_performance(results['extracted_documents'])
        
        return ProcessingResult(
            success=results['successful_extractions'] > 0,
            result={
                'extracted_text': self._get_consolidated_text(results['extracted_documents']),
                'documents': results['extracted_documents'],
                'metadata': results['extraction_metadata']
            },
            confidence=results['overall_confidence'],
            processing_time=0.0,
            metadata={
                'documents_processed': results['documents_processed'],
                'successful_extractions': results['successful_extractions'],
                'engines_used': len(self.available_engines)
            }
        )
    
    async def _load_document(self, document: Dict[str, Any]) -> List[Image.Image]:
        """Load and convert document to images for processing."""
        
        images = []
        
        try:
            if 'file_path' in document:
                file_path = Path(document['file_path'])
                if not file_path.exists():
                    self.logger.error(f"File not found: {file_path}")
                    return images
                
                if document['file_format'].lower() == 'pdf':
                    # Convert PDF to images
                    pdf_images = pdf2image.convert_from_path(file_path, dpi=300)
                    images.extend(pdf_images)
                else:
                    # Load image directly
                    image = Image.open(file_path)
                    images.append(image)
            
            elif 'file_data' in document:
                # Handle base64 encoded data
                if isinstance(document['file_data'], str):
                    # Assume base64 encoded
                    image_data = base64.b64decode(document['file_data'])
                    image = Image.open(io.BytesIO(image_data))
                    images.append(image)
                else:
                    # Handle binary data
                    image = Image.open(io.BytesIO(document['file_data']))
                    images.append(image)
        
        except Exception as e:
            self.logger.error(f"Failed to load document: {str(e)}")
            return []
        
        # Preprocess images
        processed_images = []
        for image in images:
            processed_image = await self._preprocess_image(image)
            processed_images.append(processed_image)
        
        return processed_images
    
    async def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR accuracy."""
        
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Apply image enhancements
            if self.image_enhancement['contrast_factor'] != 1.0:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(self.image_enhancement['contrast_factor'])
            
            if self.image_enhancement['sharpness_factor'] != 1.0:
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(self.image_enhancement['sharpness_factor'])
            
            if self.image_enhancement['brightness_factor'] != 1.0:
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(self.image_enhancement['brightness_factor'])
            
            # Denoise if enabled
            if self.image_enhancement['denoise']:
                image = image.filter(ImageFilter.MedianFilter(size=3))
            
            return image
        
        except Exception as e:
            self.logger.warning(f"Image preprocessing failed: {str(e)}")
            return image
    
    async def _process_image_ensemble(self, image: Image.Image, page_index: int) -> Dict[str, Any]:
        """Process single image through all available OCR engines in parallel."""
        
        page_result = {
            'page_number': page_index + 1,
            'engine_results': {},
            'consensus_text': '',
            'confidence': 0.0,
            'text_blocks': [],
            'layout_info': {}
        }
        
        # Run OCR engines in parallel
        engine_tasks = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.available_engines)) as executor:
            for engine in self.available_engines:
                future = executor.submit(self._run_single_engine, engine, image)
                engine_tasks.append((engine, future))
            
            # Collect results
            for engine, future in engine_tasks:
                try:
                    result = future.result(timeout=60)  # 60 second timeout per engine
                    page_result['engine_results'][engine] = result
                except Exception as e:
                    self.logger.warning(f"Engine {engine} failed: {str(e)}")
                    page_result['engine_results'][engine] = {
                        'text': '',
                        'confidence': 0.0,
                        'blocks': [],
                        'error': str(e)
                    }
        
        # Create consensus from multiple engine results
        await self._create_consensus(page_result)
        
        return page_result
    
    def _run_single_engine(self, engine: str, image: Image.Image) -> Dict[str, Any]:
        """Run single OCR engine on image."""
        
        result = {
            'text': '',
            'confidence': 0.0,
            'blocks': [],
            'processing_time': 0.0
        }
        
        start_time = time.time()
        
        try:
            if engine == 'google_vision':
                result = self._run_google_vision(image)
            elif engine == 'paddleocr':
                result = self._run_paddleocr(image)
            elif engine == 'easyocr':
                result = self._run_easyocr(image)
            elif engine == 'tesseract':
                result = self._run_tesseract(image)
            
            result['processing_time'] = time.time() - start_time
            
        except Exception as e:
            self.logger.error(f"Engine {engine} processing failed: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    def _run_google_vision(self, image: Image.Image) -> Dict[str, Any]:
        """Run Google Vision OCR."""
        
        # Convert PIL image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Create Vision API image object
        vision_image = vision.Image(content=img_byte_arr)
        
        # Perform text detection
        response = self.google_client.text_detection(image=vision_image)
        texts = response.text_annotations
        
        if response.error.message:
            raise Exception(f"Google Vision API error: {response.error.message}")
        
        if not texts:
            return {'text': '', 'confidence': 0.0, 'blocks': []}
        
        # Extract full text and confidence
        full_text = texts[0].description if texts else ''
        
        # Extract individual text blocks
        blocks = []
        for text in texts[1:]:  # Skip first element which is the full text
            vertices = [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices]
            blocks.append({
                'text': text.description,
                'confidence': 0.9,  # Google Vision doesn't provide per-text confidence
                'bbox': vertices
            })
        
        # Calculate overall confidence (Google Vision is generally high quality)
        confidence = 0.9 if full_text.strip() else 0.0
        
        return {
            'text': full_text,
            'confidence': confidence,
            'blocks': blocks
        }
    
    def _run_paddleocr(self, image: Image.Image) -> Dict[str, Any]:
        """Run PaddleOCR."""
        
        # Convert PIL image to numpy array
        img_array = np.array(image)
        
        # Run OCR
        results = self.paddle_ocr.ocr(img_array, cls=True)
        
        if not results or not results[0]:
            return {'text': '', 'confidence': 0.0, 'blocks': []}
        
        full_text_parts = []
        blocks = []
        confidences = []
        
        for line in results[0]:
            bbox = line[0]
            text_info = line[1]
            text = text_info[0]
            confidence = text_info[1]
            
            full_text_parts.append(text)
            blocks.append({
                'text': text,
                'confidence': confidence,
                'bbox': bbox
            })
            confidences.append(confidence)
        
        full_text = '\n'.join(full_text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            'text': full_text,
            'confidence': avg_confidence,
            'blocks': blocks
        }
    
    def _run_easyocr(self, image: Image.Image) -> Dict[str, Any]:
        """Run EasyOCR."""
        
        # Convert PIL image to numpy array
        img_array = np.array(image)
        
        # Run OCR
        results = self.easy_reader.readtext(img_array)
        
        if not results:
            return {'text': '', 'confidence': 0.0, 'blocks': []}
        
        full_text_parts = []
        blocks = []
        confidences = []
        
        for (bbox, text, confidence) in results:
            full_text_parts.append(text)
            blocks.append({
                'text': text,
                'confidence': confidence,
                'bbox': bbox
            })
            confidences.append(confidence)
        
        full_text = '\n'.join(full_text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            'text': full_text,
            'confidence': avg_confidence,
            'blocks': blocks
        }
    
    def _run_tesseract(self, image: Image.Image) -> Dict[str, Any]:
        """Run Tesseract OCR."""
        
        # Configure Tesseract for better accuracy
        config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?@#$%^&*()_+-=[]{}|;:,.<>? '
        
        # Extract text
        text = pytesseract.image_to_string(image, config=config)
        
        # Get detailed data for confidence and blocks
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, config=config)
        
        blocks = []
        confidences = []
        
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 0:  # Filter out low confidence detections
                confidence = int(data['conf'][i]) / 100.0
                confidences.append(confidence)
                
                if data['text'][i].strip():  # Only add non-empty text
                    blocks.append({
                        'text': data['text'][i],
                        'confidence': confidence,
                        'bbox': [
                            (data['left'][i], data['top'][i]),
                            (data['left'][i] + data['width'][i], data['top'][i]),
                            (data['left'][i] + data['width'][i], data['top'][i] + data['height'][i]),
                            (data['left'][i], data['top'][i] + data['height'][i])
                        ]
                    })
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            'text': text,
            'confidence': avg_confidence,
            'blocks': blocks
        }
    
    async def _create_consensus(self, page_result: Dict[str, Any]):
        """Create consensus text from multiple engine results."""
        
        engine_results = page_result['engine_results']
        
        if not engine_results:
            page_result['consensus_text'] = ''
            page_result['confidence'] = 0.0
            return
        
        # Get texts from all engines
        texts = []
        confidences = []
        
        for engine, result in engine_results.items():
            if result['text'].strip() and 'error' not in result:
                texts.append(result['text'].strip())
                confidences.append(result['confidence'])
        
        if not texts:
            page_result['consensus_text'] = ''
            page_result['confidence'] = 0.0
            return
        
        # If only one engine succeeded, use its result
        if len(texts) == 1:
            page_result['consensus_text'] = texts[0]
            page_result['confidence'] = confidences[0]
            return
        
        # Find best consensus text using similarity matching
        best_text = ''
        best_confidence = 0.0
        
        for i, text1 in enumerate(texts):
            similarity_sum = 0.0
            confidence_weight = confidences[i]
            
            for j, text2 in enumerate(texts):
                if i != j:
                    similarity = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
                    similarity_sum += similarity
            
            # Calculate consensus score
            avg_similarity = similarity_sum / (len(texts) - 1) if len(texts) > 1 else 0.0
            consensus_score = (confidence_weight + avg_similarity) / 2.0
            
            if consensus_score > best_confidence:
                best_confidence = consensus_score
                best_text = text1
        
        page_result['consensus_text'] = best_text
        page_result['confidence'] = best_confidence
    
    async def _consolidate_document_results(self, document_result: Dict[str, Any]):
        """Consolidate results across all pages of a document."""
        
        pages = document_result['pages']
        
        if not pages:
            document_result['consolidated_text'] = ''
            document_result['confidence'] = 0.0
            return
        
        # Combine text from all pages
        page_texts = []
        page_confidences = []
        
        for page in pages:
            if page['consensus_text'].strip():
                page_texts.append(page['consensus_text'].strip())
                page_confidences.append(page['confidence'])
        
        # Create consolidated text
        document_result['consolidated_text'] = '\n\n'.join(page_texts)
        
        # Calculate overall document confidence
        if page_confidences:
            document_result['confidence'] = sum(page_confidences) / len(page_confidences)
        else:
            document_result['confidence'] = 0.0
    
    def _calculate_engine_performance(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance statistics for each engine."""
        
        engine_stats = {}
        
        for engine in self.available_engines:
            engine_stats[engine] = {
                'total_pages': 0,
                'successful_pages': 0,
                'avg_confidence': 0.0,
                'avg_processing_time': 0.0,
                'success_rate': 0.0
            }
        
        # Collect statistics
        for document in documents:
            for page in document['pages']:
                for engine, result in page['engine_results'].items():
                    stats = engine_stats[engine]
                    stats['total_pages'] += 1
                    
                    if 'error' not in result and result['confidence'] > 0:
                        stats['successful_pages'] += 1
                        stats['avg_confidence'] += result['confidence']
                        stats['avg_processing_time'] += result.get('processing_time', 0.0)
        
        # Calculate averages
        for engine, stats in engine_stats.items():
            if stats['successful_pages'] > 0:
                stats['avg_confidence'] /= stats['successful_pages']
                stats['avg_processing_time'] /= stats['successful_pages']
                stats['success_rate'] = stats['successful_pages'] / stats['total_pages']
            else:
                stats['avg_confidence'] = 0.0
                stats['avg_processing_time'] = 0.0
                stats['success_rate'] = 0.0
        
        return engine_stats
    
    def _get_consolidated_text(self, documents: List[Dict[str, Any]]) -> str:
        """Get all extracted text consolidated into a single string."""
        
        all_text = []
        
        for document in documents:
            if document['consolidated_text'].strip():
                all_text.append(document['consolidated_text'].strip())
        
        return '\n\n--- DOCUMENT SEPARATOR ---\n\n'.join(all_text)