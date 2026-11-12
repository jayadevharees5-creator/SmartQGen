from modules.document_processor import extract_text_from_pdf
from modules.text_cleaner import clean_raw_text
from modules.chunker import create_chunks_from_structure


PDF_PATH = "uploads/sample.pdf"

print("================================")
print("CHUNKER TEST")
print("================================")


# 1. Read PDF
print("\nReading PDF...")

extracted_doc = extract_text_from_pdf(PDF_PATH)

print("Characters extracted:", extracted_doc["total_characters"])

# Extract actual text from all pages
raw_text = "\n".join(
    page["text"] for page in extracted_doc["pages"]
)

print("Pages extracted:", len(extracted_doc["pages"]))


# 2. Clean text
print("\nCleaning text...")

cleaned_text = clean_raw_text(raw_text)

print("Characters after cleaning:", len(cleaned_text))


# 3. Create sample structure map
print("\nPreparing structure data...")

words = cleaned_text.split()

structure_map = []

# Divide text into groups of 100 words
for i in range(0, len(words), 100):

    text = " ".join(words[i:i + 100])

    structure_map.append({
        "text": text,
        "page": 1,
        "chapter": "UNIT-I",
        "chapter_title": "Introduction to Cyber Security",
        "topic": "Cyber Security"
    })


structure_data = {
    "structure_map": structure_map
}

print("Structure items:", len(structure_map))


# 4. Create chunks
print("\nCreating chunks...")

chunks = create_chunks_from_structure(
    extracted_doc,
    structure_data
)

print("Total chunks:", len(chunks))


# 5. Display first chunk
if chunks:

    print("\n================================")
    print("FIRST CHUNK")
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
    print("CHUNKER TEST COMPLETED")
    print("================================")

else:

    print("\nNo chunks were created.")

    print("\n================================")
    print("CHUNKER TEST FAILED")
    print("================================")
    raise SystemExit(1)


# 6. Test expand_chunk_context
print("\n================================")
print("TESTING CHUNK CONTEXT EXPANSION")
print("================================")

from modules.chunker import expand_chunk_context

target_chunk = chunks[0]

expanded_context = expand_chunk_context(
    chunks,
    target_chunk,
    window_size=1
)

print("Target Chunk:", target_chunk["chunk_id"])
print("Expanded Context Characters:", len(expanded_context))

print("\nExpanded Context:")
print(expanded_context[:1500])

print("\n================================")
print("CHUNKER TEST COMPLETED")
print("================================")