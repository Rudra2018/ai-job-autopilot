#!/usr/bin/env python3
"""
Enhanced PDF-to-Text Extraction Module
Multi-method PDF text extraction with fallback mechanisms for maximum accuracy
"""

import os
import io
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import json

# PDF processing libraries
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from pdf2image import convert_from_path
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False

try:
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

@dataclass
class ExtractionResult:
    """Results from PDF text extraction"""
    text: str
    method: str
    confidence: float
    pages: int
    metadata: Dict
    errors: List[str]
    processing_time: float

@dataclass
class ExtractionConfig:
    """Configuration for PDF extraction"""
    prefer_method: str = "auto"  # auto, pypdf2, pdfplumber, pymupdf, ocr
    use_ocr_fallback: bool = True
    ocr_languages: List[str] = None
    clean_text: bool = True
    preserve_formatting: bool = False
    extract_images: bool = False
    max_pages: Optional[int] = None
    
    def __post_init__(self):
        if self.ocr_languages is None:
            self.ocr_languages = ['eng']

class EnhancedPDFExtractor:
    """Enhanced PDF text extraction with multiple methods and fallbacks"""
    
    def __init__(self, config: Optional[ExtractionConfig] = None):
        self.config = config or ExtractionConfig()
        self.logger = logging.getLogger(__name__)
        
        # Check available extraction methods
        self.available_methods = self._check_available_methods()
        self.logger.info(f"Available extraction methods: {list(self.available_methods.keys())}")
    
    def _check_available_methods(self) -> Dict[str, bool]:
        """Check which PDF extraction methods are available"""
        return {
            'pypdf2': HAS_PYPDF2,
            'pdfplumber': HAS_PDFPLUMBER,
            'pymupdf': HAS_PYMUPDF,
            'ocr': HAS_OCR and HAS_PDF2IMAGE
        }
    
    def extract_text(self, pdf_path: Union[str, Path]) -> ExtractionResult:
        """Extract text from PDF using the best available method"""
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        import time
        start_time = time.time()
        
        # Determine extraction method
        if self.config.prefer_method == "auto":
            method = self._select_best_method(pdf_path)
        else:
            method = self.config.prefer_method
        
        # Try extraction with primary method
        try:
            result = self._extract_with_method(pdf_path, method)
            result.processing_time = time.time() - start_time
            
            # If text is too short or seems corrupted, try fallback
            if self._needs_fallback(result):
                fallback_result = self._try_fallback_methods(pdf_path, method)
                if fallback_result and len(fallback_result.text) > len(result.text):
                    result = fallback_result
                    result.processing_time = time.time() - start_time
            
            # Clean and post-process text if requested
            if self.config.clean_text:
                result.text = self._clean_text(result.text)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Primary extraction method '{method}' failed: {e}")
            return self._try_fallback_methods(pdf_path, exclude_method=method)
    
    def _select_best_method(self, pdf_path: Path) -> str:
        """Select the best extraction method based on PDF characteristics"""
        
        # Quick file size and complexity check
        file_size = pdf_path.stat().st_size / (1024 * 1024)  # MB
        
        # For small, simple PDFs, try PyPDF2 first (fastest)
        if file_size < 5 and self.available_methods['pypdf2']:
            return 'pypdf2'
        
        # For medium PDFs, prefer pdfplumber (better formatting)
        if file_size < 20 and self.available_methods['pdfplumber']:
            return 'pdfplumber'
        
        # For larger or complex PDFs, use PyMuPDF
        if self.available_methods['pymupdf']:
            return 'pymupdf'
        
        # Fallback order
        for method in ['pdfplumber', 'pypdf2', 'ocr']:
            if self.available_methods.get(method, False):
                return method
        
        raise RuntimeError("No PDF extraction methods available")
    
    def _extract_with_method(self, pdf_path: Path, method: str) -> ExtractionResult:
        """Extract text using specified method"""
        
        if method == 'pypdf2':
            return self._extract_with_pypdf2(pdf_path)
        elif method == 'pdfplumber':
            return self._extract_with_pdfplumber(pdf_path)
        elif method == 'pymupdf':
            return self._extract_with_pymupdf(pdf_path)
        elif method == 'ocr':
            return self._extract_with_ocr(pdf_path)
        else:
            raise ValueError(f"Unknown extraction method: {method}")
    
    def _extract_with_pypdf2(self, pdf_path: Path) -> ExtractionResult:
        """Extract text using PyPDF2"""
        if not HAS_PYPDF2:
            raise RuntimeError("PyPDF2 not available")
        
        text_parts = []
        pages = 0
        errors = []
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                pages = len(reader.pages)
                
                max_pages = self.config.max_pages or pages
                for i, page in enumerate(reader.pages[:max_pages]):
                    try:
                        text_parts.append(page.extract_text())
                    except Exception as e:
                        errors.append(f"Page {i+1}: {str(e)}")
                
                metadata = {
                    'total_pages': pages,
                    'extracted_pages': min(max_pages, pages),
                    'pdf_metadata': reader.metadata if hasattr(reader, 'metadata') else {}
                }
                
                text = '\n\n'.join(text_parts)
                confidence = self._calculate_confidence(text, 'pypdf2')
                
                return ExtractionResult(
                    text=text,
                    method='pypdf2',
                    confidence=confidence,
                    pages=pages,
                    metadata=metadata,
                    errors=errors,
                    processing_time=0
                )
        
        except Exception as e:
            raise RuntimeError(f"PyPDF2 extraction failed: {e}")
    
    def _extract_with_pdfplumber(self, pdf_path: Path) -> ExtractionResult:
        """Extract text using pdfplumber"""
        if not HAS_PDFPLUMBER:
            raise RuntimeError("pdfplumber not available")
        
        text_parts = []
        errors = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                pages = len(pdf.pages)
                max_pages = self.config.max_pages or pages
                
                for i, page in enumerate(pdf.pages[:max_pages]):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    except Exception as e:
                        errors.append(f"Page {i+1}: {str(e)}")
                
                metadata = {
                    'total_pages': pages,
                    'extracted_pages': min(max_pages, pages),
                    'pdf_metadata': pdf.metadata
                }
                
                text = '\n\n'.join(text_parts)
                confidence = self._calculate_confidence(text, 'pdfplumber')
                
                return ExtractionResult(
                    text=text,
                    method='pdfplumber',
                    confidence=confidence,
                    pages=pages,
                    metadata=metadata,
                    errors=errors,
                    processing_time=0
                )
        
        except Exception as e:
            raise RuntimeError(f"pdfplumber extraction failed: {e}")
    
    def _extract_with_pymupdf(self, pdf_path: Path) -> ExtractionResult:
        """Extract text using PyMuPDF"""
        if not HAS_PYMUPDF:
            raise RuntimeError("PyMuPDF not available")
        
        text_parts = []
        errors = []
        
        try:
            doc = fitz.open(pdf_path)
            pages = doc.page_count
            max_pages = self.config.max_pages or pages
            
            for i in range(min(max_pages, pages)):
                try:
                    page = doc.load_page(i)
                    text = page.get_text()
                    if text.strip():
                        text_parts.append(text)
                except Exception as e:
                    errors.append(f"Page {i+1}: {str(e)}")
            
            metadata = {
                'total_pages': pages,
                'extracted_pages': min(max_pages, pages),
                'pdf_metadata': doc.metadata
            }
            
            text = '\n\n'.join(text_parts)
            confidence = self._calculate_confidence(text, 'pymupdf')
            
            doc.close()
            
            return ExtractionResult(
                text=text,
                method='pymupdf',
                confidence=confidence,
                pages=pages,
                metadata=metadata,
                errors=errors,
                processing_time=0
            )
        
        except Exception as e:
            raise RuntimeError(f"PyMuPDF extraction failed: {e}")
    
    def _extract_with_ocr(self, pdf_path: Path) -> ExtractionResult:
        """Extract text using OCR (Tesseract)"""
        if not HAS_OCR or not HAS_PDF2IMAGE:
            raise RuntimeError("OCR dependencies not available")
        
        text_parts = []
        errors = []
        
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            pages = len(images)
            max_pages = self.config.max_pages or pages
            
            # Configure OCR
            ocr_config = '--oem 3 --psm 6'  # Use LSTM OCR Engine with uniform text block
            
            for i, image in enumerate(images[:max_pages]):
                try:
                    # Extract text using OCR
                    text = pytesseract.image_to_string(
                        image, 
                        lang='+'.join(self.config.ocr_languages),
                        config=ocr_config
                    )
                    if text.strip():
                        text_parts.append(text)
                except Exception as e:
                    errors.append(f"Page {i+1}: {str(e)}")
            
            metadata = {
                'total_pages': pages,
                'extracted_pages': min(max_pages, pages),
                'ocr_languages': self.config.ocr_languages,
                'ocr_config': ocr_config
            }
            
            text = '\n\n'.join(text_parts)
            confidence = self._calculate_confidence(text, 'ocr')
            
            return ExtractionResult(
                text=text,
                method='ocr',
                confidence=confidence,
                pages=pages,
                metadata=metadata,
                errors=errors,
                processing_time=0
            )
        
        except Exception as e:
            raise RuntimeError(f"OCR extraction failed: {e}")
    
    def _needs_fallback(self, result: ExtractionResult) -> bool:
        """Determine if fallback extraction is needed"""
        text = result.text.strip()
        
        # Too little text extracted
        if len(text) < 50:
            return True
        
        # Low confidence score
        if result.confidence < 0.5:
            return True
        
        # High error rate
        if len(result.errors) > result.pages * 0.3:
            return True
        
        # Text seems corrupted (too many special characters)
        special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text)
        if special_char_ratio > 0.3:
            return True
        
        return False
    
    def _try_fallback_methods(self, pdf_path: Path, exclude_method: str = None) -> Optional[ExtractionResult]:
        """Try fallback extraction methods"""
        fallback_order = ['pdfplumber', 'pymupdf', 'pypdf2', 'ocr']
        
        # Remove excluded method
        if exclude_method:
            fallback_order = [m for m in fallback_order if m != exclude_method]
        
        for method in fallback_order:
            if not self.available_methods.get(method, False):
                continue
                
            try:
                self.logger.info(f"Trying fallback method: {method}")
                result = self._extract_with_method(pdf_path, method)
                if len(result.text.strip()) > 50:  # Minimum viable text
                    return result
            except Exception as e:
                self.logger.warning(f"Fallback method '{method}' failed: {e}")
                continue
        
        return None
    
    def _calculate_confidence(self, text: str, method: str) -> float:
        """Calculate confidence score for extracted text"""
        if not text.strip():
            return 0.0
        
        confidence = 0.0
        text_length = len(text)
        
        # Base confidence by method
        method_confidence = {
            'pdfplumber': 0.9,
            'pymupdf': 0.85,
            'pypdf2': 0.8,
            'ocr': 0.7
        }
        confidence += method_confidence.get(method, 0.5)
        
        # Adjust for text characteristics
        if text_length > 100:
            confidence += 0.1
        if text_length > 500:
            confidence += 0.1
        
        # Check for common resume keywords
        resume_keywords = [
            'experience', 'education', 'skills', 'work', 'university',
            'degree', 'phone', 'email', 'address', 'linkedin'
        ]
        keyword_matches = sum(1 for keyword in resume_keywords if keyword.lower() in text.lower())
        confidence += min(keyword_matches * 0.05, 0.2)
        
        # Penalize if mostly special characters
        special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / text_length
        if special_char_ratio > 0.2:
            confidence -= (special_char_ratio - 0.2) * 2
        
        return min(max(confidence, 0.0), 1.0)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        import re
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common PDF artifacts
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
        
        # Fix common OCR mistakes for resumes
        text = re.sub(r'\bEducat10n\b', 'Education', text, flags=re.IGNORECASE)
        text = re.sub(r'\bExper1ence\b', 'Experience', text, flags=re.IGNORECASE)
        text = re.sub(r'\bSk111s\b', 'Skills', text, flags=re.IGNORECASE)
        text = re.sub(r'\b0f\b', 'of', text)
        
        # Normalize email and phone patterns
        text = re.sub(r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', r'\1@\2', text)
        
        return text.strip()
    
    def extract_multiple(self, pdf_paths: List[Union[str, Path]]) -> List[ExtractionResult]:
        """Extract text from multiple PDF files"""
        results = []
        
        for pdf_path in pdf_paths:
            try:
                result = self.extract_text(pdf_path)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to extract text from {pdf_path}: {e}")
                # Create error result
                error_result = ExtractionResult(
                    text="",
                    method="error",
                    confidence=0.0,
                    pages=0,
                    metadata={},
                    errors=[str(e)],
                    processing_time=0.0
                )
                results.append(error_result)
        
        return results

# Convenience function for quick extraction
def extract_pdf_text(pdf_path: Union[str, Path], config: Optional[ExtractionConfig] = None) -> str:
    """Quick function to extract text from a PDF file"""
    extractor = EnhancedPDFExtractor(config)
    result = extractor.extract_text(pdf_path)
    return result.text

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
        
        config = ExtractionConfig(
            clean_text=True,
            use_ocr_fallback=True
        )
        
        extractor = EnhancedPDFExtractor(config)
        result = extractor.extract_text(pdf_file)
        
        print(f"Extraction Method: {result.method}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Pages: {result.pages}")
        print(f"Processing Time: {result.processing_time:.2f}s")
        print(f"Errors: {len(result.errors)}")
        print("\n--- Extracted Text ---")
        print(result.text[:1000] + "..." if len(result.text) > 1000 else result.text)
    else:
        print("Usage: python pdf_text_extractor.py <pdf_file>")