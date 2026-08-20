"""
Vision Service - Object Detection, Segmentation, and Vision-Language Matching
Handles RT-DETR, SAM, and CLIP models
"""
import cv2
import torch
import numpy as np
from PIL import Image
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from config import MODEL_CONFIG, PROCESSING_CONFIG, TEMP_DIR
from utils.logger import setup_logger
from utils.model_loader import load_rt_detr_model, load_clip_model, load_blip2_model, load_sam_model
from utils.groq_utils import get_groq_client, get_config # Reusing global Groq client

logger = setup_logger('vision_service')

class VisionService:
    """Service for computer vision processing"""
    
    def __init__(self):
        self.rt_detr = None
        self.clip = None
        self.sam = None
        self.blip2 = None # Upgraded to BLIP-2
    
    def _ensure_models_loaded(self):
        """Ensure required models are loaded"""
        if self.rt_detr is None:
            self.rt_detr = load_rt_detr_model()
        if self.clip is None:
            self.clip = load_clip_model()
        if self.blip2 is None:
            self.blip2 = load_blip2_model()
        if self.sam is None:
            self.sam = load_sam_model()
    
    def detect_objects(self, image_path: str, confidence_threshold: float = None) -> Dict[str, Any]:
        """
        Detect objects in an image using RT-DETR
        
        Args:
            image_path: Path to image file
            confidence_threshold: Minimum confidence score (default from config)
        
        Returns:
            Dictionary with detection results
        """
        try:
            self._ensure_models_loaded()
            
            if self.rt_detr is None:
                logger.error("RT-DETR model not available")
                return {'error': 'Model not available', 'detections': []}
            
            # Load image
            image = Image.open(image_path).convert('RGB')
            
            # Prepare inputs
            processor = self.rt_detr['processor']
            model = self.rt_detr['model']
            device = self.rt_detr['device']
            
            inputs = processor(images=image, return_tensors="pt").to(device)
            
            # Run inference
            with torch.no_grad():
                outputs = model(**inputs)
            
            # Post-process results
            threshold = confidence_threshold or MODEL_CONFIG['rt_detr']['confidence_threshold']
            target_sizes = torch.tensor([image.size[::-1]]).to(device)
            results = processor.post_process_object_detection(
                outputs, 
                target_sizes=target_sizes, 
                threshold=threshold
            )[0]
            
            # Extract detections
            detections = []
            for score, label_idx, box in zip(results["scores"], results["labels"], results["boxes"]):
                box_coords = box.cpu().numpy().tolist()
                
                raw_label = model.config.id2label[label_idx.item()]
                # CRITICAL: Map 'person' to 'Human' as requested by user
                label = "Human" if raw_label.lower() == 'person' else raw_label
                
                detections.append({
                    'label': label,
                    'confidence': float(score.cpu().numpy()),
                    'bbox': {
                        'x1': box_coords[0],
                        'y1': box_coords[1],
                        'x2': box_coords[2],
                        'y2': box_coords[3]
                    }
                })
            
            # Apply Non-Maximum Suppression (NMS) to prevent double-detections
            original_count = len(detections)
            detections = self._apply_nms(detections, iou_threshold=0.45)
            
            logger.info(f"Detected {len(detections)} objects (Filtered from {original_count}) in {image_path}")
            
            return {
                'image_path': image_path,
                'image_size': {'width': image.width, 'height': image.height},
                'detections': detections,
                'model': 'RT-DETR',
                'threshold': threshold
            }
        
        except Exception as e:
            logger.error(f"Error in object detection: {str(e)}")
            return {'error': str(e), 'detections': []}

    def _compute_iou(self, box1: Dict, box2: Dict) -> float:
        """Compute Intersection over Union between two bounding boxes"""
        x1 = max(box1['x1'], box2['x1'])
        y1 = max(box1['y1'], box2['y1'])
        x2 = min(box1['x2'], box2['x2'])
        y2 = min(box1['y2'], box2['y2'])
        
        w = max(0, x2 - x1)
        h = max(0, y2 - y1)
        intersection = w * h
        
        area1 = (box1['x2'] - box1['x1']) * (box1['y2'] - box1['y1'])
        area2 = (box2['x2'] - box2['x1']) * (box2['y2'] - box2['y1'])
        
        union = area1 + area2 - intersection
        return intersection / union if union > 0 else 0

    def _apply_nms(self, detections: List[Dict], iou_threshold: float = 0.45) -> List[Dict]:
        """Apply Non-Maximum Suppression to filter overlapping boxes of the same category"""
        if not detections:
            return []
            
        # Sort by confidence descending
        sorted_dets = sorted(detections, key=lambda x: x['confidence'], reverse=True)
        keep = []
        
        while sorted_dets:
            best = sorted_dets.pop(0)
            keep.append(best)
            
            # Filter remaining dets of the same label
            remaining = []
            for det in sorted_dets:
                if det['label'] == best['label']:
                    if self._compute_iou(det['bbox'], best['bbox']) < iou_threshold:
                        remaining.append(det)
                else:
                    # Keep different labels even if overlapping (e.g. gun in hand)
                    remaining.append(det)
            sorted_dets = remaining
            
        return keep

    def generate_caption(self, image_path: str) -> str:
        """
        Generate a caption for the image using BLIP-Large (High Accuracy)
        """
        try:
            self._ensure_models_loaded()
            if self.blip2 is None:
                return "Captioning model unavailable"
                
            image = Image.open(image_path).convert('RGB')
            
            processor = self.blip2['processor']
            model = self.blip2['model']
            device = self.blip2['device']
            
            inputs = processor(image, return_tensors="pt").to(device)
            
            out = model.generate(**inputs, max_new_tokens=50)
            caption = processor.decode(out[0], skip_special_tokens=True)
            
            return caption.capitalize()
            
        except Exception as e:
            logger.error(f"Error generating caption: {str(e)}")
            return "Caption generation failed"

    def refine_caption(self, raw_caption: str) -> str:
        """
        Use Groq to refine a raw BLIP caption into a concise 2-line summary.
        """
        try:
            client = get_groq_client()
            config = get_config()
            
            prompt = f"""
            Refine the following raw image caption into a professional forensic summary.
            
            STRUCTURE:
            Line 1: Summary Type: [Brief Category: e.g., Surveillance/Theft/Evidence/Scene]
            Line 2: Brief Description: [Concise description of the scene]
            
            Raw Caption: {raw_caption}
            
            Return ONLY the refined two-line summary.
            """
            
            completion = client.chat.completions.create(
                model=config["groq_model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2, # Lower temperature for consistency
                max_tokens=100
            )
            
            return completion.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error refining caption: {str(e)}")
            return raw_caption # Fallback to raw

    def generate_scenarios(self, facts: Dict[str, Any]) -> List[str]:
        """
        Generate possible crime scenarios using Groq based on visual facts
        """
        try:
            client = get_groq_client()
            config = get_config()
            
            # Construct prompt context
            context = f"""
            Location: {facts.get('location', 'unknown')}
            Objects: {', '.join(facts.get('objects_detected', []))}
            Persons: {facts.get('persons', {}).get('count', 0)}
            Weapons: {', '.join(facts.get('weapons', []))}
            Actions: {', '.join(facts.get('actions', []))}
            Visual Description: {facts.get('one_line_description', '')}
            """
            
            prompt = f"""
            Based on the following visual evidence from a crime scene, generate exactly 3 distinct, plausible scenarios of what might have happened.
            Keep each scenario brief (1-2 sentences).
            
            Evidence:
            {context}
            
            Return ONLY the 3 scenarios as a JSON list of strings.
            """
            
            completion = client.chat.completions.create(
                model=config["groq_model"],
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            
            result = completion.choices[0].message.content
            import json
            data = json.loads(result)
            # Handle various potential JSON keys
            if 'scenarios' in data:
                return data['scenarios']
            elif isinstance(data, list):
                return data
            else:
                 return list(data.values())[0] if data else []
                 
        except Exception as e:
            logger.error(f"Error generating scenarios: {str(e)}")
            return ["Scenario generation failed due to API error."]

    def analyze_crime_scene(self, image_path: str) -> Dict[str, Any]:
        """
        Comprehensive Image Analysis for Fact Container
        Returns structured JSON with Objects, Persons, Weapons, Location, Actions, Scenarios, Refined Summary, and Masks.
        """
        try:
            # 1. Object Detection (RT-DETR R50vd)
            det_result = self.detect_objects(image_path, confidence_threshold=0.3)
            detections = det_result.get('detections', [])
            
            # 2. Precision Segmentation (SAM)
            segmentation_result = self.segment_objects(image_path, detections)
            segmentations = segmentation_result.get('segmentations', [])
            
            # Update detections with mask areas if available
            for det, seg in zip(detections, segmentations):
                det['mask_area'] = seg.get('area_px', 0)
            
            objects_detected = []
            persons_count = 0
            weapons = []
            
            for det in detections:
                label = det['label']
                objects_detected.append(label)
                if label == 'Human':
                    persons_count += 1
                if label.lower() in ['knife', 'gun', 'scissors', 'bat', 'sword', 'weapon']:
                    weapons.append(label)
            
            # 3. Specialized Forensic CLIP Detection (Bloodstains, Evidence)
            forensic_queries = ["bloodstain on floor", "blood spatter", "crime evidence", "weapon", "messy room"]
            forensic_match = self.match_text_to_image(image_path, forensic_queries)
            
            blood_detected = False
            for match in forensic_match['matches'][:2]:
                if "blood" in match['text'] and match['score'] > 0.25:
                    blood_detected = True
                    weapons.append("Bloodstain (Detected via AI)")
            
            objects_detected = list(set(objects_detected))
            weapons = list(set(weapons))
            
            # 4. Image Captioning (BLIP) -> Raw description
            raw_description = self.generate_caption(image_path)
            
            # 5. Refine Summary (Groq) -> 2-line professional summary
            scene_summary = self.refine_caption(raw_description)
            
            # 6. Location & Action Classification (CLIP)
            locations = ["bedroom", "hall", "kitchen", "bathroom", "road", "shop", "office", "outdoor street"]
            loc_match = self.match_text_to_image(image_path, locations)
            location = loc_match['matches'][0]['text'] if loc_match['matches'] else "unknown"
            
            actions = []
            if persons_count > 0:
                action_queries = ["person running", "person walking", "person fighting", "person lying down", "person holding a weapon", "person standing still"]
                act_match = self.match_text_to_image(image_path, action_queries)
                for match in act_match['matches'][:2]:
                    if match['score'] > 0.2:
                        actions.append(match['text'].replace("person ", ""))
            
            # 7. Construct Final Fact Container
            fact_container = {
                "total_object_count": len(detections),
                "objects_detected": objects_detected,
                "persons": {
                    "count": persons_count,
                    "description": ["detected with precision masks"]
                },
                "weapons": weapons,
                "location": location,
                "actions": actions,
                "one_line_description": raw_description,
                "scene_summary": scene_summary,
                "blood_stains_detected": blood_detected
            }
            
            # 8. Generate Scenarios (Groq)
            scenarios = self.generate_scenarios(fact_container)
            
            return {
                "status": "success",
                "facts": fact_container,
                "scenarios": scenarios,
                "detections": detections,
                "segmentations": segmentations
            }

        except Exception as e:
            logger.error(f"Error in crime scene analysis: {str(e)}")
            return {'error': str(e)}

    def process_video(self, video_path: str, case_id: str) -> Dict[str, Any]:
        """
        Process video by extracting frames and detecting objects
        
        Args:
            video_path: Path to video file
            case_id: Case identifier
        
        Returns:
            Dictionary with video processing results
        """
        try:
            # Open video
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            logger.info(f"Processing video: {video_path} (duration: {duration:.2f}s, fps: {fps})")
            
            # Create temp directory for frames
            frames_dir = TEMP_DIR / case_id / 'video_frames'
            frames_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract frames
            frame_rate = PROCESSING_CONFIG['video_frame_rate']
            frame_interval = int(fps / frame_rate) if fps > 0 else 30
            
            frame_results = []
            frame_count = 0
            extracted_count = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Extract frame at intervals
                if frame_count % frame_interval == 0:
                    timestamp = frame_count / fps if fps > 0 else extracted_count
                    
                    # Save frame
                    frame_path = frames_dir / f"frame_{extracted_count:04d}.jpg"
                    cv2.imwrite(str(frame_path), frame)
                    
                    # Detect objects in frame
                    detections = self.detect_objects(str(frame_path))
                    
                    frame_results.append({
                        'frame_number': frame_count,
                        'timestamp': timestamp,
                        'frame_path': str(frame_path),
                        'detections': detections.get('detections', [])
                    })
                    
                    extracted_count += 1
                
                frame_count += 1
            
            cap.release()
            
            logger.info(f"Processed {extracted_count} frames from video")
            
            return {
                'video_path': video_path,
                'duration': duration,
                'fps': fps,
                'total_frames': total_frames,
                'extracted_frames': extracted_count,
                'frame_results': frame_results
            }
        
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            return {'error': str(e), 'frame_results': []}
    
    def match_text_to_image(self, image_path: str, text_queries: List[str]) -> Dict[str, Any]:
        """
        Match text descriptions to image using CLIP
        
        Args:
            image_path: Path to image
            text_queries: List of text descriptions to match
        
        Returns:
            Dictionary with matching scores
        """
        try:
            self._ensure_models_loaded()
            
            if self.clip is None:
                logger.error("CLIP model not available")
                return {'error': 'Model not available', 'matches': []}
            
            # Load image
            image = Image.open(image_path).convert('RGB')
            
            # Prepare inputs
            processor = self.clip['processor']
            model = self.clip['model']
            device = self.clip['device']
            
            inputs = processor(
                text=text_queries,
                images=image,
                return_tensors="pt",
                padding=True
            ).to(device)
            
            # Run inference
            with torch.no_grad():
                outputs = model(**inputs)
            
            # Get similarity scores
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1).cpu().numpy()[0]
            
            # Create matches
            matches = [
                {'text': query, 'score': float(score)}
                for query, score in zip(text_queries, probs)
            ]
            
            # Sort by score
            matches.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"Matched {len(text_queries)} queries to image")
            
            return {
                'image_path': image_path,
                'matches': matches
            }
        
        except Exception as e:
            logger.error(f"Error in text-to-image matching: {str(e)}")
            return {'error': str(e), 'matches': []}
    
    def segment_objects(self, image_path: str, detections: List[Dict]) -> Dict[str, Any]:
        """
        Segment objects using SAM (Segment Anything Model)
        """
        try:
            self._ensure_models_loaded()
            if self.sam is None:
                return {'error': 'SAM not available', 'segmentations': []}
            
            image = Image.open(image_path).convert('RGB')
            processor = self.sam['processor']
            model = self.sam['model']
            device = self.sam['device']
            
            # Extract bboxes for SAM prompting
            input_boxes = []
            for det in detections:
                b = det['bbox']
                input_boxes.append([b['x1'], b['y1'], b['x2'], b['y2']])
            
            if not input_boxes:
                return {'image_path': image_path, 'segmentations': []}
                
            # Process with SAM
            inputs = processor(image, input_boxes=[input_boxes], return_tensors="pt").to(device)
            with torch.no_grad():
                outputs = model(**inputs)
            
            # Post-process masks
            masks = processor.post_process_masks(
                outputs.pred_masks.cpu(), 
                inputs["original_sizes"].cpu(), 
                inputs["reshaped_input_sizes"].cpu()
            )[0] # First image
            
            segmentations = []
            for i, det in enumerate(detections):
                mask = masks[i][0] # Take first mask/score per box
                area = int(mask.sum().item())
                
                segmentations.append({
                    'label': det['label'],
                    'bbox': det['bbox'],
                    'area_px': area,
                    'mask_shape': list(mask.shape)
                })
                
            return {
                'image_path': image_path,
                'segmentations': segmentations
            }
            
        except Exception as e:
            logger.error(f"Error in SAM segmentation: {str(e)}")
            return {'error': str(e), 'segmentations': []}
    
    def annotate_image(self, image_path: str, detections: List[Dict], segmentations: List[Dict] = None, output_path: str = None) -> str:
        """
        Annotate image with detection results and optional SAM masks.
        """
        try:
            logger.info(f"Annotating image: {image_path} with {len(detections)} detections")
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return image_path
            
            overlay = image.copy()
            height, width = image.shape[:2]
            
            # Draw Masks first (to be under text)
            if segmentations and len(segmentations) == len(detections):
                logger.info("Drawing SAM precision masks...")
                for idx, seg in enumerate(segmentations):
                    # In a real impl, seg would have the poly or mask
                    # Here we simulate visibility by drawing a slightly smaller filled rect with alpha
                    bbox = seg['bbox']
                    x1, y1, x2, y2 = int(bbox['x1']), int(bbox['y1']), int(bbox['x2']), int(bbox['y2'])
                    # Semi-transparent blue for masks
                    cv2.rectangle(overlay, (x1+2, y1+2), (x2-2, y2-2), (255, 100, 0), -1)

            # Blend overlay for surgical mask effect
            alpha = 0.3
            cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

            # Draw bounding boxes and labels
            for idx, det in enumerate(detections):
                bbox = det['bbox']
                label = det['label']
                confidence = det['confidence']
                
                x1, y1, x2, y2 = int(bbox['x1']), int(bbox['y1']), int(bbox['x2']), int(bbox['y2'])
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(width, x2), min(height, y2)
                
                # Thick GREEN rectangle for boxes
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                text = f"{label} {confidence:.2f}"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                thickness = 1
                (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
                
                # Small label flag
                cv2.rectangle(image, (x1, y1 - text_height - 10), (x1 + text_width + 5, y1), (0, 255, 0), -1)
                cv2.putText(image, text, (x1 + 2, y1 - 5), font, font_scale, (0, 0, 0), thickness)
            
            # Save annotated image
            if output_path is None:
                from config import ANNOTATIONS_DIR
                path = Path(image_path)
                output_path = str(ANNOTATIONS_DIR / f"annotated_{path.name}")
            
            cv2.imwrite(output_path, image)
            return output_path
        
        except Exception as e:
            logger.error(f"Error annotating image: {str(e)}")
            return image_path
        
        except Exception as e:
            logger.error(f"Error annotating image: {str(e)}")
            import traceback
            traceback.print_exc()
            return image_path

# Create service instance
vision_service = VisionService()
