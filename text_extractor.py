import pdfplumber
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
import os
import platform
import shutil

# Minimum character threshold to consider extraction successful.
# Scanned PDFs often return empty strings or a few stray characters.
MIN_TEXT_LENGTH = 50


def _configure_tesseract():
    """
    Auto-detect and configure the Tesseract executable path.
    On Windows, Tesseract is often installed but not added to PATH.
    On Linux (e.g., Streamlit Cloud), it's typically available via apt.
    """
    import pytesseract

    # If tesseract is already in PATH, nothing to do
    if shutil.which("tesseract"):
        return True

    # Common Windows install locations
    if platform.system() == "Windows":
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expanduser(r"~\AppData\Local\Tesseract-OCR\tesseract.exe"),
        ]
        for path in common_paths:
            if os.path.isfile(path):
                pytesseract.pytesseract.tesseract_cmd = path
                return True

    return False


def _extract_with_pdfplumber(file_bytes):
    """Extract text from a digitally-created PDF using pdfplumber."""
    text = ""
    file_bytes.seek(0)
    with pdfplumber.open(file_bytes) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text


def _extract_with_fitz(file_bytes):
    """Extract text from a PDF using PyMuPDF's built-in text extraction."""
    file_bytes.seek(0)
    raw = file_bytes.read()
    file_bytes.seek(0)

    doc = fitz.open(stream=raw, filetype="pdf")
    text = ""
    for page in doc:
        page_text = page.get_text("text")
        if page_text:
            text += page_text
    doc.close()
    return text


def _extract_with_ocr(file_bytes):
    """Extract text from a scanned/image-based PDF using Tesseract OCR."""
    import pytesseract

    file_bytes.seek(0)
    raw = file_bytes.read()
    file_bytes.seek(0)

    doc = fitz.open(stream=raw, filetype="pdf")
    text = ""
    for page in doc:
        # Render page to a pixmap (image) at 300 DPI for good OCR quality
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        page_text = pytesseract.image_to_string(img)
        if page_text:
            text += page_text
    doc.close()
    return text


def _is_tesseract_available():
    """Check if Tesseract OCR is installed and accessible."""
    try:
        # First, try to auto-configure the path
        _configure_tesseract()

        import pytesseract
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file, with automatic OCR fallback.

    Extraction pipeline:
    1. pdfplumber (fast, accurate for typed/digital PDFs)
    2. PyMuPDF get_text (alternative digital text extraction)
    3. Tesseract OCR (auto-detected — for scanned/image PDFs)

    Args:
        file_path: A file-like object (e.g. BytesIO) containing PDF data.

    Returns:
        tuple: (extracted_text: str, method: str)
            method is "pdfplumber", "fitz", "ocr", "none", or "error"
    """
    try:
        # Validate the stream is not empty before attempting extraction
        file_path.seek(0, 2)  # Seek to end to get size
        stream_size = file_path.tell()
        file_path.seek(0)  # Reset to beginning

        if stream_size == 0:
            return (
                "The uploaded file is empty (0 bytes). Please upload a valid PDF.",
                "error",
            )

        # --- Attempt 1: pdfplumber (fast path for typed PDFs) ---
        file_path.seek(0)
        text = _extract_with_pdfplumber(file_path)
        if text and len(text.strip()) >= MIN_TEXT_LENGTH:
            return (text, "pdfplumber")

        # --- Attempt 2: PyMuPDF text extraction ---
        file_path.seek(0)
        text = _extract_with_fitz(file_path)
        if text and len(text.strip()) >= MIN_TEXT_LENGTH:
            return (text, "fitz")

        # --- Attempt 3: OCR (the PDF is likely scanned/image-based) ---
        if _is_tesseract_available():
            # Configure tesseract path before OCR extraction
            _configure_tesseract()
            file_path.seek(0)
            text = _extract_with_ocr(file_path)
            if text and len(text.strip()) >= MIN_TEXT_LENGTH:
                return (text, "ocr")

        # Neither method produced enough text
        return ("", "none")

    except Exception as e:
        return (f"Error extracting text: {str(e)}", "error")
