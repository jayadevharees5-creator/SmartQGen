from modules.document_processor import extract_text_from_pdf
from modules.structure_detector import parse_document_structure
from modules.chunker import create_chunks_from_structure
from modules.retriever import retrieve_relevant_chunks
from modules.question_generator import generate_question_from_context


PDF_PATH = "uploads/sample.pdf"


print("================================")
print("ALL QUESTION TYPES TEST")
print("================================")


# ------------------------------------------------------------
# STEP 1: READ PDF
# ------------------------------------------------------------

print("\n[1] Reading PDF...")

extracted_doc = extract_text_from_pdf(PDF_PATH)

if not extracted_doc:
    raise SystemExit("ERROR: PDF extraction failed.")

print("Pages:", len(extracted_doc["pages"]))
print("Characters:", extracted_doc["total_characters"])


# ------------------------------------------------------------
# STEP 2: STRUCTURE
# ------------------------------------------------------------

print("\n[2] Detecting structure...")

structure_data = parse_document_structure(extracted_doc)

if not structure_data:
    raise SystemExit("ERROR: Structure detection failed.")

print("Structure items:", len(structure_data))


# ------------------------------------------------------------
# STEP 3: CHUNKS
# ------------------------------------------------------------

print("\n[3] Creating chunks...")

chunks = create_chunks_from_structure(
    extracted_doc,
    structure_data
)

if not chunks:
    raise SystemExit("ERROR: Chunk creation failed.")

print("Total chunks:", len(chunks))


# ------------------------------------------------------------
# STEP 4: RETRIEVAL
# ------------------------------------------------------------

print("\n[4] Retrieving context...")

retrieved_chunks = retrieve_relevant_chunks(
    chunks,
    "cyber security attacks",
    top_k=10
)

if not retrieved_chunks:
    raise SystemExit("ERROR: Retrieval failed.")

print("Retrieved chunks:", len(retrieved_chunks))


# ------------------------------------------------------------
# STEP 5: TEST QUESTION TYPES
# ------------------------------------------------------------

question_types = [
    "MCQ",
    "Fill in the Blank",
    "True/False",
    "Short Answer",
    "Long Answer",
]


for q_type in question_types:

    print("\n--------------------------------")
    print("Testing:", q_type)
    print("--------------------------------")

    question = generate_question_from_context(
        retrieved_chunks,
        q_type=q_type,
        difficulty="Medium",
        bloom_level="Understand",
        attempt_idx=0,
    )

    if not question:
        print("❌ FAILED: No question generated.")
        continue

    print("Question:")
    print(question.get("question"))

    print("Type:")
    print(question.get("type"))

    print("Answer:")
    print(
        question.get(
            "correct_answer",
            question.get("answer")
        )
    )

    # --------------------------------------------------------
    # Basic validation
    # --------------------------------------------------------

    if not question.get("question"):
        print("❌ FAILED: Empty question.")
        continue

    if not question.get("type"):
        print("❌ FAILED: Missing question type.")
        continue

    if not (
        question.get("correct_answer")
        or question.get("answer")
    ):
        print("❌ FAILED: Missing answer.")
        continue

    print("✅ PASSED")


print("\n================================")
print("ALL QUESTION TYPES TEST COMPLETED")
print("================================")