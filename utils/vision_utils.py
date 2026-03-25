# utils/vision_utils.py
"""
Visual Q&A utility – Groq-compatible page inspector.
Uses pdfplumber for rich text/table extraction per page,
and pypdfium2 for rendering a page preview image.
"""

import io
from typing import Optional, Tuple
from PIL import Image


def extract_page_content(pdf_bytes: bytes, page_num: int) -> dict:
    """
    Extract structured content (text + tables) from a specific PDF page.
    
    Args:
        pdf_bytes: Raw bytes of the PDF file
        page_num: 1-indexed page number
    
    Returns:
        dict with keys: 'text', 'tables', 'combined_markdown', 'page_num'
    """
    try:
        import pdfplumber

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            if page_num < 1 or page_num > len(pdf.pages):
                return {
                    "error": f"Page {page_num} does not exist. PDF has {len(pdf.pages)} pages.",
                    "page_num": page_num,
                }

            page = pdf.pages[page_num - 1]

            # Extract plain text
            raw_text = page.extract_text() or ""

            # Extract tables and format as markdown
            tables_md = []
            tables = page.extract_tables()
            for t_idx, table in enumerate(tables):
                if not table:
                    continue
                md_rows = []
                for row_idx, row in enumerate(table):
                    cells = [str(c).strip() if c else "" for c in row]
                    md_rows.append("| " + " | ".join(cells) + " |")
                    if row_idx == 0:
                        md_rows.append("| " + " | ".join(["---"] * len(cells)) + " |")
                tables_md.append(f"**Table {t_idx + 1}:**\n" + "\n".join(md_rows))

            combined = f"=== Page {page_num} Text ===\n{raw_text}"
            if tables_md:
                combined += "\n\n=== Extracted Tables ===\n" + "\n\n".join(tables_md)

            return {
                "text": raw_text,
                "tables": tables_md,
                "combined_markdown": combined,
                "page_num": page_num,
                "total_pages": len(pdf.pages),
            }

    except Exception as e:
        return {"error": str(e), "page_num": page_num}


def render_page_preview(pdf_bytes: bytes, page_num: int, scale: float = 1.5) -> Optional[Image.Image]:
    """
    Render a PDF page as a PIL Image for display purposes only (not sent to AI).
    
    Args:
        pdf_bytes: Raw bytes of the PDF file
        page_num: 1-indexed page number
        scale: Render scale factor (higher = better quality)
    
    Returns:
        PIL Image or None on failure
    """
    try:
        import pypdfium2 as pdfium

        pdf = pdfium.PdfDocument(pdf_bytes)
        if page_num < 1 or page_num > len(pdf):
            return None

        page = pdf[page_num - 1]
        bitmap = page.render(scale=scale, rotation=0)
        pil_image = bitmap.to_pil()
        return pil_image

    except Exception:
        return None


def get_page_count(pdf_bytes: bytes) -> int:
    """Return total number of pages in a PDF."""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            return len(pdf.pages)
    except Exception:
        return 0
