# modules/chunker.py
# Smart Q Gen
# ============================================================
# CONTEXT-AWARE DOCUMENT CHUNKING
#
# Flow:
#
# Extracted Document
#        ↓
# Structure Map
#        ↓
# Chunking
#        ↓
# Text Chunks + Internal Metadata + Concepts
#        ↓
# Hybrid Retrieval
#
# IMPORTANT:
#
# Unit / Topic / Chapter are INTERNAL metadata only.
#
# They are NOT:
#   - faculty selection inputs
#   - manual filters
#   - retrieval restrictions
#
# The complete chunk list is passed to the retriever.
# ============================================================

import re

from config import (
    CHUNK_SIZE_WORDS,
    CHUNK_OVERLAP_WORDS
)

from modules.text_cleaner import (
    clean_raw_text
)


# ============================================================
# GENERIC / INVALID TOPICS
# ============================================================

_GENERIC_TOPICS = {
    "this",
    "that",
    "these",
    "those",
    "it",
    "they",
    "he",
    "she",
    "we",
    "you",

    "system",
    "method",
    "process",
    "approach",
    "technique",
    "way",

    "type",
    "types",
    "example",
    "examples",

    "following",
    "figure",
    "table",

    "chapter",
    "unit",
    "section",

    "introduction",
    "definition",
    "information",
    "data",
    "result",
    "results",

    "problem",
    "solution",

    "application",
    "applications",

    "what",
    "why",
    "when",
    "where",
    "which",
    "who",
    "how",

    "there",
    "often",
    "one",
    "some",
    "many",

    "also",
    "however",
    "therefore",
    "thus",
    "such",

    "using",
    "used",
    "uses",

    "include",
    "includes",
    "including"
}


# ============================================================
# BAD START WORDS
# ============================================================

_BAD_START_WORDS = {
    "a",
    "an",
    "the",

    "is",
    "are",
    "was",
    "were",

    "be",
    "being",
    "been",

    "and",
    "or",
    "but",

    "if",
    "then",
    "than",

    "for",
    "from",
    "with",
    "without",

    "by",
    "of",
    "to",
    "in",
    "on",
    "at",
    "as",

    "this",
    "that",
    "these",
    "those",

    "what",
    "why",
    "when",
    "where",
    "which",
    "who",
    "how",

    "there",
    "one",
    "some",
    "many",
    "often"
}


# ============================================================
# BAD PHRASES
# ============================================================

_BAD_PHRASES = {
    "but are not limited to",
    "are not limited to",
    "not limited to",
    "for example",
    "such as",
    "as follows",
    "the following",
    "the above",
    "this section",
    "this chapter"
}


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def _normalize_spaces(text):
    return re.sub(
        r"\s+",
        " ",
        str(text or "")
    ).strip()


# ============================================================
# CLEAN TOPIC
# ============================================================

def _clean_topic(value):
    """
    Clean and validate an internally extracted concept/topic.
    """

    if not value:
        return ""

    value = str(value).strip()

    # --------------------------------------------------------
    # Remove numbering / bullets
    # --------------------------------------------------------

    value = re.sub(
        r"^[\s\d.)\-•*]+",
        "",
        value
    )

    # --------------------------------------------------------
    # Normalize whitespace
    # --------------------------------------------------------

    value = _normalize_spaces(
        value
    )

    # --------------------------------------------------------
    # Remove surrounding punctuation
    # --------------------------------------------------------

    value = value.strip(
        " .,:;!?()[]{}<>\"'"
    )

    if not value:
        return ""

    words = value.split()

    normalized_words = [
        word.casefold().strip(
            ".,:;!?()[]{}"
        )
        for word in words
    ]

    # --------------------------------------------------------
    # Length restrictions
    # --------------------------------------------------------

    if len(words) > 6:
        return ""

    if len(value) < 2:
        return ""

    # --------------------------------------------------------
    # Do not keep sentence-like fragments
    # --------------------------------------------------------

    if any(
        mark in value
        for mark in [
            "?",
            "!",
            ";"
        ]
    ):
        return ""

    # --------------------------------------------------------
    # Generic single words
    # --------------------------------------------------------

    if (
        len(words) == 1
        and normalized_words[0]
        in _GENERIC_TOPICS
    ):
        return ""

    # --------------------------------------------------------
    # Weak grammatical starts
    # --------------------------------------------------------

    if (
        normalized_words[0]
        in _BAD_START_WORDS
    ):
        return ""

    lowered = value.casefold()

    # --------------------------------------------------------
    # Bad phrases
    # --------------------------------------------------------

    if any(
        phrase in lowered
        for phrase in _BAD_PHRASES
    ):
        return ""

    # --------------------------------------------------------
    # Avoid complicated candidates
    # --------------------------------------------------------

    if value.count(",") > 1:
        return ""

    if ":" in value:
        return ""

    # --------------------------------------------------------
    # Must contain alphabetic characters
    # --------------------------------------------------------

    if not re.search(
        r"[a-zA-Z]",
        value
    ):
        return ""

    return value


# ============================================================
# UNIQUE TOPICS
# ============================================================

def _unique_topics(values):
    """
    Remove duplicate concepts while preserving order.
    """

    result = []
    seen = set()

    for value in values or []:

        value = _clean_topic(
            value
        )

        if not value:
            continue

        key = re.sub(
            r"\s+",
            " ",
            value
        ).casefold()

        if key in seen:
            continue

        seen.add(
            key
        )

        result.append(
            value
        )

    return result


# ============================================================
# EXTRACT TOPICS / CONCEPTS
# ============================================================

def extract_topics_from_text(
    text,
    existing_topics=None
):
    """
    Extract educational concepts from chunk content.

    Detection priority:

        1. Definition patterns
        2. Explanation patterns
        3. Educational concept patterns
        4. List items
        5. Numbered headings
        6. Existing structure metadata

    These concepts are INTERNAL metadata only.
    """

    if not text:
        return []

    original_text = str(
        text
    )

    normalized_text = _normalize_spaces(
        original_text
    )

    candidates = []

    # ========================================================
    # 1. DEFINITION PATTERNS
    # ========================================================

    definition_patterns = [

        # Cyber Security is defined as ...
        (
            r"\b([A-Za-z][A-Za-z0-9/&().-]*"
            r"(?:\s+[A-Za-z0-9][A-Za-z0-9/&().-]*){0,4})"
            r"\s+(?:is|are)"
            r"\s+(?:defined\s+as|known\s+as)\b"
        ),

        # Cyber Security refers to ...
        (
            r"\b([A-Za-z][A-Za-z0-9/&().-]*"
            r"(?:\s+[A-Za-z0-9][A-Za-z0-9/&().-]*){0,4})"
            r"\s+refers\s+to\b"
        ),

        # Integrity means ...
        (
            r"\b([A-Za-z][A-Za-z0-9/&().-]*"
            r"(?:\s+[A-Za-z0-9][A-Za-z0-9/&().-]*){0,4})"
            r"\s+means\b"
        ),

        # A virus is ...
        (
            r"\b(?:a|an|the)\s+"
            r"([A-Za-z][A-Za-z0-9/&().-]*"
            r"(?:\s+[A-Za-z0-9][A-Za-z0-9/&().-]*){0,4})"
            r"\s+(?:is|are)\b"
        ),

        # Virus is ...
        (
            r"\b([A-Za-z][A-Za-z0-9/&().-]*"
            r"(?:\s+[A-Za-z0-9][A-Za-z0-9/&().-]*){0,4})"
            r"\s+(?:is|are)\b"
        )
    ]

    for pattern in definition_patterns:

        for match in re.finditer(
            pattern,
            normalized_text,
            flags=re.IGNORECASE
        ):

            candidate = _clean_topic(
                match.group(1)
            )

            if candidate:
                candidates.append(
                    candidate
                )

    # ========================================================
    # 2. EDUCATIONAL CONCEPT PATTERNS
    # ========================================================

    educational_pattern = (
        r"\b([A-Za-z][A-Za-z0-9/&().-]*"
        r"(?:\s+[A-Za-z0-9][A-Za-z0-9/&().-]*){0,4})"
        r"\s+is\s+(?:a|an|the)\s+"
        r"(?:method|technique|process|system|"
        r"approach|technology|mechanism|framework|"
        r"model|protocol|algorithm|attack|threat|"
        r"concept|practice|activity|tool|device|"
        r"service|software|program|strategy)\b"
    )

    for match in re.finditer(
        educational_pattern,
        normalized_text,
        flags=re.IGNORECASE
    ):

        candidate = _clean_topic(
            match.group(1)
        )

        if candidate:
            candidates.append(
                candidate
            )

    # ========================================================
    # 3. LIST EXTRACTION
    # ========================================================

    list_patterns = [

        # Types of malware include virus, worm...
        (
            r"(?:types?|kinds?|categories?)\s+of\s+"
            r"[A-Za-z][A-Za-z0-9\- ]{0,60}?\s+"
            r"include\s+([^.;]+)"
        ),

        # Types include virus, worm...
        (
            r"(?:types?|kinds?|categories?|examples?)"
            r"\s+include\s+([^.;]+)"
        ),

        # Such as virus, worm...
        (
            r"(?:such as|including)\s+([^.;]+)"
        )
    ]

    for pattern in list_patterns:

        for match in re.finditer(
            pattern,
            normalized_text,
            flags=re.IGNORECASE
        ):

            values = match.group(1)

            parts = re.split(
                r",|\band\b|\bor\b",
                values,
                flags=re.IGNORECASE
            )

            for part in parts:

                candidate = _clean_topic(
                    part
                )

                if candidate:
                    candidates.append(
                        candidate
                    )

    # ========================================================
    # 4. NUMBERED / TITLE HEADINGS
    # ========================================================

    for line in original_text.splitlines():

        line = line.strip()

        if not line:
            continue

        heading = re.sub(
            r"^\d+(?:\.\d+)*[\s.)-]+",
            "",
            line
        ).strip()

        heading = _normalize_spaces(
            heading
        )

        if not heading:
            continue

        if len(
            heading.split()
        ) > 6:
            continue

        is_heading = (
            heading.isupper()
            or bool(
                re.match(
                    r"^[A-Z][A-Za-z0-9/&()\-]*"
                    r"(?:\s+[A-Za-z0-9/&()\-]+){0,5}$",
                    heading
                )
            )
        )

        if is_heading:

            candidate = _clean_topic(
                heading
            )

            if candidate:
                candidates.append(
                    candidate
                )

    # ========================================================
    # 5. EXISTING STRUCTURE METADATA
    # ========================================================

    if existing_topics:

        if isinstance(
            existing_topics,
            str
        ):

            existing_topics = [
                existing_topics
            ]

        for topic in existing_topics:

            candidate = _clean_topic(
                topic
            )

            if candidate:
                candidates.append(
                    candidate
                )

    # ========================================================
    # 6. REMOVE DUPLICATES
    # ========================================================

    return _unique_topics(
        candidates
    )


# ============================================================
# MERGE TOPICS
# ============================================================

def _merge_topics(
    chunk_topics,
    metadata_topic
):
    """
    Merge extracted concepts with structure metadata.
    """

    values = []

    if metadata_topic:
        values.append(
            metadata_topic
        )

    values.extend(
        chunk_topics or []
    )

    result = _unique_topics(
        values
    )

    if not result:
        result = [
            "General"
        ]

    return result


# ============================================================
# SAFE INTEGER
# ============================================================

def _safe_positive_int(
    value,
    default
):
    try:

        value = int(
            value
        )

    except (
        ValueError,
        TypeError
    ):

        return default

    if value <= 0:
        return default

    return value


# ============================================================
# CREATE CHUNKS
# ============================================================

def create_chunks_from_structure(
    extracted_doc,
    structure_data,
    chunk_size=CHUNK_SIZE_WORDS,
    chunk_overlap=CHUNK_OVERLAP_WORDS
):
    """
    Create retrieval chunks from document structure.

    Metadata preserved:

        chapter
        chapter_title
        unit
        unit_title
        topic
        topics

    IMPORTANT:

    All chunks are returned to the retriever.

    Unit/topic/chapter metadata does NOT restrict
    document retrieval.
    """

    # ========================================================
    # INPUT VALIDATION
    # ========================================================

    if not extracted_doc:
        return []

    if not structure_data:
        return []

    chunk_size = _safe_positive_int(
        chunk_size,
        400
    )

    chunk_overlap = _safe_positive_int(
        chunk_overlap,
        50
    )

    if chunk_overlap >= chunk_size:

        chunk_overlap = max(
            0,
            chunk_size // 10
        )

    source_filename = (
        extracted_doc.get(
            "source"
        )
        or extracted_doc.get(
            "filename"
        )
        or "unknown_document"
    )

    structure_map = (
        structure_data.get(
            "structure_map",
            []
        )
    )

    # ========================================================
    # FALLBACK
    # ========================================================

    if not structure_map:

        return _create_fallback_chunks(
            extracted_doc,
            source_filename,
            chunk_size,
            chunk_overlap
        )

    chunks = []

    chunk_id = 1

    current_words = []

    current_text_blocks = []

    current_chapter = "General"

    current_chapter_title = ""

    current_unit = "General"

    current_unit_title = ""

    current_topic = "General"

    current_page = 1

    # ========================================================
    # SAVE CHUNK
    # ========================================================

    def save_chunk():

        nonlocal chunk_id
        nonlocal current_words
        nonlocal current_text_blocks

        if not current_text_blocks:
            return

        raw_text = " ".join(
            current_text_blocks
        ).strip()

        cleaned_text = clean_raw_text(
            raw_text
        ).strip()

        if not cleaned_text:
            return

        words = cleaned_text.split()

        # Ignore extremely tiny chunks.
        if len(words) < 8:
            return

        # ----------------------------------------------------
        # Extract concepts from actual text.
        # ----------------------------------------------------

        extracted_topics = (
            extract_topics_from_text(
                cleaned_text,
                existing_topics=current_topic
            )
        )

        # ----------------------------------------------------
        # Merge structure topic.
        # ----------------------------------------------------

        extracted_topics = _merge_topics(
            extracted_topics,
            current_topic
        )

        primary_topic = extracted_topics[0]

        if (
            current_topic != "General"
            and _clean_topic(
                current_topic
            )
        ):
            primary_topic = current_topic

        # ----------------------------------------------------
        # Create chunk.
        # ----------------------------------------------------

        chunk = {

            "chunk_id":
                chunk_id,

            "document_id":
                source_filename,

            "source":
                source_filename,

            "page":
                current_page,

            # ------------------------------------------------
            # Internal structure metadata
            # ------------------------------------------------

            "chapter":
                current_chapter,

            "chapter_title":
                current_chapter_title,

            "unit":
                current_unit,

            "unit_title":
                current_unit_title,

            # ------------------------------------------------
            # Internal concept metadata
            # ------------------------------------------------

            "topic":
                primary_topic,

            "topics":
                extracted_topics,

            # ------------------------------------------------
            # Retrieval text
            # ------------------------------------------------

            "text":
                cleaned_text,

            "word_count":
                len(words)
        }

        chunks.append(
            chunk
        )

        print(
            f"    Chunk {chunk_id}: "
            f"{len(words)} words | "
            f"Page {current_page} | "
            f"Unit: {current_unit} | "
            f"Concepts: {len(extracted_topics)}"
        )

        chunk_id += 1

    # ========================================================
    # PROCESS STRUCTURE MAP
    # ========================================================

    for item in structure_map:

        if not isinstance(
            item,
            dict
        ):
            continue

        text_line = str(
            item.get(
                "text",
                ""
            )
        ).strip()

        if not text_line:
            continue

        line_words = text_line.split()

        item_chapter = (
            item.get(
                "chapter",
                "General"
            )
            or "General"
        )

        item_chapter_title = (
            item.get(
                "chapter_title",
                ""
            )
            or ""
        )

        item_unit = (
            item.get(
                "unit",
                "General"
            )
            or "General"
        )

        item_unit_title = (
            item.get(
                "unit_title",
                ""
            )
            or ""
        )

        item_topic = (
            item.get(
                "topic",
                "General"
            )
            or "General"
        )

        item_page = item.get(
            "page",
            1
        )

        # ====================================================
        # CHAPTER / UNIT CHANGE
        # ====================================================

        structure_changed = (
            item_chapter != current_chapter
            or item_unit != current_unit
        )

        if (
            structure_changed
            and current_words
        ):

            save_chunk()

            current_words = []

            current_text_blocks = []

        # ====================================================
        # UPDATE METADATA
        # ====================================================

        current_chapter = (
            item_chapter
        )

        current_chapter_title = (
            item_chapter_title
        )

        current_unit = (
            item_unit
        )

        current_unit_title = (
            item_unit_title
        )

        if (
            item_topic
            and item_topic != "General"
        ):

            current_topic = (
                item_topic
            )

        try:

            current_page = int(
                item_page
            )

        except (
            ValueError,
            TypeError
        ):

            current_page = 1

        # ====================================================
        # ADD TEXT
        # ====================================================

        current_text_blocks.append(
            text_line
        )

        current_words.extend(
            line_words
        )

        # ====================================================
        # CHUNK SIZE
        # ====================================================

        if len(
            current_words
        ) >= chunk_size:

            save_chunk()

            # ------------------------------------------------
            # Preserve overlap.
            # ------------------------------------------------

            if chunk_overlap > 0:

                overlap_words = (
                    current_words[
                        -chunk_overlap:
                    ]
                )

            else:

                overlap_words = []

            current_words = list(
                overlap_words
            )

            if overlap_words:

                current_text_blocks = [
                    " ".join(
                        overlap_words
                    )
                ]

            else:

                current_text_blocks = []

    # ========================================================
    # FINAL CHUNK
    # ========================================================

    if current_words:
        save_chunk()

    # ========================================================
    # FALLBACK
    # ========================================================

    if not chunks:

        print(
            "\nStructure chunking produced "
            "no usable chunks."
        )

        print(
            "Trying direct page-based chunking..."
        )

        chunks = _create_fallback_chunks(
            extracted_doc,
            source_filename,
            chunk_size,
            chunk_overlap
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    all_topics = []

    for chunk in chunks:

        all_topics.extend(
            chunk.get(
                "topics",
                []
            )
        )

    unique_topics = _unique_topics(
        all_topics
    )

    print()

    print(
        "========================================"
    )

    print(
        "CHUNKING COMPLETED"
    )

    print(
        "========================================"
    )

    print(
        "Total chunks:",
        len(chunks)
    )

    print(
        "Internal concepts/topics:",
        len(unique_topics)
    )

    print(
        unique_topics
    )

    print(
        "========================================"
    )

    return chunks


# ============================================================
# FALLBACK PAGE-BASED CHUNKING
# ============================================================

def _create_fallback_chunks(
    extracted_doc,
    source_filename,
    chunk_size,
    chunk_overlap
):
    """
    Create chunks directly from document pages.
    """

    chunks = []

    chunk_id = 1

    pages = extracted_doc.get(
        "pages",
        []
    )

    for page in pages:

        if not isinstance(
            page,
            dict
        ):
            continue

        page_text = str(
            page.get(
                "text",
                ""
            )
        ).strip()

        if not page_text:
            continue

        cleaned_text = clean_raw_text(
            page_text
        ).strip()

        if not cleaned_text:
            continue

        words = cleaned_text.split()

        if len(words) < 8:
            continue

        start = 0

        while start < len(words):

            end = min(
                start + chunk_size,
                len(words)
            )

            chunk_words = words[
                start:end
            ]

            if not chunk_words:
                break

            chunk_text = " ".join(
                chunk_words
            )

            extracted_topics = (
                extract_topics_from_text(
                    chunk_text
                )
            )

            if not extracted_topics:

                extracted_topics = [
                    "General"
                ]

            page_number = page.get(
                "page_number",
                1
            )

            chunk = {

                "chunk_id":
                    chunk_id,

                "document_id":
                    source_filename,

                "source":
                    source_filename,

                "page":
                    page_number,

                "chapter":
                    "General",

                "chapter_title":
                    "",

                "unit":
                    "General",

                "unit_title":
                    "",

                "topic":
                    extracted_topics[0],

                "topics":
                    extracted_topics,

                "text":
                    chunk_text,

                "word_count":
                    len(chunk_words)
            }

            chunks.append(
                chunk
            )

            print(
                f"    Fallback Chunk "
                f"{chunk_id}: "
                f"{len(chunk_words)} words | "
                f"Page {page_number} | "
                f"Concepts: {len(extracted_topics)}"
            )

            chunk_id += 1

            # ------------------------------------------------
            # Move forward.
            # ------------------------------------------------

            if end >= len(words):
                break

            next_start = (
                end - chunk_overlap
            )

            # Safety against infinite loops.
            if next_start <= start:
                next_start = end

            start = next_start

    return chunks


# ============================================================
# EXPAND CHUNK CONTEXT
# ============================================================

def expand_chunk_context(
    chunks,
    target_chunk,
    window_size=1
):
    """
    Expand a chunk using nearby chunks
    from the same internal chapter/unit.

    This does NOT filter retrieval.
    """

    if not target_chunk:
        return ""

    if not chunks:

        return target_chunk.get(
            "text",
            ""
        )

    target_id = target_chunk.get(
        "chunk_id"
    )

    try:

        target_id = int(
            target_id
        )

    except (
        ValueError,
        TypeError
    ):

        return target_chunk.get(
            "text",
            ""
        )

    target_chapter = (
        target_chunk.get(
            "chapter"
        )
    )

    target_unit = (
        target_chunk.get(
            "unit"
        )
    )

    neighbor_chunks = []

    for chunk in chunks:

        if not isinstance(
            chunk,
            dict
        ):
            continue

        try:

            chunk_id = int(
                chunk.get(
                    "chunk_id"
                )
            )

        except (
            ValueError,
            TypeError
        ):

            continue

        if (
            chunk.get("chapter")
            != target_chapter
        ):
            continue

        if (
            chunk.get("unit")
            != target_unit
        ):
            continue

        if abs(
            chunk_id - target_id
        ) <= window_size:

            text = chunk.get(
                "text",
                ""
            )

            if text:

                neighbor_chunks.append(
                    (
                        chunk_id,
                        text
                    )
                )

    neighbor_chunks.sort(
        key=lambda item: item[0]
    )

    if neighbor_chunks:

        return "\n\n".join(
            text
            for _, text
            in neighbor_chunks
        )

    return target_chunk.get(
        "text",
        ""
    )


# ============================================================
# MODULE SELF TEST
# ============================================================

if __name__ == "__main__":

    print(
        "========================================"
    )

    print(
        "SMART Q GEN - CHUNKER TEST"
    )

    print(
        "========================================"
    )

    sample_document = {

        "source":
            "sample.txt",

        "pages": [

            {
                "page_number": 1,

                "text": (
                    "UNIT 1\n"
                    "MALWARE\n"
                    "Malware is malicious software "
                    "designed to damage computer systems. "
                    "Types include virus, worm and trojan."
                )
            }
        ]
    }

    sample_structure = {

        "structure_map": [

            {
                "page": 1,

                "chapter":
                    "Chapter 1",

                "chapter_title":
                    "Cyber Security",

                "unit":
                    "Unit 1",

                "unit_title":
                    "Malware",

                "topic":
                    "Malware",

                "text":
                    (
                        "Malware is malicious software "
                        "designed to damage computer systems."
                    )
            },

            {
                "page": 1,

                "chapter":
                    "Chapter 1",

                "chapter_title":
                    "Cyber Security",

                "unit":
                    "Unit 1",

                "unit_title":
                    "Malware",

                "topic":
                    "Malware",

                "text":
                    (
                        "Types include virus, worm and trojan."
                    )
            }
        ]
    }

    result = create_chunks_from_structure(
        sample_document,
        sample_structure,
        chunk_size=100,
        chunk_overlap=10
    )

    print()

    print(
        "Created chunks:"
    )

    for chunk in result:

        print()

        print(
            "--------------------"
        )

        print(
            "Chunk ID:",
            chunk.get(
                "chunk_id"
            )
        )

        print(
            "Page:",
            chunk.get(
                "page"
            )
        )

        print(
            "Chapter:",
            chunk.get(
                "chapter"
            )
        )

        print(
            "Unit:",
            chunk.get(
                "unit"
            )
        )

        print(
            "Topic:",
            chunk.get(
                "topic"
            )
        )

        print(
            "Topics:",
            chunk.get(
                "topics"
            )
        )

        print(
            "Word count:",
            chunk.get(
                "word_count"
            )
        )

        print(
            "Text:",
            chunk.get(
                "text"
            )
        )

    print()

    print(
        "========================================"
    )

    print(
        "CHUNKER TEST COMPLETED"
    )

    print(
        "========================================"
    )