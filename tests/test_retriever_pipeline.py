from modules.document_processor import extract_document
from modules.structure_detector import parse_document_structure
from modules.chunker import create_chunks_from_structure
from modules.retriever import retrieve_relevant_chunks


FILE_PATH = "uploads/sample.pdf"


print("=" * 60)
print("RETRIEVER PIPELINE TEST")
print("=" * 60)


# ------------------------------------------------------------
# 1. Extract document
# ------------------------------------------------------------

print("\n[1] Extracting document...")

document = extract_document(FILE_PATH)

print("Source:", document.get("source"))
print("Pages:", len(document.get("pages", [])))
print("Characters:", document.get("total_characters"))


# ------------------------------------------------------------
# 2. Detect structure
# ------------------------------------------------------------

print("\n[2] Detecting structure...")

structure = parse_document_structure(document)

print(
    "Structure items:",
    len(structure.get("structure_map", []))
)


# ------------------------------------------------------------
# 3. Create chunks
# ------------------------------------------------------------

print("\n[3] Creating chunks...")

chunks = create_chunks_from_structure(
    document,
    structure
)

print("Total chunks:", len(chunks))


if not chunks:
    print("\nERROR: No chunks available.")
    exit()


# ------------------------------------------------------------
# 4. Multiple retrieval queries
# ------------------------------------------------------------

queries = [
    "types of cyber attacks and cyber threats",
    "cyber security basic concepts",
    "CIA triad confidentiality integrity availability",
    "cyber warfare cyber crime cyber terrorism",
    "phishing malware virus worm",
    "denial of service attacks"
]


# ------------------------------------------------------------
# 5. Test every query
# ------------------------------------------------------------

for query_number, query in enumerate(queries, start=1):

    print("\n")
    print("=" * 60)
    print(f"QUERY {query_number}")
    print("=" * 60)

    print("\nRetrieval query:")
    print(query)

    print("\nRetrieving relevant chunks...")

    retrieved_chunks = retrieve_relevant_chunks(
        chunks,
        query,
        top_k=5
    )

    print("\nRetrieved chunks:", len(retrieved_chunks))

    # --------------------------------------------------------
    # Display retrieved chunks
    # --------------------------------------------------------

    for index, chunk in enumerate(retrieved_chunks, start=1):

        print(f"\n--- Retrieved Chunk {index} ---")

        print("Chunk ID:", chunk.get("chunk_id"))
        print("Page:", chunk.get("page"))
        print("Chapter:", chunk.get("chapter"))
        print("Topic:", chunk.get("topic"))
        print("Word count:", chunk.get("word_count"))

        text = chunk.get("text", "")

        print("\nText:")
        print(text[:800])

        print("\n" + "-" * 60)


# ------------------------------------------------------------
# 6. Test completed
# ------------------------------------------------------------

print("\n")
print("=" * 60)
print("MULTI-QUERY RETRIEVER TEST COMPLETED")
print("=" * 60)