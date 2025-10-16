import fitz  # PyMuPDF
import docx
from pathlib import Path
from typing import Union

def load_pdf(file_path: Union[str, Path]) -> str:
    """
    Extracts text content from a PDF file.

    Args:
        file_path: The path to the PDF file.

    Returns:
        The extracted text as a single string.
    """
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def load_docx(file_path: Union[str, Path]) -> str:
    """
    Extracts text content from a DOCX file.

    Args:
        file_path: The path to the DOCX file.

    Returns:
        The extracted text as a single string.
    """
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def load_document(file_path: Union[str, Path]) -> str:
    """
    Loads a document (PDF or DOCX) and extracts its text content.

    Args:
        file_path: The path to the document.

    Returns:
        The extracted text content.
    
    Raises:
        ValueError: If the file type is not supported.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found at: {path}")

    file_extension = path.suffix.lower()
    if file_extension == ".pdf":
        return load_pdf(path)
    elif file_extension == ".docx":
        return load_docx(path)
    else:
        raise ValueError(f"Unsupported file type: '{file_extension}'")