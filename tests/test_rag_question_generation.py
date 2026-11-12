from modules.document_processor import extract_document
from modules.structure_detector import parse_document_structure
from modules.chunker import create_chunks_from_structure
from modules.retriever import retrieve_relevant_chunks
from modules.question_paper_generator import generate_question_paper

PDF_PATH = "uploads/sample.pdf"


print("=" * 60)
print("RAG QUESTION GENERATION TEST")
print("=" * 60)


# ------------------------------------------------------------
# 1. EXTRACT DOCUMENT
# ------------------------------------------------------------

print("\n[1] Extracting document...")

document = extract_document(PDF_PATH)

print("Source:", document["source"])
print("Pages:", len(document["pages"]))
print("Characters:", document["total_characters"])


# ------------------------------------------------------------
# 2. DETECT STRUCTURE
# ------------------------------------------------------------

print("\n[2] Detecting structure...")

structure = parse_document_structure(document)

print(
    "Structure items:",
    len(structure.get("structure_map", []))
)


# ------------------------------------------------------------
# 3. CREATE CHUNKS
# ------------------------------------------------------------

print("\n[3] Creating chunks...")

chunks = create_chunks_from_structure(
    document,
    structure
)

print("Total chunks:", len(chunks))


# ------------------------------------------------------------
# 4. RETRIEVE RELEVANT CHUNKS
# ------------------------------------------------------------

query = "phishing malware virus worm"

print("\n[4] Retrieving relevant chunks...")
print("Query:", query)

retrieved_chunks = retrieve_relevant_chunks(
    chunks,
    query,
    top_k=5
)

print(
    "Retrieved chunks:",
    len(retrieved_chunks)
)


# ------------------------------------------------------------
# 5. DISPLAY RETRIEVED CONTEXT
# ------------------------------------------------------------

print("\n[5] Retrieved Context")
print("-" * 60)

for i, chunk in enumerate(retrieved_chunks, start=1):

    print(f"\n--- Retrieved Chunk {i} ---")

    print(
        "Page:",
        chunk.get("page", chunk.get("page_number", "N/A"))
    )

    print(
        "Chapter:",
        chunk.get("chapter", "")
    )

    print(
        "Topic:",
        chunk.get("topic", "")
    )

    text = chunk.get("text", "")

    print("Text:")
    print(text[:500])


# ------------------------------------------------------------
# 6. GENERATE QUESTION PAPER
# ------------------------------------------------------------

print("\n[6] Generating question paper...")

paper = generate_question_paper(
    retrieved_chunks,
    num_questions=3,
    q_type="MCQ",
    difficulty="Medium",
    bloom_level="Understand",
    query=query,
    chapter=None,
    topic=None,
    retrieval_top_k=5
)


# ------------------------------------------------------------
# 7. DISPLAY RESULT
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("GENERATED QUESTION PAPER")
print("=" * 60)

if paper:

    print("\nPaper type:", type(paper).__name__)

    if isinstance(paper, dict):

        print("\nKeys:")
        print(list(paper.keys()))

        print("\nGenerated Questions:")

        questions = paper.get("questions", [])

        for i, question in enumerate(questions, start=1):

            print(f"\nQuestion {i}:")
            print(question)

    else:

        print(paper)

else:

    print("Question paper generation failed.")


print("\n" + "=" * 60)
print("RAG QUESTION GENERATION TEST COMPLETED")
print("=" * 60)