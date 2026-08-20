import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Line

class PDFGenerator:
    """Utility class for generating PDF Crime Scene Reports"""
    
    def __init__(self, output_Dir):
        self.output_dir = output_Dir
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
    def _create_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.darkblue,
            alignment=1, # Center
            spaceAfter=30
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.darkblue,
            spaceBefore=20,
            spaceAfter=10,
            borderPadding=(0, 0, 5, 0),
            borderColor=colors.gray,
            borderWidth=1
        ))

        self.styles.add(ParagraphStyle(
            name='FactLabel',
            fontSize=10,
            fontName='Helvetica-Bold',
            textColor=colors.black
        ))
        
        self.styles.add(ParagraphStyle(
            name='FactValue',
            fontSize=10,
            fontName='Helvetica',
            textColor=colors.black
        ))

    def generate_report(self, case_id, image_path, facts, scenarios, output_filename=None):
        """
        Generate a PDF report for a specific case with optimized images for speed
        """
        if not output_filename:
            output_filename = f"Crime_Scene_Report_{case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
        output_path = os.path.join(self.output_dir, output_filename)
        
        doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        story = []
        
        # 1. Header
        story.append(Paragraph("Crime Scene Analysis Report", self.styles['ReportTitle']))
        story.append(Paragraph(f"Case ID: {case_id}", self.styles['Normal']))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal']))
        story.append(Spacer(1, 12))
        
        # 2. Optimized Image Thumbnail
        temp_thumb = None
        if image_path and os.path.exists(image_path):
            try:
                from PIL import Image as PILImage
                from config import TEMP_DIR
                
                # Create a lightweight thumbnail for the PDF to speed up generation
                original_img = PILImage.open(image_path)
                # target width ~600px is perfect for A4 PDF and very fast to process
                w, h = original_img.size
                ratio = 600 / float(w)
                new_size = (600, int(h * ratio))
                
                thumb_path = TEMP_DIR / f"thumb_{case_id}_{os.path.basename(image_path)}"
                original_img.resize(new_size, PILImage.LANCZOS).save(thumb_path, "JPEG", quality=85)
                temp_thumb = str(thumb_path)
                
                img = Image(temp_thumb, width=5.5*inch, height=(5.5*inch * h / w))
                img.hAlign = 'CENTER'
                story.append(img)
                story.append(Spacer(1, 20))
            except Exception as e:
                # Fallback to original if resizing fails
                img = Image(image_path, width=4*inch, height=3*inch)
                img.hAlign = 'CENTER'
                story.append(img)
            
        # 3. Vision Analysis Summary
        story.append(Paragraph("Vision Analysis Summary", self.styles['SectionHeader']))
        
        # Create Main Facts Table
        data = [
            ['Category', 'Findings']
        ]
        
        if facts.get('one_line_description'):
             data.append(['Visual Summary', Paragraph(str(facts['one_line_description']), self.styles['FactValue'])])
             
        if facts.get('location'):
            data.append(['Scene Location', Paragraph(str(facts['location']).title(), self.styles['FactValue'])])
            
        if facts.get('objects_detected'):
            # Convert list to string safely
            objs = ", ".join(facts['objects_detected']) if isinstance(facts['objects_detected'], list) else str(facts['objects_detected'])
            data.append(['Objects Detected', Paragraph(objs, self.styles['FactValue'])])
            
        if facts.get('persons'):
             p_info = facts['persons']
             desc = f"Count: {p_info.get('count',0)}"
             if p_info.get('description'):
                 desc += f" ({', '.join(p_info['description'])})"
             data.append(['Persons Detected', Paragraph(desc, self.styles['FactValue'])])
             
        if facts.get('weapons'):
            weaps = ", ".join(facts['weapons']) if facts['weapons'] else "None detected"
            data.append(['Weapons', Paragraph(str(weaps), self.styles['FactValue'])])
            
        if facts.get('actions'):
            acts = ", ".join(facts['actions']) if facts['actions'] else "No specific actions"
            data.append(['Actions', Paragraph(str(acts), self.styles['FactValue'])])
            
        table = Table(data, colWidths=[1.5*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('GRID', (0,0), (-1,-1), 1, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # 4. Scenarios
        if scenarios:
            story.append(Paragraph("Possible Scenarios", self.styles['SectionHeader']))
            for idx, scen in enumerate(scenarios, 1):
                story.append(Paragraph(f"<b>Scenario {idx}:</b> {scen}", self.styles['Normal']))
                story.append(Spacer(1, 8))
                
        # 5. Footer
        story.append(Spacer(1, 40))
        story.append(Paragraph("Generated by AI Crime Scene Reconstruction System", self.styles['Italic']))
        
        doc.build(story)
        
        # Cleanup temporary thumbnail
        if temp_thumb and os.path.exists(temp_thumb):
            try:
                os.remove(temp_thumb)
            except:
                pass
                
        return output_filename
