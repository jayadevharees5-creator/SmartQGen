import re

CHAPTER_PATTERNS = [
    r'^(chapter|unit|module)\s+([0-9ivxlcdm]+)\s*[:\-–—·.]?\s*(.*)$',

    r'^(chapter|unit|module)\s*[:\-–—·.]?\s*'
    r'([0-9ivxlcdm]+)\s*[:\-–—·.]?\s*(.*)$',

    r'^([0-9]+)\.\s+'
    r'([A-Z][A-Za-z0-9\s,\-&\(\)/]{2,80})$'
]


TOPIC_PATTERNS = [

    # Example:
    # 1.1 Database Models
    # 2.3 Normalization
    # 3.2.1 Transaction States
    r'^([0-9]+\.[0-9]+(?:\.[0-9]+)?)\s+(.+)$',

    # Example:
    # Topic: Database Models
    # Section: Normalization
    # Sub-topic: Primary Keys
    r'^(topic|section|sub-topic|subtopic)\s*'
    r'[:\-–—·.]?\s*(.+)$'
]


IGNORED_TOPICS = {
    "overview",
    "general",
    "general topic",
    "general context",
    "introduction",
    "contents",
    "table of contents",
    "index",
    "references",
    "bibliography",
    "summary",
    "conclusion",
    "appendix",
    "acknowledgement",
    "acknowledgements",
    "preface"
}


# ============================================================
# CLEAN TITLE
# ============================================================

def clean_title(title_str: str) -> str:

    if not title_str:
        return ""

    cleaned = re.sub(
        r'^[^\w]+',
        '',
        title_str
    ).strip()

    cleaned = re.sub(
        r'\s+',
        ' ',
        cleaned
    )

    return cleaned if cleaned else title_str.strip()


# ============================================================
# CHECK WHETHER TEXT LOOKS LIKE A HEADING
# ============================================================

def looks_like_heading(text: str) -> bool:

    if not text:
        return False

    text = text.strip()

    if len(text) < 3:
        return False

    if len(text) > 120:
        return False

    # Avoid normal sentences
    if text.endswith(".") and len(
        text.split()
    ) > 8:
        return False

    # Avoid question sentences
    if text.endswith("?"):
        return False

    return True


# ============================================================
# DETECT TOPIC FROM A LINE
# ============================================================

def detect_heading_topic(line: str):

    if not line:
        return None

    line = line.strip()

    if not looks_like_heading(line):
        return None

    # --------------------------------------------------------
    # Explicit topic / section heading
    # --------------------------------------------------------

    for pattern in TOPIC_PATTERNS:

        match = re.match(
            pattern,
            line,
            re.IGNORECASE
        )

        if match:

            groups = match.groups()

            title = clean_title(
                groups[-1]
            )

            if not title:
                return None

            if (
                title.casefold()
                in IGNORED_TOPICS
            ):
                return None

            return title

    return None


# ============================================================
# PARSE DOCUMENT STRUCTURE
# ============================================================

def parse_document_structure(extracted_doc):

    pages = extracted_doc.get(
        "pages",
        []
    )

    structure_map = []

    current_chapter = "General"
    current_chapter_title = ""
    current_topic = ""

    detected_chapters = set()
    detected_topics = set()

    # ========================================================
    # PROCESS EVERY PAGE
    # ========================================================

    for page in pages:

        page_num = page.get(
            "page_number",
            1
        )

        page_text = page.get(
            "text",
            ""
        )

        if not page_text:
            continue

        lines = [
            line.strip()
            for line in page_text.split("\n")
            if line.strip()
        ]

        # ====================================================
        # PROCESS EVERY LINE
        # ====================================================

        for line in lines:

            matched_chapter = False

            # ------------------------------------------------
            # 1. CHAPTER / UNIT / MODULE DETECTION
            # ------------------------------------------------

            for pattern in CHAPTER_PATTERNS:

                match = re.match(
                    pattern,
                    line,
                    re.IGNORECASE
                )

                if not match:
                    continue

                groups = match.groups()

                # Pattern:
                # chapter / unit / module + number + title

                if groups[0].lower() in {
                    "chapter",
                    "unit",
                    "module"
                }:

                    ch_type = (
                        groups[0].capitalize()
                    )

                    ch_num = (
                        groups[1].upper()
                    )

                    raw_title = (
                        groups[2]
                        if len(groups) > 2
                        else ""
                    )

                else:

                    # Pattern:
                    # 1. Database Management

                    ch_type = "Chapter"

                    ch_num = groups[0]

                    raw_title = groups[1]

                ch_title = clean_title(
                    raw_title
                )

                current_chapter = (
                    f"{ch_type} {ch_num}"
                )

                current_chapter_title = (
                    ch_title
                )

                # Keep chapter title as current context,
                # but do NOT automatically add it as a topic.
                current_topic = ""

                chapter_name = (
                    current_chapter
                )

                if ch_title:

                    chapter_name += (
                        f" - {ch_title}"
                    )

                detected_chapters.add(
                    chapter_name
                )

                matched_chapter = True

                break

            # ------------------------------------------------
            # 2. TOPIC DETECTION
            # ------------------------------------------------

            if not matched_chapter:

                topic = detect_heading_topic(
                    line
                )

                if topic:

                    current_topic = topic

                    detected_topics.add(
                        topic
                    )

            # ------------------------------------------------
            # 3. ADD STRUCTURE ITEM
            # ------------------------------------------------

            structure_map.append({

                "page": page_num,

                "chapter": current_chapter,

                "chapter_title": (
                    current_chapter_title
                ),

                "topic": current_topic,

                "text": line

            })

    # ========================================================
    # FALLBACK TOPIC DETECTION
    # ========================================================

    # If explicit topic headings were not detected,
    # use meaningful chapter titles as selectable topics.

    if not detected_topics:

        for chapter in detected_chapters:

            if " - " in chapter:

                chapter_title = (
                    chapter.split(
                        " - ",
                        1
                    )[1].strip()
                )

                if (
                    chapter_title
                    and chapter_title.casefold()
                    not in IGNORED_TOPICS
                ):

                    detected_topics.add(
                        chapter_title
                    )

    # ========================================================
    # RETURN STRUCTURE
    # ========================================================

    return {

        "structure_map": structure_map,

        "detected_chapters": sorted(
            detected_chapters
        ) if detected_chapters else [
            "General"
        ],

        "detected_topics": sorted(
            detected_topics
        )
    }


# ============================================================
# SELF TEST
# ============================================================

if __name__ == "__main__":

    sample_document = {

        "pages": [

            {
                "page_number": 1,
                "text": """
                Chapter 1 - Database Management
                1.1 Database Models
                1.2 Primary Keys
                1.3 Normalization
                """
            },

            {
                "page_number": 2,
                "text": """
                Chapter 2 - SQL
                2.1 SELECT Statements
                2.2 JOIN Operations
                2.3 Aggregate Functions
                """
            },

            {
                "page_number": 3,
                "text": """
                Chapter 3 - Transactions
                3.1 ACID Properties
                3.2 Concurrency Control
                """
            }

        ]

    }

    result = parse_document_structure(
        sample_document
    )

    print("\n========================================")
    print("SMART Q GEN - STRUCTURE DETECTOR TEST")
    print("========================================")

    print("\nDetected Chapters:")

    for chapter in result[
        "detected_chapters"
    ]:

        print(
            "-",
            chapter
        )

    print("\nDetected Topics:")

    for topic in result[
        "detected_topics"
    ]:

        print(
            "-",
            topic
        )

    print("\nStructure Items:")

    for item in result[
        "structure_map"
    ][:10]:

        print(
            item
        )

    print("\n========================================")
    print("TEST COMPLETED")
    print("========================================")