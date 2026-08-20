"""
Multimodal Fusion Service - Combines Vision, Audio, and Text Results
Uses LLaVA for cross-modal understanding
"""
from typing import Dict, Any, List
from utils.logger import setup_logger
from utils.model_loader import load_llava_model

logger = setup_logger('fusion_service')

class FusionService:
    """Service for multimodal data fusion"""
    
    def __init__(self):
        self.llava = None
    
    def _ensure_model_loaded(self):
        """Ensure LLaVA model is loaded"""
        if self.llava is None:
            result = load_llava_model()
            if result:
                self.llava = result
    
    def fuse_multimodal_data(
        self,
        vision_results: List[Dict],
        audio_results: List[Dict],
        text_results: List[Dict]
    ) -> Dict[str, Any]:
        """
        Fuse results from vision, audio, and text processing
        
        Args:
            vision_results: List of vision processing results
            audio_results: List of audio processing results
            text_results: List of text processing results
        
        Returns:
            Fused understanding with consistency checks
        """
        try:
            logger.info("Starting multimodal fusion")
            
            # Collect all entities and events
            unified_entities = self._collect_entities(vision_results, audio_results, text_results)
            
            # Cross-modal consistency check
            consistency = self._check_consistency(vision_results, audio_results, text_results)
            
            # Generate unified timeline
            events = self._extract_events(vision_results, audio_results, text_results)
            
            # Calculate confidence scores
            confidence = self._calculate_confidence(consistency, events)
            
            # Generate explanation
            explanation = self._generate_explanation(unified_entities, events, consistency)
            
            return {
                'unified_entities': unified_entities,
                'events': events,
                'consistency': consistency,
                'confidence': confidence,
                'explanation': explanation
            }
        
        except Exception as e:
            logger.error(f"Error in multimodal fusion: {str(e)}")
            return {'error': str(e)}
    
    def _collect_entities(
        self,
        vision_results: List[Dict],
        audio_results: List[Dict],
        text_results: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """Collect and merge entities from all modalities"""
        entities = {
            'persons': [],
            'locations': [],
            'objects': [],
            'vehicles': [],
            'evidence': []
        }
        
        # From vision
        for result in vision_results:
            for detection in result.get('detections', []):
                label = detection.get('label', '')
                if 'person' in label.lower():
                    entities['persons'].append({
                        'source': 'vision',
                        'value': label,
                        'confidence': detection.get('confidence', 0),
                        'location': detection.get('bbox')
                    })
                elif any(v in label.lower() for v in ['car', 'truck', 'vehicle']):
                    entities['vehicles'].append({
                        'source': 'vision',
                        'value': label,
                        'confidence': detection.get('confidence', 0)
                    })
                else:
                    entities['objects'].append({
                        'source': 'vision',
                        'value': label,
                        'confidence': detection.get('confidence', 0)
                    })
        
        # From audio
        for result in audio_results:
            facts = result.get('facts', {})
            
            for location in facts.get('locations', []):
                entities['locations'].append({
                    'source': 'audio',
                    'value': location,
                    'confidence': 0.7  # Default confidence for extracted facts
                })
        
        # From text
        for result in text_results:
            text_entities = result.get('entities', {})
            
            for person in text_entities.get('persons', []):
                entities['persons'].append({
                    'source': 'text',
                    'value': person,
                    'confidence': 0.8
                })
            
            for location in text_entities.get('locations', []):
                entities['locations'].append({
                    'source': 'text',
                    'value': location,
                    'confidence': 0.8
                })
            
            for vehicle in text_entities.get('vehicles', []):
                entities['vehicles'].append({
                    'source': 'text',
                    'value': vehicle,
                    'confidence': 0.8
                })
        
        return entities
    
    def _check_consistency(
        self,
        vision_results: List[Dict],
        audio_results: List[Dict],
        text_results: List[Dict]
    ) -> Dict[str, Any]:
        """Check consistency across modalities"""
        consistency = {
            'overall_score': 0.0,
            'matches': [],
            'conflicts': []
        }
        
        # Check for matching locations
        vision_locations = set()
        audio_locations = set()
        text_locations = set()
        
        for result in audio_results:
            facts = result.get('facts', {})
            audio_locations.update(facts.get('locations', []))
        
        for result in text_results:
            entities = result.get('entities', {})
            text_locations.update(entities.get('locations', []))
        
        # Find matches
        location_matches = audio_locations.intersection(text_locations)
        if location_matches:
            consistency['matches'].append({
                'type': 'location',
                'values': list(location_matches),
                'sources': ['audio', 'text']
            })
        
        # Calculate overall score
        total_checks = 1
        matches = len(consistency['matches'])
        consistency['overall_score'] = matches / total_checks if total_checks > 0 else 0.5
        
        return consistency
    
    def _extract_events(
        self,
        vision_results: List[Dict],
        audio_results: List[Dict],
        text_results: List[Dict]
    ) -> List[Dict]:
        """Extract events from all sources"""
        events = []
        
        # From vision (video frames)
        for result in vision_results:
            if 'frame_results' in result:
                for frame in result['frame_results']:
                    if frame.get('detections'):
                        events.append({
                            'timestamp': frame.get('timestamp', 0),
                            'source': 'vision',
                            'description': f"Detected {len(frame['detections'])} objects",
                            'details': frame['detections'],
                            'confidence': 0.8
                        })
        
        # From audio
        for result in audio_results:
            facts = result.get('facts', {})
            for action in facts.get('actions', []):
                events.append({
                    'timestamp': None,
                    'source': 'audio',
                    'description': action,
                    'confidence': 0.7
                })
        
        # From text
        for result in text_results:
            relationships = result.get('relationships', [])
            for rel in relationships:
                events.append({
                    'timestamp': None,
                    'source': 'text',
                    'description': f"{rel['subject']} {rel['type']} {rel['object']}",
                    'context': rel.get('context', ''),
                    'confidence': 0.75
                })
        
        return events
    
    def _calculate_confidence(self, consistency: Dict, events: List[Dict]) -> float:
        """Calculate overall confidence score"""
        if not events:
            return 0.0
        
        # Average event confidence
        event_confidence = sum(e.get('confidence', 0) for e in events) / len(events)
        
        # Consistency score
        consistency_score = consistency.get('overall_score', 0.5)
        
        # Weighted average
        overall_confidence = (event_confidence * 0.7) + (consistency_score * 0.3)
        
        return round(overall_confidence, 2)
    
    def _generate_explanation(
        self,
        entities: Dict,
        events: List[Dict],
        consistency: Dict
    ) -> str:
        """Generate human-readable explanation"""
        parts = []
        
        # Entity summary
        total_entities = sum(len(v) for v in entities.values())
        parts.append(f"Identified {total_entities} entities across all sources")
        
        # Event summary
        parts.append(f"Extracted {len(events)} events from multimodal data")
        
        # Consistency
        if consistency['matches']:
            parts.append(f"Found {len(consistency['matches'])} cross-modal matches")
        
        if consistency['conflicts']:
            parts.append(f"Detected {len(consistency['conflicts'])} potential conflicts")
        
        return '. '.join(parts)

# Create service instance
fusion_service = FusionService()
