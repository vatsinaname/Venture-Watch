import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import markdown
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch

from startup_agent.config import DATA_DIR

class PDFReportGenerator:
    """
    Utility for generating PDF reports from startup data
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        # Add custom styles
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#4285f4')
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.gray
        ))
        self.styles.add(ParagraphStyle(
            name='Tag',
            parent=self.styles['BodyText'],
            fontSize=8,
            textColor=colors.white,
            backColor=colors.HexColor('#4285f4'),
            borderPadding=5,
            spaceAfter=5
        ))
    
    def _create_tag_table(self, tags: List[str]) -> Table:
        """Create a table of tag elements"""
        if not tags:
            return Paragraph("None", self.styles["BodyText"])
        
        # Create tags as paragraphs with special styling
        tag_elements = [Paragraph(tag, self.styles["Tag"]) for tag in tags]
        
        # Create a table with 3 columns and as many rows as needed
        max_cols = 3
        rows = []
        current_row = []
        
        for tag in tag_elements:
            current_row.append(tag)
            if len(current_row) == max_cols:
                rows.append(current_row)
                current_row = []
        
        # Add the last row if it has any elements
        if current_row:
            # Pad with empty cells
            while len(current_row) < max_cols:
                current_row.append("")
            rows.append(current_row)
        
        if not rows:
            return Paragraph("None", self.styles["BodyText"])
        
        # Create the table
        table = Table(rows)
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0, colors.white),
        ]))
        
        return table
    
    def generate_pdf_report(self, startup_data: List[Dict[str, Any]], output_path: Optional[Path] = None) -> Path:
        """
        Generate a PDF report from analyzed startup data
        
        Args:
            startup_data: List of startup dictionaries with analysis data
            output_path: Optional path to save the PDF, defaults to data directory
            
        Returns:
            Path to the generated PDF
        """
        if not output_path:
            timestamp = datetime.datetime.now().strftime("%Y%m%d")
            output_path = DATA_DIR / f"startup_report_{timestamp}.pdf"
        
        # Create the PDF document
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # List to hold the flowable elements
        elements = []
        
        # Add title
        title = Paragraph("Startup Opportunity Report", self.styles["Title"])
        subtitle = Paragraph(f"Generated on {datetime.datetime.now().strftime('%B %d, %Y')}", self.styles["Italic"])
        elements.append(title)
        elements.append(subtitle)
        elements.append(Spacer(1, 0.25*inch))
        
        # Add description
        intro = Paragraph(f"Here are {len(startup_data)} recently funded startups that match your interests:", self.styles["BodyText"])
        elements.append(intro)
        elements.append(Spacer(1, 0.25*inch))
        
        # Add each startup
        for company in startup_data:
            # Company name and funding
            elements.append(Paragraph(company.get("company_name", "Unknown Company"), self.styles["CompanyName"]))
            funding_text = f"{company.get('funding_round', 'Unknown')} - {company.get('funding_amount', 0)} {company.get('funding_currency', 'USD')}"
            elements.append(Paragraph(funding_text, self.styles["Italic"]))
            elements.append(Spacer(1, 0.1*inch))
            
            # Location
            elements.append(Paragraph("📍 Location:", self.styles["SectionHeader"]))
            elements.append(Paragraph(company.get("location", "Unknown"), self.styles["BodyText"]))
            elements.append(Spacer(1, 0.1*inch))
            
            # Description
            elements.append(Paragraph("🔍 Description:", self.styles["SectionHeader"]))
            elements.append(Paragraph(company.get("description", "No description available"), self.styles["BodyText"]))
            elements.append(Spacer(1, 0.1*inch))
            
            # Website
            elements.append(Paragraph("🔗 Website:", self.styles["SectionHeader"]))
            elements.append(Paragraph(f"<a href='{company.get('website', '#')}'>{company.get('website', 'None')}</a>", self.styles["BodyText"]))
            elements.append(Spacer(1, 0.1*inch))
            
            # Categories
            elements.append(Paragraph("🧩 Categories:", self.styles["SectionHeader"]))
            elements.append(self._create_tag_table(company.get("categories", [])))
            elements.append(Spacer(1, 0.1*inch))
            
            # Tech Stack
            elements.append(Paragraph("💻 Likely Tech Stack:", self.styles["SectionHeader"]))
            elements.append(self._create_tag_table(company.get("tech_stack", [])))
            elements.append(Spacer(1, 0.1*inch))
            
            # Hiring Needs
            elements.append(Paragraph("👥 Potential Hiring Needs:", self.styles["SectionHeader"]))
            elements.append(self._create_tag_table(company.get("hiring_needs", [])))
            elements.append(Spacer(1, 0.1*inch))
            
            # Product Focus
            elements.append(Paragraph("🎯 Product Focus:", self.styles["SectionHeader"]))
            elements.append(Paragraph(company.get("product_focus", "Unknown"), self.styles["BodyText"]))
            
            # Add a page break between companies (except the last one)
            elements.append(Spacer(1, 0.5*inch))
        
        # Build the PDF
        doc.build(elements)
        
        # Save the PDF
        with open(output_path, "wb") as f:
            f.write(buffer.getvalue())
        
        return output_path
    
    def generate_from_latest(self) -> Optional[Path]:
        """
        Generate a PDF report from the most recent analyzed startup data
        
        Returns:
            Path to the generated PDF or None if no data found
        """
        # Find the most recent analyzed data file
        data_files = list(DATA_DIR.glob("funding_data_*_analyzed.json"))
        if not data_files:
            print("No analyzed startup data files found")
            return None
            
        # Sort by modification time (most recent first)
        most_recent_file = max(data_files, key=os.path.getmtime)
        
        print(f"Generating PDF report from {most_recent_file}...")
        
        # Load the data
        try:
            with open(most_recent_file, 'r', encoding='utf-8') as f:
                startup_data = json.load(f)
        except Exception as e:
            print(f"Error loading analyzed startup data: {e}")
            return None
        
        # Generate the PDF
        return self.generate_pdf_report(startup_data)


if __name__ == "__main__":
    # Test the PDF generation
    generator = PDFReportGenerator()
    pdf_path = generator.generate_from_latest()
    if pdf_path:
        print(f"PDF report generated at {pdf_path}") 