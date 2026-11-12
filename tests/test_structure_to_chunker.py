from modules.document_processor import extract_text_from_pdf
from modules.structure_detector import parse_document_structure
from modules.chunker import create_chunks_from_structure


PDF_PATH = "uploads/sample.pdf"


print("================================")
print("STRUCTURE → CHUNKER INTEGRATION TEST")
print("================================")


# ============================================================
# STEP 1: DOCUMENT PROCESSOR
# ============================================================

print("\n[1] Reading PDF...")

extracted_doc = extract_text_from_pdf(PDF_PATH)

print("Source:", extracted_doc["source"])
print("Pages:", len(extracted_doc["pages"]))
print("Characters:", extracted_doc["total_characters"])


# ============================================================
# STEP 2: STRUCTURE DETECTOR
# ============================================================

print("\n[2] Detecting document structure...")

structure_data = parse_document_structure(extracted_doc)

print("Structure items:",
      len(structure_data["structure_map"]))

print("Detected chapters:",
      len(structure_data["detected_chapters"]))


# ============================================================
# STEP 3: CHUNKER
# ============================================================

print("\n[3] Creating chunks...")

chunks = create_chunks_from_structure(
    extracted_doc,
    structure_data
)

print("Total chunks:", len(chunks))


# ============================================================
# STEP 4: DISPLAY RESULT
# ============================================================

if chunks:

    print("\n================================")
    print("FIRST GENERATED CHUNK")
    print("================================")

    first_chunk = chunks[0]

    print("Chunk ID:", first_chunk["chunk_id"])
    print("Document:", first_chunk["document_id"])
    print("Page:", first_chunk["page"])
    print("Chapter:", first_chunk["chapter"])
    print("Chapter Title:", first_chunk["chapter_title"])
    print("Topic:", first_chunk["topic"])
    print("Word Count:", first_chunk["word_count"])

    print("\nText:")
    print(first_chunk["text"][:1000])


    print("\n================================")
    print("INTEGRATION TEST PASSED")
    print("================================")

else:

    print("\n================================")
    print("INTEGRATION TEST FAILED")
    print("No chunks were generated.")
    print("================================")