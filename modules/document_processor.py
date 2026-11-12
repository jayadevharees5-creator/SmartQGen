import os
import fitz  # PyMuPDF
from docx import Document


# ============================================================
# CONFIGURATION
# ============================================================

LOGICAL_PAGE_WORD_LIMIT = 400
SCANNED_PDF_MIN_CHARACTERS = 50


# ============================================================
# COMMON HELPERS
# ============================================================

def _create_logical_pages(paragraphs, words_per_page=LOGICAL_PAGE_WORD_LIMIT):
    """
    Divide text into logical pages.

    Used for DOCX and TXT because those formats do not provide
    reliable physical page numbers.
    """

    pages = []

    current_text = []
    current_word_count = 0
    page_number = 1

    for paragraph in paragraphs:

        paragraph = str(paragraph).strip()

        if not paragraph:
            continue

        words = len(paragraph.split())

        current_text.append(paragraph)
        current_word_count += words

        if current_word_count >= words_per_page:

            pages.append({
                "page_number": page_number,
                "text": "\n".join(current_text)
            })

            page_number += 1
            current_text = []
            current_word_count = 0

    # Add remaining content
    if current_text:

        pages.append({
            "page_number": page_number,
            "text": "\n".join(current_text)
        })

    return pages


def _empty_document_result(filename, message):
    """
    Create a standard empty-document response.
    """

    return {
        "source": filename,
        "pages": [],
        "is_scanned": False,
        "total_characters": 0,
        "status_message": message
    }


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_text_from_pdf(file_path):
    """
    Extract text page-by-page from a PDF using PyMuPDF.

    Returns:
        {
            "source": filename,
            "pages": [
                {
                    "page_number": 1,
                    "text": "..."
                }
            ],
            "is_scanned": True/False,
            "total_characters": int,
            "status_message": str/None
        }
    """

    filename = os.path.basename(file_path)

    pages = []
    total_characters = 0

    try:

        with fitz.open(file_path) as doc:

            for page_number, page in enumerate(doc, start=1):

                page_text = page.get_text("text") or ""

                page_text = page_text.strip()

                total_characters += len(page_text)

                pages.append({
                    "page_number": page_number,
                    "text": page_text
                })

    except Exception as error:

        raise ValueError(
            f"Unable to read PDF '{filename}': {error}"
        )

    # --------------------------------------------------------
    # Detect scanned / image-only PDF
    # --------------------------------------------------------

    is_scanned = (
        len(pages) > 0
        and total_characters < SCANNED_PDF_MIN_CHARACTERS
    )

    status_message = None

    if is_scanned:

        status_message = (
            "This PDF appears to be scanned or image-based. "
            "OCR is required to extract text."
        )

    elif total_characters == 0:

        status_message = (
            "The PDF does not contain extractable text."
        )

    return {
        "source": filename,
        "pages": pages,
        "is_scanned": is_scanned,
        "total_characters": total_characters,
        "status_message": status_message
    }


# ============================================================
# DOCX TEXT EXTRACTION
# ============================================================

def extract_text_from_docx(file_path):
    """
    Extract text from a Microsoft Word DOCX file.

    python-docx does not reliably provide physical page numbers.
    Therefore, paragraphs are divided into logical pages of
    approximately 400 words.

    Returns the same structure as PDF extraction.
    """

    filename = os.path.basename(file_path)

    try:

        doc = Document(file_path)

    except Exception as error:

        raise ValueError(
            f"Unable to read DOCX '{filename}': {error}"
        )

    # --------------------------------------------------------
    # Extract non-empty paragraphs
    # --------------------------------------------------------

    paragraphs = []

    for paragraph in doc.paragraphs:

        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    # --------------------------------------------------------
    # Handle empty DOCX
    # --------------------------------------------------------

    if not paragraphs:

        return _empty_document_result(
            filename,
            "The DOCX document does not contain usable text."
        )

    # --------------------------------------------------------
    # Create logical pages
    # --------------------------------------------------------

    pages = _create_logical_pages(paragraphs)

    full_text = "\n\n".join(paragraphs)

    total_characters = len(full_text)

    return {
        "source": filename,
        "pages": pages,
        "is_scanned": False,
        "total_characters": total_characters,
        "status_message": None
    }


# ============================================================
# TXT TEXT EXTRACTION
# ============================================================

def extract_text_from_txt(file_path):
    """
    Extract text from a plain TXT file.

    TXT files do not have physical pages.
    Therefore, the content is divided into logical pages
    of approximately 400 words.
    """

    filename = os.path.basename(file_path)

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:

            content = file.read()

    except Exception as error:

        raise ValueError(
            f"Unable to read TXT '{filename}': {error}"
        )

    content = content.strip()

    # --------------------------------------------------------
    # Empty TXT
    # --------------------------------------------------------

    if not content:

        return _empty_document_result(
            filename,
            "The TXT file is empty."
        )

    # --------------------------------------------------------
    # Extract paragraphs
    # --------------------------------------------------------

    paragraphs = [
        paragraph.strip()
        for paragraph in content.split("\n\n")
        if paragraph.strip()
    ]

    # --------------------------------------------------------
    # If no paragraph separation exists,
    # use non-empty lines.
    # --------------------------------------------------------

    if not paragraphs:

        paragraphs = [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]

    # --------------------------------------------------------
    # Create logical pages
    # --------------------------------------------------------

    pages = _create_logical_pages(paragraphs)

    total_characters = len(content)

    return {
        "source": filename,
        "pages": pages,
        "is_scanned": False,
        "total_characters": total_characters,
        "status_message": None
    }


# ============================================================
# COMMON DOCUMENT EXTRACTION
# ============================================================

def extract_document(file_path):
    """
    Automatically detect the document type and extract text.

    Supported formats:
        PDF
        DOCX
        TXT
    """

    if not file_path:

        raise ValueError(
            "No document path was provided."
        )

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if not os.path.isfile(file_path):

        raise ValueError(
            f"The provided path is not a file: {file_path}"
        )

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":

        return extract_text_from_pdf(file_path)

    elif extension == ".docx":

        return extract_text_from_docx(file_path)

    elif extension in [".txt", ".text"]:

        return extract_text_from_txt(file_path)

    else:

        raise ValueError(
            f"Unsupported file format: '{extension}'. "
            "Supported formats: PDF, DOCX, TXT."
        )


# ============================================================
# SIMPLE VALIDATION
# ============================================================

def validate_extracted_document(document):
    """
    Validate the output returned by extract_document().

    Returns:
        True if usable
        False otherwise
    """

    if not isinstance(document, dict):

        return False

    pages = document.get("pages", [])

    if not isinstance(pages, list):

        return False

    total_characters = document.get(
        "total_characters",
        0
    )

    if total_characters <= 0:

        return False

    # Check whether at least one page contains text
    for page in pages:

        if isinstance(page, dict):

            text = page.get("text", "")

            if isinstance(text, str) and text.strip():

                return True

    return False


# ============================================================
# SELF TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("Smart Q Gen - Document Processor")
    print("=" * 60)

    print("\nSupported formats:")
    print("1. PDF")
    print("2. DOCX")
    print("3. TXT")

    print("\nExpected extraction structure:")
    print(
        """
{
    "source": "example.pdf",
    "pages": [
        {
            "page_number": 1,
            "text": "Extracted text..."
        }
    ],
    "is_scanned": False,
    "total_characters": 1234,
    "status_message": None
}
        """
    )

    print("Document processor loaded successfully.")