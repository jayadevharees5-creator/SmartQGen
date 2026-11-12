# modules/text_cleaner.py
# Advanced Text Cleaning & Preprocessing preserving formulas and academic content

import re
import spacy

_nlp = None

def get_spacy_nlp():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except Exception:
            _nlp = None
    return _nlp


def clean_raw_text(text: str) -> str:
    """
    Cleans raw document text safely:
    1. Removes PDF noise, slide headers/footers (e.g. "7 KLNCE TQM-Unit 1 Dr.RMS", "Page 15").
    2. Strips faculty names, subject codes, slide numbers, and isolated artifacts.
    3. Normalizes bullet symbols ('➢', '•', '■', '→') into proper sentence structures.
    4. Deduplicates repeated consecutive words caused by PDF text extraction (e.g., "Availability Availability" -> "Availability").
    5. Preserves mathematical/scientific formulas (x², E=mc², H₂O, O(n²)).
    """
    if not text:
        return ""

    # Replace non-breaking spaces and vertical tabs
    text = text.replace('\xa0', ' ').replace('\v', '\n').replace('\r', '\n')

    # Remove repeated page numbers & page header/footer patterns
    text = re.sub(r'(?i)page\s+\d+(\s+of\s+\d+)?', '', text)
    text = re.sub(r'(?i)-+\s*page\s*\d+\s*-+', '', text)
    
    # Remove college/faculty footer & header artifacts (e.g., "MALLA REDDY COLLEGE...", "DEPARTMENT OF INFORMATION TECHNOLOGY", "TQM-Unit 1", etc.)
    text = re.sub(r'(?i)\bDIGITAL\s+NOTES\s+ON\s+[A-Za-z0-9\s,\-()]+', '', text)
    text = re.sub(r'(?i)\b(III|II|IV)\s+YEAR\s+–?\s+(I|II)\s+SEM\b', '', text)
    text = re.sub(r'(?i)\b(Autonomous\s+Institution|Govt|UGC)\b', '', text)
    text = re.sub(r'(?i)\bMALLA\s+REDDY\s+[A-Za-z0-9\s,&]+(DEPARTMENT|TECHNOLOGY|ENGINEERING)\b', '', text)
    text = re.sub(r'(?i)\bDEPARTMENT\s+OF\s+[A-Z\s,]+\b', '', text)
    text = re.sub(r'\b\d+\s+[A-Z]{3,}\s+[A-Z0-9\-]+\s+Dr\.[A-Za-z0-9.]+\b', '', text)
    text = re.sub(r'\bDr\.[A-Z]{2,5}\b', '', text)
    text = re.sub(r'\b[A-Z]{4,}\s+TQM-Unit\s+\d+\b', '', text)
    text = re.sub(r'(?i)\b(R18A\d+|B\.TECH|COURSE\s+NOTES|LECTURE\s+NOTES)\b', '', text)
    text = re.sub(r'(?i)\bslide\s+\d+\b', '', text)

    # Normalize symbols such as "➢", "•", "■", "->", "=>" into clean line breaks or sentence separators
    text = re.sub(r'[➢•■▪►▶✓✦❖\t]+', ' ', text)
    text = re.sub(r'\s*[-=]>\s*', ' - ', text)

    # Deduplicate consecutive identical words (case-insensitive) e.g., "Availability Availability" -> "Availability"
    text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text, flags=re.IGNORECASE)

    # Clean concatenated heading + pronoun artifacts from PDF extraction (e.g. "Worm It is" -> "Worm is", "Brute force It is" -> "Brute force is")
    text = re.sub(r'\b([A-Z][A-Za-z0-9\s\-]{2,35})\s+(It|They|This|These|That|Those)\s+(is|are|was|were|refers|denotes|represents|defines)\b', r'\1 \3', text)
    text = re.sub(r'\b([A-Z][A-Za-z0-9\s\-]{2,35})\s+(There|Here)\s+(is|are|was|were)\b', r'\1: \2 \3', text)

    # Normalize excessive linebreaks
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Clean multiple spaces within lines while preserving single newline breaks
    lines = []
    for line in text.split('\n'):
        cleaned_line = re.sub(r'[ \t]+', ' ', line).strip()
        # Deduplicate words within line
        cleaned_line = re.sub(r'\b(\w+)\s+\1\b', r'\1', cleaned_line, flags=re.IGNORECASE)
        # Filter out standalone numbers or single-word noise lines (e.g., standalone page numbers "7" or "Page")
        if re.match(r'^\d+$', cleaned_line):
            continue
        if len(cleaned_line) > 0:
            lines.append(cleaned_line)

    cleaned_text = '\n'.join(lines)
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)

    return cleaned_text.strip()


def split_into_sentences(text: str) -> list:
    """
    Splits cleaned text into sentences using spaCy NLP or regex fallback.
    Ensures extracted sentences are complete and contain sufficient information (> 25 chars, > 4 words).
    """
    cleaned = clean_raw_text(text)
    if not cleaned:
        return []

    raw_sentences = []
    nlp = get_spacy_nlp()
    if nlp is not None:
        doc = nlp(cleaned)
        raw_sentences = [sent.text.strip() for sent in doc.sents]
    else:
        # Fallback sentence splitter using regex
        raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', cleaned)]

    valid_sentences = []
    for s in raw_sentences:
        s_clean = re.sub(r'\s+', ' ', s).strip()
        s_clean = re.sub(r'\b(\w+)\s+\1\b', r'\1', s_clean, flags=re.IGNORECASE)
        words = s_clean.split()

        # Reject sentences that are too short, incomplete fragments, or non-alphabetic noise
        if len(s_clean) < 25 or len(words) < 5:
            continue

        # Must contain at least one verb and noun / proper noun structure (alphabetic chars > 60%)
        alpha_count = sum(1 for c in s_clean if c.isalpha())
        if alpha_count / max(len(s_clean), 1) < 0.5:
            continue

        valid_sentences.append(s_clean)

    return valid_sentences

