# utils/paper_utils.py
import os
import json
from datetime import datetime
from fpdf import FPDF
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

HISTORY_FILE = "paper_history.json"

class PDF(FPDF):
    def header(self):
        # Optional Header can go here
        pass

    def footer(self):
        # Page numbering
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

def get_template_config(template_name):
    """Return styling configuration for different academic templates."""
    configs = {
        "IEEE": {
            "font_family": "Times",
            "title_size": 24,
            "section_size": 11,
            "body_size": 10,
            "columns": 2,
            "line_spacing": 1.0,
        },
        "ACM": {
            "font_family": "Helvetica",
            "title_size": 18,
            "section_size": 12,
            "body_size": 9,
            "columns": 1,
            "line_spacing": 1.15,
        },
        "Springer": {
            "font_family": "Times",
            "title_size": 16,
            "section_size": 11,
            "body_size": 10,
            "columns": 1,
            "line_spacing": 1.2,
        },
        "Generic University": {
            "font_family": "Arial",
            "title_size": 16,
            "section_size": 14,
            "body_size": 12,
            "columns": 1,
            "line_spacing": 1.5,
        }
    }
    return configs.get(template_name, configs["Generic University"])

def export_as_pdf(paper_data, template_name="Generic University", font_style="Serif"):
    """Export formatted paper as PDF using fpdf2."""
    config = get_template_config(template_name)
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Font Mapping for fpdf2
    font_map = {
        "Serif": "Times",
        "Sans-Serif": "Helvetica",
        "Monospace": "Courier"
    }
    pdf_font = font_map.get(font_style, "Times")

    # Title
    pdf.set_font(pdf_font, 'B', config["title_size"])
    pdf.cell(0, 20, paper_data.get("title", "Research Paper"), ln=True, align='C')
    pdf.ln(5)
    
    sections = [
        ("Abstract", "abstract"),
        ("Keywords", "keywords"),
        ("Introduction", "introduction"),
        ("Literature Review", "lit_review"),
        ("Methodology", "methodology"),
        ("Results & Discussion", "results"),
        ("Conclusion", "conclusion"),
        ("Future Scope", "future_scope"),
        ("References", "references"),
    ]
    
    for label, key in sections:
        content = paper_data.get(key, "")
        if not content: continue
        
        # Section Header
        pdf.set_font(pdf_font, 'B', config["section_size"])
        pdf.set_fill_color(240, 240, 240) # Subtle grey background for headers
        pdf.cell(0, 10, label.upper(), ln=True, fill=True)
        pdf.ln(2)
        
        # Section Content
        pdf.set_font(pdf_font, '', config["body_size"])
        if isinstance(content, list):
            content = ", ".join(content)
        
        # multi_cell is robust in fpdf2
        pdf.multi_cell(0, 7, str(content), align='J')
        pdf.ln(4)
        
    return bytes(pdf.output()) # Convert bytearray to bytes for Streamlit compatibility

def export_as_docx(paper_data, template_name="Generic University", font_style="Serif"):
    """Export formatted paper as DOCX using python-docx."""
    config = get_template_config(template_name)
    doc = Document()
    
    # Title
    title_heading = doc.add_heading(paper_data.get("title", "Research Paper"), 0)
    title_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    font_name = "Times New Roman" if font_style == "Serif" else "Arial" if font_style == "Sans-Serif" else "Courier New"
    
    sections = [
        ("Abstract", "abstract"),
        ("Keywords", "keywords"),
        ("Introduction", "introduction"),
        ("Literature Review", "lit_review"),
        ("Methodology", "methodology"),
        ("Results & Discussion", "results"),
        ("Conclusion", "conclusion"),
        ("Future Scope", "future_scope"),
        ("References", "references"),
    ]
    
    for label, key in sections:
        content = paper_data.get(key, "")
        if not content: continue
        
        h = doc.add_heading(label, level=1)
        for run in h.runs:
            run.font.name = font_name
            run.font.size = Pt(config["section_size"])

        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if isinstance(content, list):
            content = ", ".join(content)
        run = p.add_run(str(content))
        run.font.name = font_name
        run.font.size = Pt(config["body_size"])
        
    from io import BytesIO
    docx_io = BytesIO()
    doc.save(docx_io)
    return docx_io.getvalue()

# History Management
def save_to_history(paper_data):
    history = load_history()
    paper_data["id"] = datetime.now().strftime("%Y%m%d_%H%M%S")
    paper_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    history.append(paper_data)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)
    return paper_data["id"]

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def delete_from_history(paper_id):
    history = load_history()
    new_history = [p for p in history if p.get("id") != paper_id]
    with open(HISTORY_FILE, "w") as f:
        json.dump(new_history, f, indent=4)
    return True
