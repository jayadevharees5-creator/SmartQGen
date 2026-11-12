from modules.document_processor import extract_text_from_pdf
from modules.structure_detector import parse_document_structure
from modules.chunker import create_chunks_from_structure


PDF_PATH = "uploads/sample.pdf"


print("================================")
print("CHUNK QUALITY TEST")
print("================================")


# --------------------------------------------------
# 1. Read PDF
# --------------------------------------------------

print("\n[1] Reading PDF...")

extracted_doc = extract_text_from_pdf(PDF_PATH)

print("Source:", extracted_doc.get("source"))
print("Pages:", extracted_doc.get("pages"))
print("Characters:", len(extracted_doc.get("text", "")))


# --------------------------------------------------
# 2. Detect structure
# --------------------------------------------------

print("\n[2] Detecting document structure...")

structure_data = parse_document_structure(extracted_doc)

print(
    "Structure items:",
    len(structure_data.get("structure_map", []))
)


# --------------------------------------------------
# 3. Create chunks
# --------------------------------------------------

print("\n[3] Creating chunks...")

chunks = create_chunks_from_structure(
    extracted_doc,
    structure_data
)

print("Total chunks:", len(chunks))


# --------------------------------------------------
# 4. Basic validation
# --------------------------------------------------

print("\n[4] Validating chunks...")

assert isinstance(chunks, list), "Chunks must be a list"

assert len(chunks) > 0, "No chunks generated"

print("✓ Chunk list valid")


# --------------------------------------------------
# 5. Check required fields
# --------------------------------------------------

required_fields = [
    "chunk_id",
    "document_id",
    "source",
    "page",
    "chapter",
    "chapter_title",
    "topic",
    "text",
    "word_count"
]

for chunk in chunks:

    for field in required_fields:

        assert field in chunk, (
            f"Missing field '{field}' "
            f"in chunk {chunk.get('chunk_id')}"
        )

print("✓ Required metadata fields present")


# --------------------------------------------------
# 6. Check empty chunks
# --------------------------------------------------

empty_chunks = [
    c for c in chunks
    if not c["text"].strip()
]

print("Empty chunks:", len(empty_chunks))

assert len(empty_chunks) == 0, "Empty chunks found"

print("✓ No empty chunks")


# --------------------------------------------------
# 7. Check minimum word count
# --------------------------------------------------

small_chunks = [
    c for c in chunks
    if c["word_count"] < 25
]

print("Chunks below 25 words:", len(small_chunks))

assert len(small_chunks) == 0, (
    "Chunks below minimum word count found"
)

print("✓ Minimum word count satisfied")


# --------------------------------------------------
# 8. Check duplicate chunk IDs
# --------------------------------------------------

chunk_ids = [
    c["chunk_id"]
    for c in chunks
]

assert len(chunk_ids) == len(set(chunk_ids)), (
    "Duplicate chunk IDs found"
)

print("✓ Chunk IDs are unique")


# --------------------------------------------------
# 9. Check duplicate text
# --------------------------------------------------

texts = [
    c["text"]
    for c in chunks
]

duplicate_texts = len(texts) - len(set(texts))

print("Duplicate text chunks:", duplicate_texts)


# --------------------------------------------------
# 10. Word count verification
# --------------------------------------------------

incorrect_word_counts = []

for chunk in chunks:

    actual_count = len(chunk["text"].split())

    if actual_count != chunk["word_count"]:

        incorrect_word_counts.append(
            chunk["chunk_id"]
        )

print(
    "Incorrect word counts:",
    len(incorrect_word_counts)
)

assert len(incorrect_word_counts) == 0, (
    "Word count mismatch found"
)

print("✓ Word counts are correct")


# --------------------------------------------------
# 11. Show statistics
# --------------------------------------------------

word_counts = [
    c["word_count"]
    for c in chunks
]

print("\n================================")
print("CHUNK STATISTICS")
print("================================")

print("Total chunks:", len(chunks))
print("Minimum words:", min(word_counts))
print("Maximum words:", max(word_counts))
print(
    "Average words:",
    round(sum(word_counts) / len(word_counts), 2)
)


# --------------------------------------------------
# 12. Show sample chunks
# --------------------------------------------------

print("\n================================")
print("SAMPLE CHUNKS")
print("================================")

for chunk in chunks[:3]:

    print("\nChunk ID:", chunk["chunk_id"])
    print("Page:", chunk["page"])
    print("Chapter:", chunk["chapter"])
    print("Topic:", chunk["topic"])
    print("Word count:", chunk["word_count"])

    print("Text:")
    print(chunk["text"][:300])
    print("...")


# --------------------------------------------------
# Final result
# --------------------------------------------------

print("\n================================")
print("CHUNK QUALITY TEST PASSED")
print("================================")
