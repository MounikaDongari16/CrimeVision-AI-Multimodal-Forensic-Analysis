"""
Report Generation Service - Creates PDF and JSON reports
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from config import REPORTS_OUTPUT_DIR, REPORT_CONFIG
from utils.logger import setup_logger

logger = setup_logger('report_service')

class ReportService:
    """Service for generating evidence reports"""
    
    def generate_report(
        self,
        case_id: str,
        vision_results: List[Dict],
        audio_results: List[Dict],
        text_results: List[Dict],
        fusion_results: Dict,
        timeline_results: Dict,
        reconstruction_results: Dict
    ) -> Dict[str, Any]:
        """
        Generate comprehensive evidence report
        
        Args:
            case_id: Case identifier
            vision_results: Vision processing results
            audio_results: Audio processing results
            text_results: Text processing results
            fusion_results: Fusion results
            timeline_results: Timeline results
            reconstruction_results: 3D reconstruction results
        
        Returns:
            Dictionary with report paths
        """
        try:
            logger.info(f"Generating report for case: {case_id}")
            
            # Compile report data
            report_data = self._compile_report_data(
                case_id,
                vision_results,
                audio_results,
                text_results,
                fusion_results,
                timeline_results,
                reconstruction_results
            )
            
            # Generate JSON report
            json_path = self._generate_json_report(report_data, case_id)
            
            # Generate PDF report
            pdf_path = self._generate_pdf_report(report_data, case_id)
            
            return {
                'case_id': case_id,
                'json_report': json_path,
                'pdf_report': pdf_path,
                'generated_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {'error': str(e)}
    
    def _compile_report_data(
        self,
        case_id: str,
        vision_results: List[Dict],
        audio_results: List[Dict],
        text_results: List[Dict],
        fusion_results: Dict,
        timeline_results: Dict,
        reconstruction_results: Dict
    ) -> Dict[str, Any]:
        """Compile enriched data into structured report"""
        
        # Audio metrics aggregation
        audio_scenarios = []
        audio_facts = {}
        for ar in audio_results:
            if 'scenarios' in ar:
                audio_scenarios.extend(ar['scenarios'])
            if 'facts' in ar:
                for k, v in ar['facts'].items():
                    if k not in audio_facts: audio_facts[k] = []
                    audio_facts[k].extend(v)

        report_data = {
            'case_id': case_id,
            'generated_at': datetime.now().isoformat(),
            'evidence_summary': {
                'location': vision_results[0].get('summary', {}).get('location', 'Unknown') if vision_results else 'Unknown',
                'people_count': sum(r.get('summary', {}).get('people_count', 0) for r in vision_results),
                'weapons': list(set([w for r in vision_results for w in r.get('summary', {}).get('weapon_types', [])])),
                'observations': list(set([o for r in vision_results for o in r.get('summary', {}).get('key_observations', [])])),
                'scenarios': list(set(audio_scenarios))[:3]
            },
            'vision_analysis': self._summarize_vision_results(vision_results),
            'audio_analysis': self._summarize_audio_results(audio_results),
            'text_analysis': self._summarize_text_results(text_results),
            'timeline': timeline_results,
            'recon_data': reconstruction_results
        }
        
        return report_data

    def _generate_pdf_report(self, report_data: Dict, case_id: str) -> str:
        """Generate Enriched PDF report"""
        output_dir = REPORTS_OUTPUT_DIR / case_id
        output_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = output_dir / 'evidence_report.pdf'
        
        doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Styles
        title_style = ParagraphStyle('Title', fontSize=22, spaceAfter=20, textColor=colors.navy)
        section_style = ParagraphStyle('Section', fontSize=14, spaceAfter=10, textColor=colors.darkred, fontName='Helvetica-Bold')
        normal_style = styles['Normal']
        
        story.append(Paragraph(f"Crime Scene Reconstruction Report", title_style))
        story.append(Paragraph(f"<b>Case ID:</b> {case_id} | <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # --- ENRICHED SUMMARY SECTION ---
        story.append(Paragraph("AI-Generated Evidence Summary", section_style))
        summary = report_data['evidence_summary']
        
        data = [
            ["Metric", "Finding"],
            ["Scene Location", summary['location'].capitalize()],
            ["Total People Count", str(summary['people_count'])],
            ["Identified Weaponry", ", ".join(summary['weapons']) if summary['weapons'] else "None detected"]
        ]
        t = Table(data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.lightgrey),
            ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
        ]))
        story.append(t)
        story.append(Spacer(1, 0.15*inch))
        
        # Key Observations
        story.append(Paragraph("<b>Key Observations:</b>", normal_style))
        for obs in summary['observations']:
            story.append(Paragraph(f"• {obs}", normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # AI Scenarios
        if summary['scenarios']:
            story.append(Paragraph("AI-Inferred Event Scenarios", section_style))
            for i, scenario in enumerate(summary['scenarios'], 1):
                story.append(Paragraph(f"<b>Option {i}:</b> {scenario}", normal_style))
                story.append(Spacer(1, 0.1*inch))
        
        # --- ORIGINAL ANALYSIS SECTIONS (Brief) ---
        story.append(PageBreak())
        story.append(Paragraph("Technical Modality Analysis", section_style))
        story.append(Paragraph(f"Vision: {report_data['vision_analysis']['total_detections']} detections found.", normal_style))
        story.append(Paragraph(f"Audio: {report_data['audio_analysis']['total_files']} files transcribed.", normal_style))
        
        # Build PDF
        doc.build(story)
        logger.info(f"Generated Enriched PDF: {pdf_path}")
        return str(pdf_path)

    def _summarize_vision_results(self, vision_results: List[Dict]) -> Dict:
        all_detections = []
        for result in vision_results:
            all_detections.extend(result.get('detections', []))
        return {
            'total_detections': len(all_detections),
            'detection_breakdown': {}, # Simplified for now
            'high_confidence_detections': 0
        }
    
    def _summarize_audio_results(self, audio_results: List[Dict]) -> Dict:
        return {'total_files': len(audio_results)}
    
    def _summarize_text_results(self, text_results: List[Dict]) -> Dict:
        return {'total_reports': len(text_results)}

    def _generate_json_report(self, report_data: Dict, case_id: str) -> str:
        output_dir = REPORTS_OUTPUT_DIR / case_id
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / 'evidence_report.json'
        with open(json_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        return str(json_path)

# Create service instance
report_service = ReportService()

# Create service instance
report_service = ReportService()
