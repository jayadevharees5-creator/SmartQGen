from modules.document_processor import extract_text_from_pdf
from modules.structure_detector import parse_document_structure
from modules.chunker import create_chunks_from_structure

from modules.question_paper_generator import (
    generate_question_paper,
    print_question_paper
)


PDF_PATH = "uploads/sample.pdf"


print("================================")
print("QUESTION PAPER GENERATOR TEST")
print("================================")


# ============================================================
# 1. READ PDF
# ============================================================

print("\n[1] Reading PDF...")

extracted_doc = extract_text_from_pdf(PDF_PATH)

if not extracted_doc:
    print("ERROR: PDF extraction failed.")
    raise SystemExit(1)

print("Source:", extracted_doc["source"])
print("Pages:", len(extracted_doc["pages"]))
print("Characters:", extracted_doc["total_characters"])


# ============================================================
# 2. DETECT STRUCTURE
# ============================================================

print("\n[2] Detecting document structure...")

structure_data = parse_document_structure(
    extracted_doc
)

if not structure_data:
    print("ERROR: Structure detection failed.")
    raise SystemExit(1)

print(
    "Structure items:",
    len(structure_data)
)


# ============================================================
# 3. CREATE CHUNKS
# ============================================================

print("\n[3] Creating chunks...")

chunks = create_chunks_from_structure(
    extracted_doc,
    structure_data
)

if not chunks:
    print("ERROR: Chunk creation failed.")
    raise SystemExit(1)

print(
    "Total chunks:",
    len(chunks)
)


# ============================================================
# 4. GENERATE QUESTION PAPER
# ============================================================

print("\n[4] Generating question paper...")

paper = generate_question_paper(
    chunks=chunks,
    num_questions=5,
    q_type="MCQ",
    difficulty="Medium",
    bloom_level="Understand",
    query="cyber security attacks",
    retrieval_top_k=10
)


# ============================================================
# 5. CHECK RESULT
# ============================================================

if not paper:
    print(
        "ERROR: Question paper generation returned None."
    )
    raise SystemExit(1)


print("\nGeneration completed.")

print(
    "Requested questions:",
    paper.get("requested_questions")
)

print(
    "Generated questions:",
    paper.get("total_questions")
)

print(
    "Success:",
    paper.get("success")
)


# ============================================================
# 6. VALIDATE NUMBER OF QUESTIONS
# ============================================================

questions = paper.get(
    "questions",
    []
)

if len(questions) != 5:

    print(
        "\nERROR: Expected 5 questions."
    )

    print(
        "Generated:",
        len(questions)
    )

    if paper.get("error"):
        print(
            "Reason:",
            paper.get("error")
        )

    raise SystemExit(1)


# ============================================================
# 7. VALIDATE EACH QUESTION
# ============================================================

print("\n[5] Validating generated questions...")

for index, question in enumerate(
    questions,
    start=1
):

    print(
        f"Checking Question {index}..."
    )

    if not question.get("question"):
        print(
            f"ERROR: Question {index} "
            "has no question text."
        )
        raise SystemExit(1)

    if question.get("type") != "MCQ":

        print(
            f"ERROR: Question {index} "
            "is not MCQ."
        )

        print(
            "Received type:",
            question.get("type")
        )

        raise SystemExit(1)

    options = question.get(
        "options",
        []
    )

    if len(options) != 4:

        print(
            f"ERROR: Question {index} "
            "does not have exactly 4 options."
        )

        print(
            "Options:",
            options
        )

        raise SystemExit(1)

    if len(
        set(
            str(option).strip().lower()
            for option in options
        )
    ) != 4:

        print(
            f"ERROR: Question {index} "
            "contains duplicate options."
        )

        raise SystemExit(1)

    if not question.get("correct_answer"):

        print(
            f"ERROR: Question {index} "
            "has no correct answer."
        )

        raise SystemExit(1)


# ============================================================
# 8. PRINT COMPLETE PAPER
# ============================================================

print("\n[6] Generated Question Paper:")

print_question_paper(
    paper
)


# ============================================================
# 9. FINAL RESULT
# ============================================================

print("\n================================")
print("QUESTION PAPER GENERATOR TEST PASSED")
print("================================")