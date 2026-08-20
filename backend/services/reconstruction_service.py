"""
3D Reconstruction Service - Generates spatial scene representation
Uses Open3D for 3D processing
"""
import numpy as np
import open3d as o3d
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from config import RECONSTRUCTION_CONFIG, RECONSTRUCTIONS_DIR
from utils.logger import setup_logger

logger = setup_logger('reconstruction_service')

class ReconstructionService:
    """Service for 3D scene reconstruction"""
    
    def __init__(self):
        self.default_room_size = RECONSTRUCTION_CONFIG['default_room_size']
    
    def reconstruct_scene(
        self,
        vision_results: List[Dict],
        fusion_results: Dict,
        case_id: str
    ) -> Dict[str, Any]:
        """
        Reconstruct 3D scene from detection results
        
        Args:
            vision_results: Vision processing results
            fusion_results: Fused multimodal results
            case_id: Case identifier
        
        Returns:
            3D scene data
        """
        try:
            logger.info(f"Reconstructing 3D scene for case: {case_id}")
            
            # Create room structure
            room = self._create_room_structure()
            
            # Place detected objects
            objects = self._place_objects(vision_results, fusion_results)
            
            # Generate scene data
            scene_data = {
                'case_id': case_id,
                'room': room,
                'objects': objects,
                'metadata': {
                    'total_objects': len(objects),
                    'room_size': self.default_room_size
                }
            }
            
            # Save scene data
            output_path = self._save_scene_data(scene_data, case_id)
            
            # Generate 3D visualization (optional)
            visualization_path = self._generate_visualization(scene_data, case_id)
            
            return {
                'scene_data': scene_data,
                'output_path': output_path,
                'visualization_path': visualization_path
            }
        
        except Exception as e:
            logger.error(f"Error reconstructing scene: {str(e)}")
            return {'error': str(e)}
    
    def _create_room_structure(self) -> Dict[str, Any]:
        """Create basic room structure"""
        width, depth, height = self.default_room_size
        
        # Define room boundaries
        room = {
            'type': 'room',
            'dimensions': {
                'width': width,
                'depth': depth,
                'height': height
            },
            'walls': [
                {'name': 'north', 'position': [0, depth/2, height/2], 'size': [width, 0.1, height]},
                {'name': 'south', 'position': [0, -depth/2, height/2], 'size': [width, 0.1, height]},
                {'name': 'east', 'position': [width/2, 0, height/2], 'size': [0.1, depth, height]},
                {'name': 'west', 'position': [-width/2, 0, height/2], 'size': [0.1, depth, height]}
            ],
            'floor': {
                'position': [0, 0, 0],
                'size': [width, depth, 0.1]
            },
            'ceiling': {
                'position': [0, 0, height],
                'size': [width, depth, 0.1]
            }
        }
        
        return room
    
    def _place_objects(
        self,
        vision_results: List[Dict],
        fusion_results: Dict
    ) -> List[Dict]:
        """Place detected objects in 3D space"""
        objects = []
        object_id = 0
        
        # Get unified entities from fusion
        entities = fusion_results.get('unified_entities', {})
        
        # Process vision detections
        for result in vision_results:
            detections = result.get('detections', [])
            
            for detection in detections:
                # Estimate 3D position from 2D bbox
                position = self._estimate_3d_position(detection.get('bbox', {}))
                
                # Determine object size
                size = self._estimate_object_size(detection.get('label', 'unknown'))
                
                objects.append({
                    'id': object_id,
                    'label': detection.get('label', 'unknown'),
                    'position': position,
                    'size': size,
                    'confidence': detection.get('confidence', 0),
                    'source': 'vision',
                    'color': self._get_object_color(detection.get('label', 'unknown'))
                })
                
                object_id += 1
        
        logger.info(f"Placed {len(objects)} objects in 3D scene")
        
        return objects
    
    def _estimate_3d_position(self, bbox: Dict) -> List[float]:
        """Estimate 3D position from 2D bounding box"""
        # Simple heuristic: use bbox center and assume ground level
        if not bbox:
            return [0, 0, 0]
        
        # Normalize bbox coordinates to room space
        width, depth, height = self.default_room_size
        
        # Center of bbox
        x_center = (bbox.get('x1', 0) + bbox.get('x2', 0)) / 2
        y_center = (bbox.get('y1', 0) + bbox.get('y2', 0)) / 2
        
        # Map to room coordinates (simplified)
        # Assume image width/height of 1920x1080
        x = (x_center / 1920 - 0.5) * width
        y = (y_center / 1080 - 0.5) * depth
        z = 0.5  # Ground level
        
        return [round(x, 2), round(y, 2), round(z, 2)]
    
    def _estimate_object_size(self, label: str) -> List[float]:
        """Estimate object size based on label"""
        # Default sizes for common objects (width, depth, height in meters)
        size_map = {
            'person': [0.5, 0.3, 1.7],
            'car': [1.8, 4.5, 1.5],
            'truck': [2.5, 6.0, 2.5],
            'backpack': [0.3, 0.2, 0.4],
            'handbag': [0.3, 0.1, 0.2],
            'cell phone': [0.08, 0.15, 0.01],
            'bottle': [0.08, 0.08, 0.25],
            'knife': [0.05, 0.2, 0.02],
            'gun': [0.05, 0.2, 0.15]
        }
        
        return size_map.get(label.lower(), [0.2, 0.2, 0.2])
    
    def _get_object_color(self, label: str) -> List[float]:
        """Get color for object type (RGB normalized)"""
        color_map = {
            'person': [0.2, 0.6, 1.0],  # Blue
            'weapon': [1.0, 0.2, 0.2],  # Red
            'knife': [1.0, 0.2, 0.2],
            'gun': [1.0, 0.2, 0.2],
            'car': [0.5, 0.5, 0.5],  # Gray
            'truck': [0.5, 0.5, 0.5],
            'backpack': [0.8, 0.6, 0.2],  # Orange
            'handbag': [0.8, 0.4, 0.8],  # Purple
            'cell phone': [0.3, 0.3, 0.3],  # Dark gray
            'bottle': [0.2, 0.8, 0.2]  # Green
        }
        
        return color_map.get(label.lower(), [0.7, 0.7, 0.7])
    
    def _save_scene_data(self, scene_data: Dict, case_id: str) -> str:
        """Save scene data as JSON"""
        output_dir = RECONSTRUCTIONS_DIR / case_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / 'scene.json'
        
        with open(output_path, 'w') as f:
            json.dump(scene_data, f, indent=2)
        
        logger.info(f"Saved scene data: {output_path}")
        
        return str(output_path)
    
    def _generate_visualization(self, scene_data: Dict, case_id: str) -> str:
        """Generate 3D visualization using Open3D"""
        try:
            # Create geometries
            geometries = []
            
            # Add room floor
            floor = scene_data['room']['floor']
            floor_mesh = o3d.geometry.TriangleMesh.create_box(
                width=floor['size'][0],
                height=floor['size'][2],
                depth=floor['size'][1]
            )
            floor_mesh.translate([-floor['size'][0]/2, -floor['size'][1]/2, 0])
            floor_mesh.paint_uniform_color([0.8, 0.8, 0.8])
            geometries.append(floor_mesh)
            
            # Add objects
            for obj in scene_data['objects']:
                # Create box for object
                obj_mesh = o3d.geometry.TriangleMesh.create_box(
                    width=obj['size'][0],
                    height=obj['size'][2],
                    depth=obj['size'][1]
                )
                
                # Position object
                position = obj['position']
                obj_mesh.translate([
                    position[0] - obj['size'][0]/2,
                    position[1] - obj['size'][1]/2,
                    position[2]
                ])
                
                # Color object
                obj_mesh.paint_uniform_color(obj['color'])
                
                geometries.append(obj_mesh)
            
            # Save visualization
            output_dir = RECONSTRUCTIONS_DIR / case_id
            vis_path = output_dir / 'scene_visualization.ply'
            
            # Combine geometries
            combined = o3d.geometry.TriangleMesh()
            for geom in geometries:
                combined += geom
            
            o3d.io.write_triangle_mesh(str(vis_path), combined)
            
            logger.info(f"Saved 3D visualization: {vis_path}")
            
            return str(vis_path)
        
        except Exception as e:
            logger.error(f"Error generating visualization: {str(e)}")
            return ""

# Create service instance
reconstruction_service = ReconstructionService()
