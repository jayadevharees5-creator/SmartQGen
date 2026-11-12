import os

from modules.document_processor import extract_document
from modules.structure_detector import parse_document_structure
from modules.chunker import create_chunks_from_structure


FILE_PATH = "uploads/sample.pdf"


print("=" * 60)
print("DOCUMENT PIPELINE DEBUG TEST")
print("=" * 60)


# ------------------------------------------------------------
# 1. CHECK FILE
# ------------------------------------------------------------

print("\n[1] Checking file...")

if not os.path.exists(FILE_PATH):
    print("ERROR: File not found:")
    print(FILE_PATH)
    exit()

print("File found:", FILE_PATH)


# ------------------------------------------------------------
# 2. EXTRACT TEXT
# ------------------------------------------------------------

print("\n[2] Extracting document...")

document = extract_document(FILE_PATH)

print("Source:")
print(document.get("source"))

print("Total characters:")
print(document.get("total_characters"))

print("Number of pages:")
print(len(document.get("pages", [])))

print("Scanned:")
print(document.get("is_scanned"))


# ------------------------------------------------------------
# 3. CHECK PAGE TEXT
# ------------------------------------------------------------

print("\n[3] Checking extracted page text...")

total_page_characters = 0

for page in document.get("pages", []):

    page_number = page.get(
        "page_number",
        0
    )

    text = page.get(
        "text",
        ""
    )

    characters = len(
        text.strip()
    )

    total_page_characters += characters

    print(
        f"Page {page_number}: "
        f"{characters} characters"
    )

    if characters > 0 and page_number <= 2:

        print("Sample text:")
        print(
            text[:500]
        )
        print("-" * 40)


print(
    "\nTotal page characters:",
    total_page_characters
)


# ------------------------------------------------------------
# 4. STRUCTURE DETECTION
# ------------------------------------------------------------

print("\n[4] Detecting structure...")

structure = parse_document_structure(
    document
)

structure_map = structure.get(
    "structure_map",
    []
)

print(
    "Structure items:",
    len(structure_map)
)

print(
    "Detected chapters:",
    structure.get(
        "detected_chapters",
        []
    )
)


# ------------------------------------------------------------
# 5. CHECK STRUCTURE CONTENT
# ------------------------------------------------------------

if structure_map:

    print("\nFirst 10 structure items:")

    for item in structure_map[:10]:

        print(
            "Page:",
            item.get("page")
        )

        print(
            "Chapter:",
            item.get("chapter")
        )

        print(
            "Topic:",
            item.get("topic")
        )

        print(
            "Text:",
            item.get("text")
        )

        print("-" * 40)

else:

    print(
        "WARNING: structure_map is EMPTY"
    )


# ------------------------------------------------------------
# 6. CREATE CHUNKS
# ------------------------------------------------------------

print("\n[5] Creating chunks...")

chunks = create_chunks_from_structure(
    document,
    structure
)

print(
    "\nTOTAL CHUNKS:",
    len(chunks)
)


# ------------------------------------------------------------
# 7. SHOW FIRST CHUNKS
# ------------------------------------------------------------

if chunks:

    print("\nFirst 3 chunks:")

    for chunk in chunks[:3]:

        print("\nChunk ID:")
        print(
            chunk.get("chunk_id")
        )

        print("Page:")
        print(
            chunk.get("page")
        )

        print("Chapter:")
        print(
            chunk.get("chapter")
        )

        print("Topic:")
        print(
            chunk.get("topic")
        )

        print("Word count:")
        print(
            chunk.get("word_count")
        )

        print("Text:")
        print(
            chunk.get("text")[:500]
        )

else:

    print(
        "\nERROR: ZERO CHUNKS CREATED"
    )


print("\n" + "=" * 60)
print("DEBUG TEST COMPLETED")
print("=" * 60)