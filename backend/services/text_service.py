"""
Text Processing Service - Entity Extraction and Relationship Analysis
Handles police reports and documents
"""
import re
from pathlib import Path
from typing import Dict, Any, List
import PyPDF2
from docx import Document
from config import MODEL_CONFIG
from utils.logger import setup_logger
from utils.model_loader import load_llm_model

logger = setup_logger('text_service')

class TextService:
    """Service for text processing and entity extraction"""
    
    def __init__(self):
        self.llm = None
    
    def _ensure_model_loaded(self):
        """Ensure LLM model is loaded"""
        if self.llm is None:
            result = load_llm_model()
            if result:
                self.llm = result
    
    def extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text from various file formats
        
        Args:
            file_path: Path to file
        
        Returns:
            Extracted text
        """
        try:
            path = Path(file_path)
            ext = path.suffix.lower()
            
            if ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif ext == '.pdf':
                text = []
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text.append(page.extract_text())
                return '\n'.join(text)
            
            elif ext in ['.doc', '.docx']:
                doc = Document(file_path)
                return '\n'.join([para.text for para in doc.paragraphs])
            
            else:
                logger.warning(f"Unsupported file format: {ext}")
                return ""
        
        except Exception as e:
            logger.error(f"Error extracting text from file: {str(e)}")
            return ""
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities from text using regex patterns
        
        Args:
            text: Input text
        
        Returns:
            Dictionary of extracted entities
        """
        try:
            entities = {
                'persons': [],
                'locations': [],
                'times': [],
                'dates': [],
                'actions': [],
                'evidence': [],
                'vehicles': []
            }
            
            # Extract persons (capitalized names)
            person_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
            entities['persons'] = list(set(re.findall(person_pattern, text)))
            
            # Extract locations
            location_keywords = ['Street', 'Avenue', 'Road', 'Boulevard', 'Building', 'Park', 'Plaza']
            for keyword in location_keywords:
                pattern = rf'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+{keyword})\b'
                entities['locations'].extend(re.findall(pattern, text))
            
            # Extract times
            time_patterns = [
                r'\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\b',
                r'\b(\d{1,2}\s*(?:AM|PM|am|pm))\b'
            ]
            for pattern in time_patterns:
                entities['times'].extend(re.findall(pattern, text))
            
            # Extract dates
            date_patterns = [
                r'\b(\d{1,2}/\d{1,2}/\d{2,4})\b',
                r'\b([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})\b',
                r'\b(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})\b'
            ]
            for pattern in date_patterns:
                entities['dates'].extend(re.findall(pattern, text))
            
            # Extract evidence items
            evidence_keywords = [
                'weapon', 'knife', 'gun', 'firearm', 'blood', 'fingerprint',
                'DNA', 'evidence', 'shell casing', 'bullet', 'phone', 'wallet',
                'bag', 'backpack', 'clothing', 'shoe', 'footprint'
            ]
            for keyword in evidence_keywords:
                if keyword.lower() in text.lower():
                    # Extract context around keyword
                    pattern = rf'([^.]*{keyword}[^.]*\.)'
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    entities['evidence'].extend(matches)
            
            # Extract vehicles
            vehicle_patterns = [
                r'\b((?:red|blue|black|white|silver|gray|green)\s+(?:car|truck|van|SUV|sedan|vehicle))\b',
                r'\b([A-Z][a-z]+\s+[A-Z][a-z]+\s+(?:car|truck|van|SUV))\b',  # Brand Model
            ]
            for pattern in vehicle_patterns:
                entities['vehicles'].extend(re.findall(pattern, text, re.IGNORECASE))
            
            # Remove duplicates
            for key in entities:
                entities[key] = list(set(entities[key]))
            
            logger.info(f"Extracted entities: {sum(len(v) for v in entities.values())} total")
            
            return entities
        
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return {}
    
    def extract_relationships(self, text: str, entities: Dict) -> List[Dict]:
        """
        Extract relationships between entities
        
        Args:
            text: Input text
            entities: Extracted entities
        
        Returns:
            List of relationship dictionaries
        """
        relationships = []
        
        # Simple relationship extraction based on proximity
        sentences = text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Find entities in this sentence
            found_persons = [p for p in entities.get('persons', []) if p in sentence]
            found_locations = [l for l in entities.get('locations', []) if l in sentence]
            found_times = [t for t in entities.get('times', []) if t in sentence]
            
            # Create relationships
            if found_persons and found_locations:
                for person in found_persons:
                    for location in found_locations:
                        relationships.append({
                            'type': 'person_at_location',
                            'subject': person,
                            'object': location,
                            'context': sentence
                        })
            
            if found_persons and found_times:
                for person in found_persons:
                    for time in found_times:
                        relationships.append({
                            'type': 'person_at_time',
                            'subject': person,
                            'object': time,
                            'context': sentence
                        })
        
        logger.info(f"Extracted {len(relationships)} relationships")
        
        return relationships
    
    def process_report(self, file_path: str) -> Dict[str, Any]:
        """
        Complete report processing pipeline
        
        Args:
            file_path: Path to report file
        
        Returns:
            Dictionary with extracted information
        """
        try:
            # Extract text
            text = self.extract_text_from_file(file_path)
            
            if not text:
                return {'error': 'No text extracted from file'}
            
            # Extract entities
            entities = self.extract_entities(text)
            
            # Extract relationships
            relationships = self.extract_relationships(text, entities)
            
            # Generate summary
            summary = self._generate_summary(text, entities)
            
            return {
                'file_path': file_path,
                'text': text,
                'entities': entities,
                'relationships': relationships,
                'summary': summary,
                'word_count': len(text.split())
            }
        
        except Exception as e:
            logger.error(f"Error processing report: {str(e)}")
            return {'error': str(e)}
    
    def _generate_summary(self, text: str, entities: Dict) -> str:
        """
        Generate a summary of the report
        
        Args:
            text: Full text
            entities: Extracted entities
        
        Returns:
            Summary string
        """
        summary_parts = []
        
        if entities.get('persons'):
            summary_parts.append(f"{len(entities['persons'])} persons mentioned")
        
        if entities.get('locations'):
            summary_parts.append(f"{len(entities['locations'])} locations identified")
        
        if entities.get('evidence'):
            summary_parts.append(f"{len(entities['evidence'])} evidence items referenced")
        
        if entities.get('vehicles'):
            summary_parts.append(f"{len(entities['vehicles'])} vehicles described")
        
        return ', '.join(summary_parts) if summary_parts else "Report processed"

# Create service instance
text_service = TextService()
