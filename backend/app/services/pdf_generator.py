from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import os
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class PDFGenerator:
    def __init__(self, storage_path: str = "./storage/pdfs"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Setup styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for CV."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CVTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.darkblue,
            borderWidth=1,
            borderColor=colors.darkblue,
            borderPadding=5
        ))
        
        # Contact info style
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=15
        ))
        
        # Experience item style
        self.styles.add(ParagraphStyle(
            name='ExperienceItem',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceBefore=8,
            spaceAfter=8,
            alignment=TA_JUSTIFY
        ))

    def generate_cv_pdf(self, cv_data: Dict[str, Any], user_data: Dict[str, Any]) -> str:
        """Generate PDF from CV data."""
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cv_{user_data.get('username', 'user')}_{timestamp}.pdf"
            filepath = os.path.join(self.storage_path, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build content
            story = []
            
            # Parse CV text and build structured content
            cv_sections = self._parse_cv_text(cv_data.get('original_text', ''))
            
            # Add title (user's name if available)
            if 'name' in cv_sections:
                story.append(Paragraph(cv_sections['name'], self.styles['CVTitle']))
            else:
                story.append(Paragraph(user_data.get('full_name', 'Curriculum Vitae'), self.styles['CVTitle']))
            
            # Add contact information
            contact_info = self._build_contact_info(cv_sections, user_data)
            if contact_info:
                story.append(Paragraph(contact_info, self.styles['ContactInfo']))
            
            story.append(Spacer(1, 20))
            
            # Add sections
            section_order = ['objetivo', 'experiencia', 'educacao', 'competencias', 'projetos', 'idiomas']
            
            for section_key in section_order:
                if section_key in cv_sections and cv_sections[section_key]:
                    section_title = self._get_section_title(section_key)
                    story.append(Paragraph(section_title, self.styles['SectionHeader']))
                    
                    # Add section content
                    content = cv_sections[section_key]
                    if isinstance(content, list):
                        for item in content:
                            story.append(Paragraph(f"• {item}", self.styles['ExperienceItem']))
                    else:
                        story.append(Paragraph(content, self.styles['ExperienceItem']))
                    
                    story.append(Spacer(1, 10))
            
            # Add any remaining content
            if 'outros' in cv_sections:
                story.append(Paragraph("Informações Adicionais", self.styles['SectionHeader']))
                story.append(Paragraph(cv_sections['outros'], self.styles['ExperienceItem']))
            
            # Add footer with generation info
            story.append(Spacer(1, 30))
            footer_text = f"CV gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} | CV Maker Inteligente"
            story.append(Paragraph(footer_text, self.styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF generated successfully: {filepath}")
            return filename
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise

    def _parse_cv_text(self, cv_text: str) -> Dict[str, Any]:
        """Parse CV text into structured sections."""
        sections = {}
        current_section = 'outros'
        
        lines = cv_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['nome:', 'name:']):
                sections['name'] = line.split(':', 1)[1].strip() if ':' in line else line
            elif any(keyword in line_lower for keyword in ['email:', 'e-mail:']):
                sections['email'] = line.split(':', 1)[1].strip() if ':' in line else line
            elif any(keyword in line_lower for keyword in ['telefone:', 'telemóvel:', 'phone:']):
                sections['telefone'] = line.split(':', 1)[1].strip() if ':' in line else line
            elif any(keyword in line_lower for keyword in ['objetivo', 'objectivo', 'summary', 'resumo']):
                current_section = 'objetivo'
                sections[current_section] = []
            elif any(keyword in line_lower for keyword in ['experiência', 'experiencia', 'experience', 'trabalho']):
                current_section = 'experiencia'
                sections[current_section] = []
            elif any(keyword in line_lower for keyword in ['educação', 'educacao', 'education', 'formação', 'formacao']):
                current_section = 'educacao'
                sections[current_section] = []
            elif any(keyword in line_lower for keyword in ['competências', 'competencias', 'skills', 'habilidades']):
                current_section = 'competencias'
                sections[current_section] = []
            elif any(keyword in line_lower for keyword in ['projetos', 'projects', 'projectos']):
                current_section = 'projetos'
                sections[current_section] = []
            elif any(keyword in line_lower for keyword in ['idiomas', 'languages', 'línguas', 'linguas']):
                current_section = 'idiomas'
                sections[current_section] = []
            else:
                # Add content to current section
                if current_section not in sections:
                    sections[current_section] = []
                
                if isinstance(sections[current_section], list):
                    sections[current_section].append(line)
                else:
                    sections[current_section] = line
        
        # Convert single-item lists to strings for some sections
        for section in ['objetivo', 'outros']:
            if section in sections and isinstance(sections[section], list):
                sections[section] = ' '.join(sections[section])
        
        return sections

    def _build_contact_info(self, cv_sections: Dict, user_data: Dict) -> str:
        """Build contact information string."""
        contact_parts = []
        
        if 'email' in cv_sections:
            contact_parts.append(cv_sections['email'])
        elif user_data.get('email'):
            contact_parts.append(user_data['email'])
        
        if 'telefone' in cv_sections:
            contact_parts.append(cv_sections['telefone'])
        
        return ' | '.join(contact_parts)

    def _get_section_title(self, section_key: str) -> str:
        """Get formatted section title."""
        titles = {
            'objetivo': 'Objetivo Profissional',
            'experiencia': 'Experiência Profissional',
            'educacao': 'Educação',
            'competencias': 'Competências',
            'projetos': 'Projetos',
            'idiomas': 'Idiomas',
            'outros': 'Informações Adicionais'
        }
        return titles.get(section_key, section_key.title())

    def generate_analysis_report(self, cv_data: Dict[str, Any], analysis_result: Dict[str, Any]) -> str:
        """Generate PDF report with CV analysis and suggestions."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_report_{timestamp}.pdf"
            filepath = os.path.join(self.storage_path, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            story = []
            
            # Title
            story.append(Paragraph("Relatório de Análise do CV", self.styles['CVTitle']))
            story.append(Spacer(1, 20))
            
            # Score
            score = analysis_result.get('analysis_score', 0)
            score_color = colors.green if score >= 70 else colors.orange if score >= 50 else colors.red
            score_style = ParagraphStyle(
                name='Score',
                parent=self.styles['Normal'],
                fontSize=16,
                textColor=score_color,
                alignment=TA_CENTER
            )
            story.append(Paragraph(f"Pontuação: {score}/100", score_style))
            story.append(Spacer(1, 20))
            
            # Suggestions
            suggestions = analysis_result.get('suggestions', [])
            if suggestions:
                story.append(Paragraph("Sugestões de Melhoria", self.styles['SectionHeader']))
                
                for i, suggestion in enumerate(suggestions, 1):
                    priority_color = colors.red if suggestion['priority'] == 'high' else colors.orange if suggestion['priority'] == 'medium' else colors.blue
                    
                    story.append(Paragraph(f"{i}. {suggestion['title']}", self.styles['Heading3']))
                    story.append(Paragraph(suggestion['description'], self.styles['Normal']))
                    
                    if suggestion.get('examples'):
                        story.append(Paragraph("Exemplos:", self.styles['Normal']))
                        for example in suggestion['examples']:
                            story.append(Paragraph(f"• {example}", self.styles['Normal']))
                    
                    story.append(Spacer(1, 10))
            
            # Keywords
            keywords = analysis_result.get('keywords', [])
            if keywords:
                story.append(Paragraph("Palavras-chave Identificadas", self.styles['SectionHeader']))
                keywords_text = ', '.join(keywords[:15])  # Show first 15 keywords
                story.append(Paragraph(keywords_text, self.styles['Normal']))
            
            doc.build(story)
            logger.info(f"Analysis report generated: {filepath}")
            return filename
            
        except Exception as e:
            logger.error(f"Error generating analysis report: {str(e)}")
            raise

    def get_pdf_path(self, filename: str) -> str:
        """Get full path to PDF file."""
        return os.path.join(self.storage_path, filename)

    def delete_pdf(self, filename: str) -> bool:
        """Delete PDF file."""
        try:
            filepath = self.get_pdf_path(filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting PDF {filename}: {str(e)}")
            return False
