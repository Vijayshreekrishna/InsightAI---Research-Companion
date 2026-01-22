from PyPDF2 import PdfReader
import io

def extract_text_from_pdf(uploaded_file):
    if not uploaded_file:
        return ""
    file_bytes = uploaded_file.read()
    reader = PdfReader(io.BytesIO(file_bytes))
    text = []
    for i, page in enumerate(reader.pages):
        try:
            page_text = page.extract_text() or ""
            text.append(f"\n--- Page {i+1} ---\n{page_text}")
        except Exception:
            text.append(f"\n--- Page {i+1} ---\n")
    return "\n".join(text)
