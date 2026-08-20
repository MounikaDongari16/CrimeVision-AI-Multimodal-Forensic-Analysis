"""
Results Routes - Fetch processing results and download reports
"""
from flask import Blueprint, request, jsonify, send_file
from pathlib import Path
from config import REPORTS_OUTPUT_DIR, RECONSTRUCTIONS_DIR, ANNOTATIONS_DIR
from utils.logger import setup_logger
import json

logger = setup_logger('results_routes')

results_bp = Blueprint('results', __name__, url_prefix='/api/results')

@results_bp.route('/timeline/<case_id>', methods=['GET'])
def get_timeline(case_id):
    """
    Get timeline data for a case
    
    Response:
        - success: Boolean
        - timeline: Timeline data
    """
    try:
        # Timeline data would be stored during processing
        # For now, return placeholder
        return jsonify({
            'success': True,
            'case_id': case_id,
            'message': 'Timeline data would be retrieved from storage'
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting timeline: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting timeline: {str(e)}'
        }), 500

@results_bp.route('/scene/<case_id>', methods=['GET'])
def get_scene(case_id):
    """
    Get 3D scene data for a case
    
    Response:
        - success: Boolean
        - scene_data: 3D scene JSON data
    """
    try:
        scene_path = RECONSTRUCTIONS_DIR / case_id / 'scene.json'
        
        if not scene_path.exists():
            return jsonify({
                'success': False,
                'message': 'Scene data not found'
            }), 404
        
        with open(scene_path, 'r') as f:
            scene_data = json.load(f)
        
        return jsonify({
            'success': True,
            'case_id': case_id,
            'scene_data': scene_data
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting scene: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting scene: {str(e)}'
        }), 500

@results_bp.route('/report/json/<case_id>', methods=['GET'])
def download_json_report(case_id):
    """
    Download JSON report for a case
    
    Response:
        - JSON report file
    """
    try:
        report_path = REPORTS_OUTPUT_DIR / case_id / 'evidence_report.json'
        
        if not report_path.exists():
            return jsonify({
                'success': False,
                'message': 'Report not found'
            }), 404
        
        return send_file(
            report_path,
            mimetype='application/json',
            as_attachment=True,
            download_name=f'case_{case_id}_report.json'
        )
    
    except Exception as e:
        logger.error(f"Error downloading JSON report: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error downloading report: {str(e)}'
        }), 500

@results_bp.route('/report/pdf/<case_id>', methods=['GET'])
def download_pdf_report(case_id):
    """
    Download PDF report for a case
    
    Response:
        - PDF report file
    """
    try:
        report_path = REPORTS_OUTPUT_DIR / case_id / 'evidence_report.pdf'
        
        if not report_path.exists():
            return jsonify({
                'success': False,
                'message': 'Report not found'
            }), 404
        
        return send_file(
            report_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'case_{case_id}_report.pdf'
        )
    
    except Exception as e:
        logger.error(f"Error downloading PDF report: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error downloading report: {str(e)}'
        }), 500

@results_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """
    Download a specific result file by name from the reports directory
    """
    try:
        file_path = REPORTS_OUTPUT_DIR / filename
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return jsonify({
                'success': False,
                'message': 'File not found'
            }), 404
            
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Error serving file {filename}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error serving file: {str(e)}'
        }), 500

@results_bp.route('/visualization/<case_id>', methods=['GET'])
def download_visualization(case_id):
    """
    Download 3D visualization file
    
    Response:
        - PLY visualization file
    """
    try:
        vis_path = RECONSTRUCTIONS_DIR / case_id / 'scene_visualization.ply'
        
        if not vis_path.exists():
            return jsonify({
                'success': False,
                'message': 'Visualization not found'
            }), 404
        
        return send_file(
            vis_path,
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=f'case_{case_id}_scene.ply'
        )
    
    except Exception as e:
        logger.error(f"Error downloading visualization: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error downloading visualization: {str(e)}'
        }), 500

@results_bp.route('/summary/<case_id>', methods=['GET'])
def get_case_summary(case_id):
    """
    Get summary of all results for a case
    
    Response:
        - success: Boolean
        - summary: Case summary
    """
    try:
        # Check what files exist
        report_json = REPORTS_OUTPUT_DIR / case_id / 'evidence_report.json'
        report_pdf = REPORTS_OUTPUT_DIR / case_id / 'evidence_report.pdf'
        scene_json = RECONSTRUCTIONS_DIR / case_id / 'scene.json'
        scene_vis = RECONSTRUCTIONS_DIR / case_id / 'scene_visualization.ply'
        
        summary = {
            'case_id': case_id,
            'available_results': {
                'json_report': report_json.exists(),
                'pdf_report': report_pdf.exists(),
                'scene_data': scene_json.exists(),
                'scene_visualization': scene_vis.exists()
            },
            'download_links': {}
        }
        
        if report_json.exists():
            summary['download_links']['json_report'] = f'/api/results/report/json/{case_id}'
        
        if report_pdf.exists():
            summary['download_links']['pdf_report'] = f'/api/results/report/pdf/{case_id}'
        
        if scene_vis.exists():
            summary['download_links']['visualization'] = f'/api/results/visualization/{case_id}'
        
        return jsonify({
            'success': True,
            'summary': summary
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting case summary: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error getting case summary: {str(e)}'
        }), 500

@results_bp.route('/annotated/<filename>', methods=['GET'])
def serve_annotated_image(filename):
    """
    Serve annotated image with detection boxes
    """
    try:
        image_path = ANNOTATIONS_DIR / filename
        
        if not image_path.exists():
            logger.error(f"Annotated image not found: {image_path}")
            return jsonify({
                'success': False,
                'message': 'Annotated image not found'
            }), 404
        
        logger.info(f"Serving annotated image: {image_path}")
        return send_file(
            image_path,
            mimetype='image/png',
            as_attachment=False
        )
    
    except Exception as e:
        logger.error(f"Error serving annotated image: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error serving image: {str(e)}'
        }), 500
