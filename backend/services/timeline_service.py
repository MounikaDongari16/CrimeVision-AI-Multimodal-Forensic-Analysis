"""
Timeline Generation Service - Creates chronological event timeline
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from utils.logger import setup_logger

logger = setup_logger('timeline_service')

class TimelineService:
    """Service for generating chronological timelines"""
    
    def generate_timeline(
        self,
        vision_results: List[Dict],
        audio_results: List[Dict],
        text_results: List[Dict],
        fusion_results: Dict
    ) -> Dict[str, Any]:
        """
        Generate chronological timeline from all sources
        
        Args:
            vision_results: Vision processing results
            audio_results: Audio processing results
            text_results: Text processing results
            fusion_results: Fused multimodal results
        
        Returns:
            Timeline dictionary with ordered events
        """
        try:
            logger.info("Generating timeline")
            
            # Collect all events
            events = []
            
            # Add vision events (with timestamps from video)
            events.extend(self._extract_vision_events(vision_results))
            
            # Add audio events
            events.extend(self._extract_audio_events(audio_results))
            
            # Add text events
            events.extend(self._extract_text_events(text_results))
            
            # Add fusion events
            if fusion_results and 'events' in fusion_results:
                events.extend(fusion_results['events'])
            
            # Sort events by timestamp
            sorted_events = self._sort_events(events)
            
            # Add uncertainty markers
            timeline_with_uncertainty = self._add_uncertainty_markers(sorted_events)
            
            # Generate timeline summary
            summary = self._generate_timeline_summary(timeline_with_uncertainty)
            
            return {
                'events': timeline_with_uncertainty,
                'total_events': len(timeline_with_uncertainty),
                'summary': summary,
                'time_range': self._get_time_range(timeline_with_uncertainty)
            }
        
        except Exception as e:
            logger.error(f"Error generating timeline: {str(e)}")
            return {'error': str(e), 'events': []}
    
    def _extract_vision_events(self, vision_results: List[Dict]) -> List[Dict]:
        """Extract events from vision results"""
        events = []
        
        for result in vision_results:
            # From video frames
            if 'frame_results' in result:
                for frame in result['frame_results']:
                    timestamp = frame.get('timestamp')
                    detections = frame.get('detections', [])
                    
                    if detections:
                        # Group detections by type
                        detection_summary = {}
                        for det in detections:
                            label = det.get('label', 'unknown')
                            detection_summary[label] = detection_summary.get(label, 0) + 1
                        
                        description = ', '.join([f"{count} {label}" for label, count in detection_summary.items()])
                        
                        events.append({
                            'timestamp': timestamp,
                            'source': 'vision',
                            'type': 'detection',
                            'description': f"Detected: {description}",
                            'details': detections,
                            'confidence': sum(d.get('confidence', 0) for d in detections) / len(detections),
                            'has_timestamp': True
                        })
            
            # From single images
            elif 'detections' in result:
                detections = result['detections']
                if detections:
                    events.append({
                        'timestamp': None,
                        'source': 'vision',
                        'type': 'detection',
                        'description': f"Image analysis: {len(detections)} objects detected",
                        'details': detections,
                        'confidence': sum(d.get('confidence', 0) for d in detections) / len(detections),
                        'has_timestamp': False
                    })
        
        return events
    
    def _extract_audio_events(self, audio_results: List[Dict]) -> List[Dict]:
        """Extract events from audio results"""
        events = []
        
        for result in audio_results:
            facts = result.get('facts', {})
            
            # Extract actions as events
            for action in facts.get('actions', []):
                events.append({
                    'timestamp': None,
                    'source': 'audio',
                    'type': 'witness_statement',
                    'description': action,
                    'confidence': 0.7,
                    'has_timestamp': False
                })
            
            # Extract time references
            times = facts.get('times', [])
            locations = facts.get('locations', [])
            
            if times and locations:
                for time in times[:1]:  # Use first time reference
                    for location in locations[:1]:  # Use first location
                        events.append({
                            'timestamp': None,
                            'source': 'audio',
                            'type': 'witness_statement',
                            'description': f"Witness reported activity at {location} around {time}",
                            'confidence': 0.6,
                            'has_timestamp': False,
                            'time_reference': time
                        })
        
        return events
    
    def _extract_text_events(self, text_results: List[Dict]) -> List[Dict]:
        """Extract events from text results"""
        events = []
        
        for result in text_results:
            relationships = result.get('relationships', [])
            
            for rel in relationships:
                events.append({
                    'timestamp': None,
                    'source': 'text',
                    'type': 'report_entry',
                    'description': f"{rel.get('subject', '')} {rel.get('type', '')} {rel.get('object', '')}",
                    'context': rel.get('context', ''),
                    'confidence': 0.75,
                    'has_timestamp': False
                })
        
        return events
    
    def _sort_events(self, events: List[Dict]) -> List[Dict]:
        """Sort events by timestamp"""
        # Separate events with and without timestamps
        timestamped = [e for e in events if e.get('timestamp') is not None]
        non_timestamped = [e for e in events if e.get('timestamp') is None]
        
        # Sort timestamped events
        timestamped.sort(key=lambda x: x['timestamp'])
        
        # Combine: timestamped first, then non-timestamped
        return timestamped + non_timestamped
    
    def _add_uncertainty_markers(self, events: List[Dict]) -> List[Dict]:
        """Add uncertainty markers to events"""
        for event in events:
            confidence = event.get('confidence', 0.5)
            
            if confidence >= 0.8:
                event['certainty'] = 'high'
            elif confidence >= 0.6:
                event['certainty'] = 'medium'
            else:
                event['certainty'] = 'low'
            
            # Mark events without timestamps
            if not event.get('has_timestamp'):
                event['temporal_uncertainty'] = 'unknown'
            else:
                event['temporal_uncertainty'] = 'known'
        
        return events
    
    def _generate_timeline_summary(self, events: List[Dict]) -> str:
        """Generate summary of timeline"""
        if not events:
            return "No events in timeline"
        
        timestamped_count = sum(1 for e in events if e.get('has_timestamp'))
        high_confidence = sum(1 for e in events if e.get('certainty') == 'high')
        
        return (f"Timeline contains {len(events)} events. "
                f"{timestamped_count} events have precise timestamps. "
                f"{high_confidence} events have high confidence.")
    
    def _get_time_range(self, events: List[Dict]) -> Dict[str, Any]:
        """Get time range of timeline"""
        timestamped = [e for e in events if e.get('timestamp') is not None]
        
        if not timestamped:
            return {'start': None, 'end': None, 'duration': None}
        
        timestamps = [e['timestamp'] for e in timestamped]
        start = min(timestamps)
        end = max(timestamps)
        
        return {
            'start': start,
            'end': end,
            'duration': end - start
        }

# Create service instance
timeline_service = TimelineService()
