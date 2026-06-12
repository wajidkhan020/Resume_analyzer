"""
Resume PDF Parser
Extracts readable text from uploaded PDF resumes using PyPDF2.
"""

import PyPDF2
import io
import re


def extract_text_from_pdf(uploaded_file) -> dict:
    """
    Extract all text from a PDF file.

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        dict with 'success', 'text', 'pages', and 'error' keys
    """
    try:
        # Read PDF bytes
        pdf_bytes = uploaded_file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))

        total_pages = len(pdf_reader.pages)
        full_text = []

        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    full_text.append(page_text.strip())
            except Exception as e:
                full_text.append(f"[Page {page_num + 1} could not be read]")

        combined_text = "\n\n".join(full_text)
        combined_text = clean_extracted_text(combined_text)

        if not combined_text.strip():
            return {
                "success": False,
                "text": "",
                "pages": total_pages,
                "error": "No readable text found. PDF may be image-based or encrypted.",
            }

        return {
            "success": True,
            "text": combined_text,
            "pages": total_pages,
            "error": None,
        }

    except Exception as e:
        return {
            "success": False,
            "text": "",
            "pages": 0,
            "error": f"Failed to parse PDF: {str(e)}",
        }


def clean_extracted_text(text: str) -> str:
    """Clean and normalize extracted PDF text."""
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {3,}', ' ', text)
    # Remove non-printable characters except newlines and tabs
    text = re.sub(r'[^\x20-\x7E\n\t]', ' ', text)
    return text.strip()


def validate_pdf(uploaded_file) -> dict:
    """
    Validate uploaded file is a proper PDF within size limits.

    Returns:
        dict with 'valid' bool and 'error' message
    """
    MAX_SIZE_MB = 10

    if uploaded_file is None:
        return {"valid": False, "error": "No file uploaded."}

    if not uploaded_file.name.lower().endswith(".pdf"):
        return {"valid": False, "error": "Only PDF files are supported."}

    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_SIZE_MB:
        return {
            "valid": False,
            "error": f"File too large ({file_size_mb:.1f} MB). Maximum is {MAX_SIZE_MB} MB.",
        }

    return {"valid": True, "error": None}
