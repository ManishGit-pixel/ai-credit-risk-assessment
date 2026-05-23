"""
KYC (Know Your Customer) Document Verification Service
Handles ID document upload and OCR extraction
"""

from PIL import Image
import pytesseract
import re
from datetime import datetime
from pathlib import Path
import os
from utils.logger import get_logger
from config import settings

logger = get_logger(__name__)

class KYCService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
    
    async def save_document(self, file_content: bytes, user_id: str, filename: str) -> str:
        """
        Save uploaded document to disk
        """
        try:
            # Create user-specific directory
            user_dir = self.upload_dir / user_id
            user_dir.mkdir(exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = Path(filename).suffix
            new_filename = f"id_document_{timestamp}{file_extension}"
            file_path = user_dir / new_filename
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            logger.info(f"Saved document for user {user_id}: {new_filename}")
            return str(file_path)
        
        except Exception as e:
            logger.error(f"Error saving document: {e}")
            raise Exception(f"Failed to save document: {str(e)}")
    
    async def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from image using OCR (Tesseract)
        """
        try:
            image = Image.open(image_path)
            
            # Preprocess image for better OCR
            # Convert to grayscale
            image = image.convert('L')
            
            # Extract text
            text = pytesseract.image_to_string(image)
            
            logger.info(f"Extracted text from image: {image_path}")
            return text
        
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            raise Exception(f"OCR failed: {str(e)}")
    
    def extract_name_from_text(self, text: str) -> str:
        """
        Extract name from OCR text
        Uses pattern matching for common ID formats
        """
        # Common patterns for names on IDs
        patterns = [
            r'Name[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'FULL NAME[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'([A-Z][A-Z]+,\s*[A-Z][A-Z]+)',  # LASTNAME, FIRSTNAME
            r'Name:\s*([^\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up the name
                name = re.sub(r'\s+', ' ', name)
                return name
        
        return ""
    
    def extract_dob_from_text(self, text: str) -> str:
        """
        Extract date of birth from OCR text
        """
        # Common date patterns
        patterns = [
            r'DOB[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Date of Birth[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Birth Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                dob = match.group(1)
                return dob
        
        return ""
    
    async def verify_document(self, image_path: str, expected_name: str = None, expected_dob: str = None) -> dict:
        """
        Verify ID document by extracting and matching information
        """
        try:
            # Extract text from image
            text = await self.extract_text_from_image(image_path)
            
            # Extract information
            extracted_name = self.extract_name_from_text(text)
            extracted_dob = self.extract_dob_from_text(text)
            
            # Verify matches
            name_match = False
            dob_match = False
            
            if expected_name and extracted_name:
                # Fuzzy match (case-insensitive, ignore extra spaces)
                name_match = self._fuzzy_match(expected_name, extracted_name)
            
            if expected_dob and extracted_dob:
                dob_match = self._fuzzy_match(expected_dob, extracted_dob)
            
            verification_status = "verified" if (name_match or dob_match) else "needs_review"
            
            return {
                "status": verification_status,
                "extracted_name": extracted_name,
                "extracted_dob": extracted_dob,
                "name_match": name_match,
                "dob_match": dob_match,
                "raw_text": text[:500],  # First 500 chars for debugging
                "confidence": 0.85 if (name_match or dob_match) else 0.3
            }
        
        except Exception as e:
            logger.error(f"Error verifying document: {e}")
            return {
                "status": "error",
                "error": str(e),
                "confidence": 0.0
            }
    
    def _fuzzy_match(self, str1: str, str2: str, threshold: float = 0.7) -> bool:
        """
        Simple fuzzy string matching
        """
        str1 = str1.lower().strip()
        str2 = str2.lower().strip()
        
        # Exact match
        if str1 == str2:
            return True
        
        # Check if one contains the other
        if str1 in str2 or str2 in str1:
            return True
        
        # Simple similarity check
        common_chars = sum(1 for c in str1 if c in str2)
        similarity = common_chars / max(len(str1), len(str2))
        
        return similarity >= threshold

# Singleton instance
kyc_service = KYCService()
