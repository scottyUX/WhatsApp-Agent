from typing import Dict, Any, List, Optional
from datetime import datetime
import base64
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import requests
from io import BytesIO

class ReportGenerationService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#58B8B8')
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#2C3E50')
        ))
        
        # Body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_LEFT
        ))
        
        # Highlight style
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            textColor=colors.HexColor('#E74C3C'),
            fontName='Helvetica-Bold'
        ))

    def generate_pdf_report(self, analysis_data: Dict[str, Any], patient_name: str = "Patient") -> bytes:
        """
        Generate a comprehensive PDF report from hair transplant analysis data
        
        Args:
            analysis_data: The analysis data from the image agent
            patient_name: Name of the patient
            
        Returns:
            PDF content as bytes
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Build the story (content)
        story = []
        
        # Title
        story.append(Paragraph("Hair Transplant Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # Patient info and timestamp
        story.append(Paragraph(f"<b>Patient:</b> {patient_name}", self.styles['CustomBody']))
        story.append(Paragraph(f"<b>Report Date:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.styles['CustomBody']))
        story.append(Paragraph(f"<b>Report ID:</b> {analysis_data.get('report_id', 'N/A')}", self.styles['CustomBody']))
        story.append(Spacer(1, 20))
        
        # Analysis Summary
        story.append(Paragraph("Analysis Summary", self.styles['CustomSubtitle']))
        
        analysis = analysis_data.get('analysis', {})
        if isinstance(analysis, dict):
            # Extract key metrics
            norwood_scale = analysis.get('norwood_scale', 'Not specified')
            graft_estimate = analysis.get('graft_estimate', {})
            cost_estimate = analysis.get('cost_estimate', {})
            
            # Create summary table
            summary_data = [
                ['Metric', 'Value'],
                ['Norwood Scale Classification', norwood_scale],
                ['Estimated Grafts Required', f"{graft_estimate.get('min', 'N/A')} - {graft_estimate.get('max', 'N/A')}"],
                ['Estimated Cost (Turkey)', f"${cost_estimate.get('min', 'N/A')} - ${cost_estimate.get('max', 'N/A')} {cost_estimate.get('currency', 'USD')}"],
                ['Procedure Type', analysis.get('procedure_type', 'FUE/DHI')],
                ['Expected Timeline', analysis.get('expected_timeline', '12-18 months')],
                ['Images Analyzed', str(analysis_data.get('images_analyzed', 0))]
            ]
            
            summary_table = Table(summary_data, colWidths=[2.5*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#58B8B8')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 20))
        
        # Detailed Analysis
        story.append(Paragraph("Detailed Analysis", self.styles['CustomSubtitle']))
        
        analysis_text = analysis.get('analysis', 'No detailed analysis available.')
        if isinstance(analysis_text, str):
            # Split long text into paragraphs
            paragraphs = analysis_text.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), self.styles['CustomBody']))
                    story.append(Spacer(1, 6))
        else:
            story.append(Paragraph("Detailed analysis not available in text format.", self.styles['CustomBody']))
        
        story.append(Spacer(1, 20))
        
        # Recommendations
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            story.append(Paragraph("Recommendations", self.styles['CustomSubtitle']))
            for i, rec in enumerate(recommendations, 1):
                story.append(Paragraph(f"{i}. {rec}", self.styles['CustomBody']))
            story.append(Spacer(1, 20))
        
        # Cost Breakdown
        if cost_estimate:
            story.append(Paragraph("Cost Breakdown", self.styles['CustomSubtitle']))
            
            cost_data = [
                ['Service', 'Cost Range (USD)'],
                ['Hair Transplant Procedure', f"${cost_estimate.get('min', 'N/A')} - ${cost_estimate.get('max', 'N/A')}"],
                ['All-inclusive Package', 'Included'],
                ['Accommodation (2-3 days)', 'Included'],
                ['Airport Transfers', 'Included'],
                ['Post-operative Care', 'Included'],
                ['Follow-up Consultations', 'Included']
            ]
            
            cost_table = Table(cost_data, colWidths=[3*inch, 2.5*inch])
            cost_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(cost_table)
            story.append(Spacer(1, 20))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("This report was generated by IstanbulMedic's AI-powered hair transplant analysis system.", 
                              self.styles['CustomBody']))
        story.append(Paragraph("For questions or to schedule a consultation, please contact our medical team.", 
                              self.styles['CustomBody']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_html_report(self, analysis_data: Dict[str, Any], patient_name: str = "Patient") -> str:
        """
        Generate an HTML report from hair transplant analysis data
        
        Args:
            analysis_data: The analysis data from the image agent
            patient_name: Name of the patient
            
        Returns:
            HTML content as string
        """
        analysis = analysis_data.get('analysis', {})
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Hair Transplant Analysis Report</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .header {{
                    text-align: center;
                    background: linear-gradient(135deg, #58B8B8, #4a9d9d);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5em;
                }}
                .patient-info {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .summary-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .summary-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .summary-card h3 {{
                    color: #58B8B8;
                    margin-top: 0;
                }}
                .metric {{
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    border-bottom: 1px solid #eee;
                }}
                .metric:last-child {{
                    border-bottom: none;
                }}
                .metric-value {{
                    font-weight: bold;
                    color: #2C3E50;
                }}
                .analysis-section {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .recommendations {{
                    background: #e8f5e8;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
                .recommendations ul {{
                    margin: 0;
                    padding-left: 20px;
                }}
                .footer {{
                    text-align: center;
                    color: #666;
                    font-size: 0.9em;
                    margin-top: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Hair Transplant Analysis Report</h1>
            </div>
            
            <div class="patient-info">
                <h2>Patient Information</h2>
                <p><strong>Patient:</strong> {patient_name}</p>
                <p><strong>Report Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                <p><strong>Report ID:</strong> {analysis_data.get('report_id', 'N/A')}</p>
            </div>
            
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>Classification</h3>
                    <div class="metric">
                        <span>Norwood Scale:</span>
                        <span class="metric-value">{analysis.get('norwood_scale', 'Not specified')}</span>
                    </div>
                    <div class="metric">
                        <span>Images Analyzed:</span>
                        <span class="metric-value">{analysis_data.get('images_analyzed', 0)}</span>
                    </div>
                </div>
                
                <div class="summary-card">
                    <h3>Graft Requirements</h3>
                    <div class="metric">
                        <span>Estimated Grafts:</span>
                        <span class="metric-value">{analysis.get('graft_estimate', {}).get('min', 'N/A')} - {analysis.get('graft_estimate', {}).get('max', 'N/A')}</span>
                    </div>
                    <div class="metric">
                        <span>Procedure Type:</span>
                        <span class="metric-value">{analysis.get('procedure_type', 'FUE/DHI')}</span>
                    </div>
                </div>
                
                <div class="summary-card">
                    <h3>Cost Estimate</h3>
                    <div class="metric">
                        <span>Price Range:</span>
                        <span class="metric-value">${analysis.get('cost_estimate', {}).get('min', 'N/A')} - ${analysis.get('cost_estimate', {}).get('max', 'N/A')} {analysis.get('cost_estimate', {}).get('currency', 'USD')}</span>
                    </div>
                    <div class="metric">
                        <span>Timeline:</span>
                        <span class="metric-value">{analysis.get('expected_timeline', '12-18 months')}</span>
                    </div>
                </div>
            </div>
            
            <div class="analysis-section">
                <h2>Detailed Analysis</h2>
                <p>{analysis.get('analysis', 'No detailed analysis available.')}</p>
            </div>
            
            <div class="recommendations">
                <h2>Recommendations</h2>
                <ul>
        """
        
        recommendations = analysis.get('recommendations', [])
        for rec in recommendations:
            html += f"<li>{rec}</li>"
        
        html += """
                </ul>
            </div>
            
            <div class="footer">
                <p>This report was generated by IstanbulMedic's AI-powered hair transplant analysis system.</p>
                <p>For questions or to schedule a consultation, please contact our medical team.</p>
            </div>
        </body>
        </html>
        """
        
        return html

# Create a singleton instance
report_service = ReportGenerationService()
