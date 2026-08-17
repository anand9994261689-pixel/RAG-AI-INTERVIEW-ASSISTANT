import io
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extracts all text from a PDF file given its bytes.
    """
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error parsing PDF file: {str(e)}")
