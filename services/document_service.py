"""
Servicio de Extracción de Documentos - Extrae atributos de PDF y DOCX
"""

import os
import re
from typing import Dict, Tuple
import openai
from .llm_service import LLMExtractionService
import pdfplumber
from docx import Document


class DocumentExtractionService:
    """Servicio para extraer atributos de documentos PDF y DOCX"""
    
    # Patrones regex configurables para extracción de atributos
    ATTRIBUTE_PATTERNS = {
        'empaquetado': [
            r'[Ee]mpaquetad[oa]\s*[:\-\,]\s*(.+?)(?:\n|$)',
            r'[Pp]ackaging\s*[:\-\,]\s*(.+?)(?:\n|$)',
        ],
        'ingredientes': [
            r'[Ii]ngrediente[s]?\s*[:\-\,]\s*(.+?)(?:\n|$)',
            r'[Ii]ngredients?\s*[:\-\,]\s*(.+?)(?:\n|$)',
        ],
        'peso': [
            r'[Pp]eso\s*[:\-\,]\s*([0-9.,]+\s*kg)',
            r'[Ww]eight\s*[:\-\,]\s*([0-9.,]+\s*kg)',
        ],
        'fecha_vencimiento': [
            r'[Cc]aducidad\s*[:\-\,]\s*([0-9]{4}-[0-9]{2}-[0-9]{2})',
            r'[Vv]encimiento\s*[:\-\,]\s*([0-9]{4}-[0-9]{2}-[0-9]{2})',
            r'[Ee]xpiration\s*[:\-\,]\s*([0-9]{4}-[0-9]{2}-[0-9]{2})',
        ],
        'registro_fda': [
            r'[Rr]egistro\s+FDA\s*[:\-\,]\s*(sí|yes|no)',
            r'FDA\s+[Rr]egistration\s*[:\-\,]\s*(sí|yes|no)',
        ],
        'etiquetado_ingles': [
            r'[Ee]tiquetado\s+en\s+inglés\s*[:\-\,]\s*(sí|yes|no)',
            r'[Ee]nglish\s+[Ll]abeling\s*[:\-\,]\s*(sí|yes|no)',
        ],
        'pais_origen': [
            r'[Pp]aís\s+de\s+origen\s*[:\-\,]\s*(.+?)(?:\n|$)',
            r'[Cc]ountry\s+of\s+origin\s*[:\-\,]\s*(.+?)(?:\n|$)',
        ],
        'certificaciones': [
            r'[Cc]ertificación\s*[:\-\,]\s*(.+?)(?:\n|$)',
            r'[Cc]ertification\s*[:\-\,]\s*(.+?)(?:\n|$)',
        ],
    }
    
    @staticmethod
    def extract_from_pdf(file_path: str) -> str:
        """Extraer texto de archivo PDF"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error extrayendo PDF: {e}")
        
        return text
    
    @staticmethod
    def extract_from_docx(file_path: str) -> str:
        """Extraer texto de archivo DOCX"""
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                if paragraph.text:
                    text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error extrayendo DOCX: {e}")
        
        return text
    
    def extract_attributes(self, file_path: str) -> Tuple[Dict[str, str], str]:

        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if ext == '.pdf':
            text = self.extract_from_pdf(file_path)

        elif ext == '.docx':
            text = self.extract_from_docx(file_path)

        else:
            return {}, 'regex'

        try:
            llm = LLMExtractionService()

            attributes = llm.extract_attributes(text)

            if attributes and len(attributes) > 0:
                return attributes, 'llm'

        except openai.RateLimitError as e:
            print(f"OpenAI: cuota o rate limit agotado, usando regex: {e}")
        except (openai.APIConnectionError, openai.AuthenticationError) as e:
            print(f"OpenAI: error de conexión/autenticación, usando regex: {e}")
        except Exception as e:
            print(f"Error usando LLM, usando regex: {e}")

        # Fallback a regex
        attributes = {}

        for attribute_key, patterns in self.ATTRIBUTE_PATTERNS.items():
            for pattern in patterns:

                match = re.search(
                    pattern,
                    text,
                    re.IGNORECASE | re.MULTILINE
                )

                if match:

                    value = match.group(1).strip()

                    if value:
                        attributes[attribute_key] = value
                        break

        return attributes, 'regex'
    
    def extract_with_confidence(self, file_path: str) -> Dict:
        """
        Extraer atributos con información de confianza

        Retorna diccionario con atributos y nivel de confianza
        """
        attributes, source = self.extract_attributes(file_path)

        result = {
            'attributes': attributes,
            'extracted_count': len(attributes),
            'extraction_source': source,
            'timestamp': __import__('datetime').datetime.utcnow().isoformat(),
            'file_path': file_path
        }

        return result
