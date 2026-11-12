from modules.document_processor import extract_document
from modules.structure_detector import parse_document_structure
from modules.chunker import create_chunks_from_structure
from modules.retriever import retrieve_relevant_chunks
from modules.question_paper_generator import generate_question_paper


PDF_PATH = "uploads/sample.pdf"


print("=" * 60)
print("QUESTION QUALITY TEST")
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
# 4. RETRIEVE RELEVANT CONTENT
# ------------------------------------------------------------

query = "virus worm phishing malware"

print("\n[4] Retrieving relevant content...")
print("Query:", query)

retrieved_chunks = retrieve_relevant_chunks(
    chunks,
    query,
    top_k=5
)

print("Retrieved chunks:", len(retrieved_chunks))


# ------------------------------------------------------------
# 5. DISPLAY RETRIEVED CONTEXT
# ------------------------------------------------------------

print("\n[5] Retrieved Context")
print("-" * 60)

for i, chunk in enumerate(retrieved_chunks, start=1):

    print(f"\n--- Retrieved Chunk {i} ---")

    print(
        "Page:",
        chunk.get(
            "page",
            chunk.get("page_number", "N/A")
        )
    )

    print(
        "Chapter:",
        chunk.get("chapter", "")
    )

    print(
        "Topic:",
        chunk.get("topic", "")
    )

    print("Text:")

    text = chunk.get("text", "")

    print(text[:500])


# ------------------------------------------------------------
# 6. GENERATE QUESTION PAPER
# ------------------------------------------------------------

print("\n[6] Generating MCQ question paper...")

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
# 7. DISPLAY GENERATED QUESTIONS
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("GENERATED QUESTION PAPER")
print("=" * 60)

if paper and isinstance(paper, dict):

    print("\nPaper generated successfully.")

    print("\nTotal Questions:")
    print(paper.get("total_questions"))

    print("\nRequested Questions:")
    print(paper.get("requested_questions"))

    questions = paper.get("questions", [])

    print("\nGenerated Questions:")
    print("-" * 60)

    for i, question in enumerate(questions, start=1):

        print(f"\nQuestion {i}:")

        print(
            "Question:",
            question.get("question", "")
        )

        print("\nOptions:")

        options = question.get("options", [])

        for option_number, option in enumerate(
            options,
            start=1
        ):
            print(
                f"({chr(64 + option_number)}) {option}"
            )

        print(
            "\nCorrect Answer:",
            question.get(
                "correct_answer",
                question.get("answer", "")
            )
        )

        print(
            "Concept:",
            question.get("concept", "")
        )

        print(
            "Difficulty:",
            question.get("difficulty", "")
        )

        print(
            "Bloom Level:",
            question.get("bloom_level", "")
        )

        print(
            "Generation Method:",
            question.get("generation_method", "")
        )

        print(
            "Quality Score:",
            question.get("quality_score", "")
        )

        print(
            "Source Page:",
            question.get("source_page", "")
        )

else:

    print("\nQuestion paper generation failed.")

    print("Result:", paper)


# ------------------------------------------------------------
# 8. TEST COMPLETED
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("QUESTION QUALITY TEST COMPLETED")
print("=" * 60)