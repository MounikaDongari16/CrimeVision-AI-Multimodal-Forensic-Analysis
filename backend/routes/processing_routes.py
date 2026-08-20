"""
Processing Routes - Handle AI processing tasks
"""
from flask import Blueprint, request, jsonify
from pathlib import Path
from services import (
    vision_service,
    audio_service,
    text_service,
    fusion_service,
    timeline_service,
    reconstruction_service,
    report_service
)
from utils.logger import setup_logger
from config import IMAGES_DIR, VIDEOS_DIR, AUDIO_DIR, REPORTS_DIR

logger = setup_logger('processing_routes')

processing_bp = Blueprint('processing', __name__, url_prefix='/api/process')

@processing_bp.route('/analyze-image', methods=['POST'])
def analyze_image_direct():
    """
    Direct endpoint for detailed image analysis
    Returns facts, counts, description, and scenarios
    """
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'No image file uploaded'}), 400
            
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No selected file'}), 400
            
        # Save temp file
        import tempfile
        import os
        from werkzeug.utils import secure_filename
        
        filename = secure_filename(file.filename)
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        logger.info(f"Analyzing uploaded image: {filename}")
        
        # Analyze
        result = vision_service.analyze_crime_scene(temp_path)
        
        # 5. Store in Session for Chat
        from utils.session_store import session_store
        session_id = session_store.create_session(result)
        result['session_id'] = session_id

        # Clean up
        try:
            os.remove(temp_path)
        except:
            pass
            
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in direct image analysis: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error analyzing image: {str(e)}'
        }), 500

@processing_bp.route('/analyze-image-visual', methods=['POST'])
def analyze_image_visual():
    """
    Analyze image and return annotated image with GREEN bounding boxes
    """
    try:
        logger.info("=== VISUAL IMAGE ANALYSIS STARTED ===")
        
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'No image file uploaded'}), 400
            
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No selected file'}), 400
            
        # Save temp file
        import tempfile
        import os
        from werkzeug.utils import secure_filename
        
        filename = secure_filename(file.filename)
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        logger.info(f"Image saved to: {temp_path}")
        logger.info("Running comprehensive analysis (RT-DETR + BLIP + CLIP + Groq)...")
        
        # Run detection and comprehensive analysis
        analysis_result = vision_service.analyze_crime_scene(temp_path)
        
        if analysis_result.get('status') == 'success':
            detections = analysis_result.get('detections', [])
            facts = analysis_result.get('facts', {})
            scenarios = analysis_result.get('scenarios', [])
            segmentations = analysis_result.get('segmentations', [])
        else:
            return jsonify({'success': False, 'message': analysis_result.get('error', 'Analysis failed')}), 500

        logger.info(f"Analysis complete. Detected {len(detections)} objects.")
        
        # Annotate image with GREEN boxes and SAM masks
        annotated_url = None
        if len(detections) > 0:
            logger.info("Drawing green bounding boxes and precision masks...")
            annotated_path = vision_service.annotate_image(temp_path, detections, segmentations)
            static_filename = os.path.basename(annotated_path)
            annotated_url = f"/api/results/annotated/{static_filename}"
        
        # 5. Store in Session for Chat
        from utils.session_store import session_store
        session_id = session_store.create_session(analysis_result)

        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass
        
        # Calculate stats
        avg_confidence = 0
        if detections:
            avg_confidence = sum(d['confidence'] for d in detections) / len(detections)
        
        logger.info("=== VISUAL IMAGE ANALYSIS COMPLETE ===")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'detections': detections,
            'facts': facts,
            'scenarios': scenarios,
            'object_count': len(detections),
            'avg_confidence': round(avg_confidence, 2),
            'annotated_image_url': annotated_url,
            'message': f"Detected {len(detections)} objects" if detections else "No objects detected"
        }), 200
        
    except Exception as e:
        logger.error(f"Error in visual image analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error analyzing image: {str(e)}'
        }), 500

@processing_bp.route('/report/image/<case_id>', methods=['POST'])
def generate_image_report(case_id):
    """
    Generate PDF report specific to Image Analysis
    """
    try:
        from utils.pdf_generator import PDFGenerator
        from config import REPORTS_OUTPUT_DIR
        
        data = request.get_json()
        image_path = data.get('image_path') # Full path sent from frontend or reconstructed
        facts = data.get('facts', {})
        scenarios = data.get('scenarios', [])
        
        pdf_gen = PDFGenerator(REPORTS_OUTPUT_DIR)
        filename = pdf_gen.generate_report(case_id, image_path, facts, scenarios)
        
        # Return URL to access report
        report_url = f"/api/results/download/{filename}"
        
        return jsonify({
            'success': True,
            'pdf_url': report_url,
            'filename': filename
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error generating PDF: {str(e)}'
        }), 500

@processing_bp.route('/vision/<case_id>', methods=['POST'])
def process_vision(case_id):
    """
    Process all images and videos for a case
    
    Response:
        - success: Boolean
        - results: Vision processing results
    """
    try:
        logger.info(f"Processing vision data for case: {case_id}")
        
        results = []
        
        # Process images
        images_dir = IMAGES_DIR / case_id
        if images_dir.exists():
            for image_path in images_dir.iterdir():
                if image_path.is_file():
                    result = vision_service.detect_objects(str(image_path))
                    results.append(result)
        
        # Process videos
        videos_dir = VIDEOS_DIR / case_id
        if videos_dir.exists():
            for video_path in videos_dir.iterdir():
                if video_path.is_file():
                    result = vision_service.process_video(str(video_path), case_id)
                    results.append(result)
        
        logger.info(f"Vision processing complete: {len(results)} files processed")
        
        return jsonify({
            'success': True,
            'case_id': case_id,
            'total_processed': len(results),
            'results': results
        }), 200
    
    except Exception as e:
        logger.error(f"Error processing vision: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error processing vision: {str(e)}'
        }), 500

@processing_bp.route('/audio/<case_id>', methods=['POST'])
def process_audio(case_id):
    """
    Process all audio files for a case
    
    Response:
        - success: Boolean
        - results: Audio processing results
    """
    try:
        logger.info(f"Processing audio data for case: {case_id}")
        
        results = []
        
        # Process audio files
        audio_dir = AUDIO_DIR / case_id
        if audio_dir.exists():
            for audio_path in audio_dir.iterdir():
                if audio_path.is_file():
                    result = audio_service.process_audio_file(str(audio_path))
                    results.append(result)
        
        logger.info(f"Audio processing complete: {len(results)} files processed")
        
        return jsonify({
            'success': True,
            'case_id': case_id,
            'total_processed': len(results),
            'results': results
        }), 200
    
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error processing audio: {str(e)}'
        }), 500

@processing_bp.route('/text/<case_id>', methods=['POST'])
def process_text(case_id):
    """
    Process all text reports for a case
    
    Response:
        - success: Boolean
        - results: Text processing results
    """
    try:
        logger.info(f"Processing text data for case: {case_id}")
        
        results = []
        
        # Process reports
        reports_dir = REPORTS_DIR / case_id
        if reports_dir.exists():
            for report_path in reports_dir.iterdir():
                if report_path.is_file():
                    result = text_service.process_report(str(report_path))
                    results.append(result)
        
        logger.info(f"Text processing complete: {len(results)} files processed")
        
        return jsonify({
            'success': True,
            'case_id': case_id,
            'total_processed': len(results),
            'results': results
        }), 200
    
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error processing text: {str(e)}'
        }), 500

@processing_bp.route('/fusion/<case_id>', methods=['POST'])
def process_fusion(case_id):
    """
    Perform multimodal fusion for a case
    
    Request body:
        - vision_results: Vision processing results
        - audio_results: Audio processing results
        - text_results: Text processing results
    
    Response:
        - success: Boolean
        - results: Fusion results
    """
    try:
        logger.info(f"Processing fusion for case: {case_id}")
        
        data = request.get_json()
        
        vision_results = data.get('vision_results', [])
        audio_results = data.get('audio_results', [])
        text_results = data.get('text_results', [])
        
        # Perform fusion
        fusion_results = fusion_service.fuse_multimodal_data(
            vision_results,
            audio_results,
            text_results
        )
        
        logger.info(f"Fusion processing complete")
        
        return jsonify({
            'success': True,
            'case_id': case_id,
            'results': fusion_results
        }), 200
    
    except Exception as e:
        logger.error(f"Error processing fusion: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error processing fusion: {str(e)}'
        }), 500

@processing_bp.route('/timeline/<case_id>', methods=['POST'])
def generate_timeline(case_id):
    """
    Generate timeline for a case
    
    Request body:
        - vision_results: Vision processing results
        - audio_results: Audio processing results
        - text_results: Text processing results
        - fusion_results: Fusion results
    
    Response:
        - success: Boolean
        - timeline: Timeline data
    """
    try:
        logger.info(f"Generating timeline for case: {case_id}")
        
        data = request.get_json()
        
        vision_results = data.get('vision_results', [])
        audio_results = data.get('audio_results', [])
        text_results = data.get('text_results', [])
        fusion_results = data.get('fusion_results', {})
        
        # Generate timeline
        timeline = timeline_service.generate_timeline(
            vision_results,
            audio_results,
            text_results,
            fusion_results
        )
        
        logger.info(f"Timeline generation complete")
        
        return jsonify({
            'success': True,
            'case_id': case_id,
            'timeline': timeline
        }), 200
    
    except Exception as e:
        logger.error(f"Error generating timeline: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error generating timeline: {str(e)}'
        }), 500

@processing_bp.route('/reconstruct/<case_id>', methods=['POST'])
def reconstruct_scene(case_id):
    """
    Generate 3D scene reconstruction
    
    Request body:
        - vision_results: Vision processing results
        - fusion_results: Fusion results
    
    Response:
        - success: Boolean
        - reconstruction: 3D reconstruction data
    """
    try:
        logger.info(f"Reconstructing scene for case: {case_id}")
        
        data = request.get_json()
        
        vision_results = data.get('vision_results', [])
        fusion_results = data.get('fusion_results', {})
        
        # Reconstruct scene
        reconstruction = reconstruction_service.reconstruct_scene(
            vision_results,
            fusion_results,
            case_id
        )
        
        logger.info(f"Scene reconstruction complete")
        
        return jsonify({
            'success': True,
            'case_id': case_id,
            'reconstruction': reconstruction
        }), 200
    
    except Exception as e:
        logger.error(f"Error reconstructing scene: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error reconstructing scene: {str(e)}'
        }), 500

@processing_bp.route('/report/<case_id>', methods=['POST'])
def generate_report(case_id):
    """
    Generate comprehensive report
    
    Request body:
        - vision_results: Vision processing results
        - audio_results: Audio processing results
        - text_results: Text processing results
        - fusion_results: Fusion results
        - timeline_results: Timeline results
        - reconstruction_results: 3D reconstruction results
    
    Response:
        - success: Boolean
        - report: Report paths
    """
    try:
        logger.info(f"Generating report for case: {case_id}")
        
        data = request.get_json()
        
        # Generate report
        report = report_service.generate_report(
            case_id,
            data.get('vision_results', []),
            data.get('audio_results', []),
            data.get('text_results', []),
            data.get('fusion_results', {}),
            data.get('timeline_results', {}),
            data.get('reconstruction_results', {})
        )
        
        logger.info(f"Report generation complete")
        
        return jsonify({
            'success': True,
            'case_id': case_id,
            'report': report
        }), 200
    
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error generating report: {str(e)}'
        }), 500

@processing_bp.route('/complete/<case_id>', methods=['POST'])
def process_complete_pipeline(case_id):
    """
    Run complete processing pipeline for a case
    
    Response:
        - success: Boolean
        - results: All processing results
    """
    try:
        logger.info(f"Running complete pipeline for case: {case_id}")
        
        # Step 1: Vision processing
        vision_results = []
        vision_facts = {}
        vision_summary = {}
        images_dir = IMAGES_DIR / case_id
        if images_dir.exists():
            for image_path in images_dir.iterdir():
                if image_path.is_file():
                    # Enriched Crime scene specific analysis
                    result = vision_service.analyze_crime_scene(str(image_path))
                    if result and not 'error' in result:
                        vision_results.append(result)
                        vision_summary = result.get('summary', {})
                        for category, items in result.get('facts', {}).items():
                            if category not in vision_facts:
                                vision_facts[category] = []
                            vision_facts[category].extend(items)
        
        # Step 2: Audio processing (with vision context for scenario reasoning)
        audio_results = []
        audio_facts = {}
        audio_dir = AUDIO_DIR / case_id
        if audio_dir.exists():
            for audio_path in audio_dir.iterdir():
                if audio_path.is_file():
                    result = audio_service.process_audio_file(str(audio_path), vision_summary)
                    audio_results.append(result)
                    if 'facts' in result:
                        f = result['facts']
                        for category, items in f.items():
                            if category not in audio_facts:
                                audio_facts[category] = []
                            audio_facts[category].extend(items)

        # Step 3: Text processing
        text_results = []
        reports_dir = REPORTS_DIR / case_id
        if reports_dir.exists():
            for report_path in reports_dir.iterdir():
                if report_path.is_file():
                    result = text_service.process_report(str(report_path))
                    text_results.append(result)
        
        # Step 4: Fusion (Multimodal consistent aggregation)
        fusion_results = fusion_service.fuse_multimodal_data(
            vision_results,
            audio_results,
            text_results
        )
        
        # Step 5: Timeline
        timeline_results = timeline_service.generate_timeline(
            vision_results,
            audio_results,
            text_results,
            fusion_results
        )
        
        # Step 6: 3D Reconstruction
        reconstruction_results = reconstruction_service.reconstruct_scene(
            vision_results,
            fusion_results,
            case_id
        )
        
        # Step 7: Enriched Report Generation
        report_results = report_service.generate_report(
            case_id,
            vision_results,
            audio_results,
            text_results,
            fusion_results,
            timeline_results,
            reconstruction_results
        )
        
        # Merge all facts for the UI
        all_facts = {**audio_facts}
        for cat, items in vision_facts.items():
            if cat in all_facts:
                all_facts[cat].extend(items)
            else:
                all_facts[cat] = items
        
        # Deduplicate all facts
        for cat in all_facts:
            all_facts[cat] = list(set(all_facts[cat]))

        logger.info(f"Complete pipeline finished for case: {case_id}")
        
        return jsonify({
            'success': True,
            'case_id': case_id,
            'vision_results': vision_results,
            'audio_results': audio_results,
            'all_facts': all_facts,
            'vision_summary': vision_summary,
            'text_results': text_results,
            'fusion_results': fusion_results,
            'timeline_results': timeline_results,
            'reconstruction_results': reconstruction_results,
            'report_results': report_results
        }), 200
    
    except Exception as e:
        logger.error(f"Error in complete pipeline: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error in complete pipeline: {str(e)}'
        }), 500
