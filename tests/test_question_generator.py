from modules.document_processor import extract_text_from_pdf
from modules.structure_detector import parse_document_structure
from modules.chunker import create_chunks_from_structure
from modules.retriever import retrieve_relevant_chunks
from modules.question_generator import generate_question_from_context


PDF_PATH = "uploads/sample.pdf"


print("================================")
print("QUESTION GENERATOR TEST")
print("================================")


# ============================================================
# STEP 1: READ PDF
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
# STEP 2: DETECT DOCUMENT STRUCTURE
# ============================================================

print("\n[2] Detecting document structure...")

structure_data = parse_document_structure(extracted_doc)

if not structure_data:
    print("ERROR: Document structure detection failed.")
    raise SystemExit(1)

print("Structure items:", len(structure_data))


# ============================================================
# STEP 3: CREATE CHUNKS
# ============================================================

print("\n[3] Creating chunks...")

chunks = create_chunks_from_structure(
    extracted_doc,
    structure_data
)

if not chunks:
    print("ERROR: Chunk creation failed.")
    raise SystemExit(1)

print("Total chunks:", len(chunks))


# ============================================================
# STEP 4: RETRIEVE RELEVANT CHUNKS
# ============================================================

print("\n[4] Retrieving relevant chunks...")

query = "cyber security attacks"

# MCQ generation needs a sufficiently large candidate pool.
retrieved_chunks = retrieve_relevant_chunks(
    chunks,
    query,
    top_k=10
)

print("Retrieved chunks:", len(retrieved_chunks))

if not retrieved_chunks:
    print("ERROR: No relevant chunks were retrieved.")
    raise SystemExit(1)


# ============================================================
# DISPLAY RETRIEVED CHUNKS
# ============================================================

print("\nRetrieved Context:")

for index, chunk in enumerate(
    retrieved_chunks,
    start=1
):
    print(
        f"\n--- Chunk {index} ---"
    )

    print(
        "Page:",
        chunk.get("page")
    )

    print(
        "Chapter:",
        chunk.get("chapter")
    )

    print(
        "Topic:",
        chunk.get("topic")
    )

    print(
        "Relevance:",
        chunk.get("relevance_score")
    )


# ============================================================
# STEP 5: GENERATE QUESTION
# ============================================================

print("\n[5] Generating question...")

question = generate_question_from_context(
    retrieved_chunks,
    q_type="MCQ",
    difficulty="Medium",
    bloom_level="Understand",
    attempt_idx=0
)


# ============================================================
# STEP 6: VALIDATE QUESTION
# ============================================================

print("\n================================")
print("GENERATED QUESTION")
print("================================")


if not question:

    print(
        "ERROR: Question generation returned None."
    )

    raise SystemExit(1)


question_text = question.get(
    "question"
)

question_type = question.get(
    "type"
)

options = question.get(
    "options",
    []
)

correct_answer = question.get(
    "correct_answer"
)


# ============================================================
# BASIC VALIDATION
# ============================================================

if not question_text:
    print("ERROR: Question text is empty.")
    raise SystemExit(1)


if question_type != "MCQ":
    print(
        "ERROR: Expected MCQ but received:",
        question_type
    )
    raise SystemExit(1)


if not isinstance(options, list):
    print("ERROR: Options are not a list.")
    raise SystemExit(1)


if len(options) != 4:
    print(
        "ERROR: MCQ must contain exactly 4 options."
    )

    print(
        "Received options:",
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
        "ERROR: MCQ contains duplicate options."
    )

    raise SystemExit(1)


if not correct_answer:
    print(
        "ERROR: Correct answer is missing."
    )

    raise SystemExit(1)


# ============================================================
# DISPLAY RESULT
# ============================================================

print(
    "Question:",
    question.get("question")
)

print(
    "Type:",
    question.get("type")
)

print(
    "Options:",
    question.get("options")
)

print(
    "Correct Answer:",
    question.get("correct_answer")
)

print(
    "Difficulty:",
    question.get("difficulty")
)

print(
    "Bloom Level:",
    question.get("bloom_level")
)

print(
    "Source Page:",
    question.get("source_page")
)

print(
    "Source Chapter:",
    question.get("source_chapter")
)

print(
    "Source Topic:",
    question.get("source_topic")
)

print(
    "Quality Score:",
    question.get("quality_score")
)


# ============================================================
# SUCCESS
# ============================================================

print("\n================================")
print("QUESTION GENERATOR TEST PASSED")
print("================================")