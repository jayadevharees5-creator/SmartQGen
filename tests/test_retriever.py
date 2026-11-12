from modules.document_processor import extract_text_from_pdf
from modules.structure_detector import parse_document_structure
from modules.chunker import create_chunks_from_structure
from modules.retriever import (
    tokenize,
    calculate_relevance,
    retrieve_relevant_chunks
)


PDF_PATH = "uploads/sample.pdf"


print("================================")
print("RETRIEVER TEST")
print("================================")


# --------------------------------------------------
# 1. Read PDF
# --------------------------------------------------

print("\n[1] Reading PDF...")

extracted_doc = extract_text_from_pdf(PDF_PATH)

print("Source:", extracted_doc["source"])
print("Pages:", len(extracted_doc["pages"]))
print("Characters:", extracted_doc["total_characters"])


# --------------------------------------------------
# 2. Detect structure
# --------------------------------------------------

print("\n[2] Detecting structure...")

structure_data = parse_document_structure(
    extracted_doc
)

print(
    "Structure items:",
    len(structure_data["structure_map"])
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
# 4. Test tokenization
# --------------------------------------------------

print("\n[4] Testing tokenization...")

tokens = tokenize(
    "Cyber security protects computer networks."
)

print("Tokens:", tokens)

assert "cyber" in tokens
assert "security" in tokens
assert "computer" in tokens

print("✓ Tokenization passed")


# --------------------------------------------------
# 5. Test relevance
# --------------------------------------------------

print("\n[5] Testing relevance...")

test_chunk = {
    "text": (
        "Cyber security protects computer systems "
        "from cyber attacks and unauthorized access."
    )
}

score = calculate_relevance(
    "cyber security attacks",
    test_chunk
)

print("Relevance score:", score)

assert score > 0

print("✓ Relevance calculation passed")


# --------------------------------------------------
# 6. Test retrieval
# --------------------------------------------------

print("\n[6] Retrieving relevant chunks...")

query = "cyber security attacks"

results = retrieve_relevant_chunks(
    chunks,
    query,
    top_k=5
)

print("Retrieved chunks:", len(results))

assert len(results) > 0

print("✓ Retrieval returned results")


# --------------------------------------------------
# 7. Display results
# --------------------------------------------------

print("\n================================")
print("TOP RETRIEVED CHUNKS")
print("================================")

for result in results:

    print("\nChunk ID:", result["chunk_id"])
    print("Page:", result["page"])
    print("Chapter:", result["chapter"])
    print("Topic:", result["topic"])
    print("Relevance:", result["relevance_score"])

    print("Text:")
    print(result["text"][:500])
    print("...")


# --------------------------------------------------
# Final result
# --------------------------------------------------

print("\n================================")
print("RETRIEVER TEST PASSED")
print("================================")