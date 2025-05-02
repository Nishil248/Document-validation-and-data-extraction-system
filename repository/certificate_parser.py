import json
import re
import google.generativeai as genai
import easyocr
import numpy as np
from pdfminer.high_level import extract_text as pdf_extract_text
from pdfminer.layout import LAParams
import os
import tempfile

class CertificateParser:
    def __init__(self, file_input, gemini_api_key=None):
        """
        Initialize the parser with either a numpy image array or PDF file path
        
        Args:
            file_input: Can be either a numpy image array or a path/bytes of a PDF file
            gemini_api_key: Google Gemini API key (optional if already configured)
        """
        self.input = file_input
        # Initialize EasyOCR reader
        self.reader = easyocr.Reader(['en'])
        
        # Configure Gemini
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    def extract_text(self):
        """Extract text from either image or PDF input"""
        try:
            # Check if input is a PDF (bytes or filepath)
            if isinstance(self.input, bytes) and self.input[:4] == b'%PDF':
                return self._extract_from_pdf_bytes(self.input)
            elif isinstance(self.input, str) and self.input.lower().endswith('.pdf'):
                return self._extract_from_pdf_file(self.input)
            # Otherwise treat as image
            else:
                return self._extract_from_image()
        except Exception as e:
            return f"Error extracting text: {e}"
    
    def _extract_from_image(self):
        """Extract text from image using EasyOCR"""
        results = self.reader.readtext(self.input)
        text = ' '.join([result[1] for result in results])
        return text.strip()
    
    def _extract_from_pdf_file(self, pdf_path):
        """Extract text from PDF file path using pdfminer"""
        try:
            text = pdf_extract_text(
                pdf_path,
                laparams=LAParams(line_margin=0.5)
            )
            return text.strip()
        except Exception as e:
            # Fallback: Convert PDF to images and process with EasyOCR
            return self._pdf_ocr_fallback(pdf_path)
    
    def _extract_from_pdf_bytes(self, pdf_bytes):
        """Extract text from PDF bytes using pdfminer"""
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(pdf_bytes)
                temp_path = temp_file.name
            
            # Extract text from the temporary file
            text = self._extract_from_pdf_file(temp_path)
            
            # Clean up
            os.unlink(temp_path)
            
            return text
        except Exception as e:
            return f"Error extracting text from PDF bytes: {e}"
    
    def _pdf_ocr_fallback(self, pdf_path):
        """Fallback method to convert PDF to images and use OCR"""
        try:
            from pdf2image import convert_from_path
            
            # Convert PDF pages to images
            images = convert_from_path(pdf_path)
            
            # Extract text from each page
            all_text = []
            for img in images:
                # Convert PIL Image to numpy array
                np_image = np.array(img)
                # Extract text using EasyOCR
                results = self.reader.readtext(np_image)
                page_text = ' '.join([result[1] for result in results])
                all_text.append(page_text)
            
            return ' '.join(all_text).strip()
        except Exception as e:
            return f"Error in PDF OCR fallback: {e}"
    
    def extract_details(self, text):
        try:
            prompt = f"""
            Extract the following details from the given internship certificate text:
            1. **Company Name**: Extract Full name of the organization that issued the certificate. Ignore references to other companies.
            2. **Person's Name**: The individual who completed the internship. Extract the name without any title (e.g., "Mr.", "Ms.", "Dr.", etc.).
            3. **Internship Domain**: The field or role in which the person interned.
            4. **Internship Duration**: Include only start and end dates in the format "Day Month, Year" (e.g., "start": 20th March, 2023, "end": 16th April, 2023").
            
            Return the output in JSON format with the keys: "Company", "Name", "Domain", and "Duration" without any additional text.
            
            Text:
            {text}
            """
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0,
                    "max_output_tokens": 1000
                },
                safety_settings={
                    "HARASSMENT": "BLOCK_NONE",
                    "HATE_SPEECH": "BLOCK_NONE",
                    "SEXUAL": "BLOCK_NONE",
                    "DANGEROUS": "BLOCK_NONE"
                }
            )
            
            if not response or not response.text:
                return {"Error": "No response received from Gemini."}
            
            result_text = response.text.strip()
            
            # Remove Markdown-style code blocks if present
            result_text = re.sub(r'^```json\n?|\n?```$', '', result_text, flags=re.MULTILINE).strip()
            
            try:
                return json.loads(result_text)
            except json.JSONDecodeError:
                # Handle common JSON format issues
                cleaned_text = self._clean_json_text(result_text)
                try:
                    return json.loads(cleaned_text)
                except:
                    return {"Error": "Invalid JSON format received from Gemini.", "Raw Response": result_text}
        except Exception as e:
            return {"Error": f"Unexpected error: {e}"}
    
    def _clean_json_text(self, text):
        """Attempt to fix common JSON formatting issues"""
        # Find content between curly braces
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            text = json_match.group(0)
        
        # Ensure property names are quoted
        text = re.sub(r'(\s*)(\w+)(\s*):(\s*)', r'\1"\2"\3:\4', text)
        
        # Fix single quotes to double quotes
        text = text.replace("'", '"')
        
        return text