# modules/question_paper_generator.py
# Smart Q Gen
# ============================================================
# QUESTION PAPER GENERATOR
#
# Flow:
#
# Complete Document
#       ↓
# Hybrid Retrieval
#       ↓
# 30 Relevant Chunks
#       ↓
# Context / Concept Pool
#       ↓
# Question Generation
#       ↓
# Validation
#       ↓
# Duplicate Check
#       ↓
# Final Question Paper
#
# IMPORTANT:
# No manual Unit / Topic / Chapter selection.
# ============================================================

import re
from typing import Any, Dict, List


from modules.question_generator import (
    generate_question_from_context
)


# ============================================================
# SUPPORTED QUESTION TYPES
# ============================================================

QUESTION_TYPES = [
    "MCQ",
    "FILL_IN_THE_BLANKS",
    "TRUE_FALSE",
    "SHORT_ANSWER",
    "LONG_ANSWER",
]


# ============================================================
# DEFAULT VALUES
# ============================================================

DEFAULT_QUESTION_TYPE = "MCQ"

DEFAULT_DIFFICULTY = "Medium"

DEFAULT_BLOOM_LEVEL = "Understand"

# IMPORTANT:
# The old value was 10.
# We now retrieve a much broader context.
DEFAULT_RETRIEVAL_TOP_K = 30

# Number of generation attempts.
# This is only a safety limit.
# It is NOT the main generation strategy.
MAX_ATTEMPTS_MULTIPLIER = 8

MINIMUM_MAX_ATTEMPTS = 60


# ============================================================
# BAD QUESTION FRAGMENTS
# ============================================================

BAD_QUESTION_FRAGMENTS = {
    "what is the main concept",
    "what is it",
    "what is this",
    "what is that",
    "according to the prompt",
    "according to the document",
    "according to the source",
    "according to the study material",
    "two words that make up",
    "as an ai",
    "i cannot",
}


# ============================================================
# BAD GENERIC TERMS
# ============================================================

BAD_GENERIC_TERMS = {
    "it",
    "this",
    "that",
    "these",
    "those",
    "what",
    "which",
    "who",
    "when",
    "where",
    "why",
    "how",
    "data",
    "information",
    "system",
    "process",
    "method",
    "thing",
    "things",
    "example",
    "examples",
    "people",
    "users",
    "others",
    "now",
    "term",
    "concept",
    "general",
    "etc",
}


# ============================================================
# QUESTION TYPE NORMALIZATION
# ============================================================

def normalize_question_type(q_type):

    if not q_type:

        return DEFAULT_QUESTION_TYPE

    value = str(
        q_type
    ).strip().upper()

    aliases = {

        "ALL": "ALL",

        "MCQ": "MCQ",

        "MULTIPLE_CHOICE": "MCQ",

        "MULTIPLE CHOICE": "MCQ",

        "MULTIPLE CHOICE QUESTIONS": "MCQ",

        "FILL": "FILL_IN_THE_BLANKS",

        "FILL_BLANK": "FILL_IN_THE_BLANKS",

        "FILL_BLANKS": "FILL_IN_THE_BLANKS",

        "FILL_IN_THE_BLANK": "FILL_IN_THE_BLANKS",

        "FILL_IN_THE_BLANKS": "FILL_IN_THE_BLANKS",

        "FILL IN THE BLANK": "FILL_IN_THE_BLANKS",

        "FILL IN THE BLANKS": "FILL_IN_THE_BLANKS",

        "TRUE_FALSE": "TRUE_FALSE",

        "TRUE / FALSE": "TRUE_FALSE",

        "TRUE/FALSE": "TRUE_FALSE",

        "TRUE OR FALSE": "TRUE_FALSE",

        "SHORT": "SHORT_ANSWER",

        "SHORT_ANSWER": "SHORT_ANSWER",

        "SHORT ANSWER": "SHORT_ANSWER",

        "LONG": "LONG_ANSWER",

        "LONG_ANSWER": "LONG_ANSWER",

        "LONG ANSWER": "LONG_ANSWER",
    }

    return aliases.get(
        value,
        value
    )


# ============================================================
# DIFFICULTY NORMALIZATION
# ============================================================

def normalize_difficulty(
    difficulty
):

    if not difficulty:

        return DEFAULT_DIFFICULTY

    value = str(
        difficulty
    ).strip().capitalize()

    allowed = {
        "Easy",
        "Medium",
        "Hard"
    }

    if value not in allowed:

        return DEFAULT_DIFFICULTY

    return value


# ============================================================
# BLOOM LEVEL NORMALIZATION
# ============================================================

def normalize_bloom_level(
    bloom_level
):

    if not bloom_level:

        return DEFAULT_BLOOM_LEVEL

    value = str(
        bloom_level
    ).strip().capitalize()

    allowed = {
        "Remember",
        "Understand",
        "Apply",
        "Analyze",
        "Evaluate",
        "Create"
    }

    if value not in allowed:

        return DEFAULT_BLOOM_LEVEL

    return value


# ============================================================
# QUESTION NORMALIZATION
# ============================================================

def normalize_question(
    text
):

    if not text:

        return ""

    text = str(
        text
    ).lower().strip()

    text = re.sub(
        r"^q\s*\d+\s*[\.\):\-]?\s*",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


# ============================================================
# DUPLICATE QUESTION CHECK
# ============================================================

def is_duplicate_question(
    question,
    existing_questions
):

    if not isinstance(
        question,
        dict
    ):

        return True

    new_question = normalize_question(
        question.get(
            "question",
            ""
        )
    )

    if not new_question:

        return True

    for existing in existing_questions:

        old_question = normalize_question(
            existing.get(
                "question",
                ""
            )
        )

        if new_question == old_question:

            return True

    return False


# ============================================================
# CONCEPT NORMALIZATION
# ============================================================

def _normalize_concept(
    value
):

    value = str(
        value or ""
    ).strip()

    value = re.sub(
        r"^\s*(?:\d+(?:\.\d+)*[.)-]?|[-*•])\s*",
        "",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    value = value.strip(
        " .,:;!?-"
    )

    return value


# ============================================================
# CONCEPT VALIDATION
# ============================================================

def _valid_concept(
    concept
):

    concept = _normalize_concept(
        concept
    )

    if not concept:

        return False

    lower = concept.casefold()

    if lower in BAD_GENERIC_TERMS:

        return False

    bad_fragments = [
        "data that",
        "term ",
        "up of two words",
        "listed below",
        "listed above",
        "for example",
        "such as",
        "the following",
        "or cyber",
        "and cyber",
        "main concept",
        "it also",
        "whereby a",
        "what is",
        "which is",
        "how to",
        "why ",
        "because ",
    ]

    for phrase in bad_fragments:

        if phrase in lower:

            return False

    # Concepts should be short.
    if len(
        concept.split()
    ) > 5:

        return False

    # Reject sentence-like concepts.
    if re.search(
        r"\b(?:is|are|was|were|that|which|who|when|where|because|include|includes|including)\b",
        lower
    ):

        return False

    # Reject bad beginnings.
    if lower.startswith(
        (
            "or ",
            "and ",
            "but ",
            "because ",
            "which ",
            "what ",
            "when ",
            "where ",
            "how ",
            "why ",
            "this ",
            "that ",
            "it ",
        )
    ):

        return False

    if not re.search(
        r"[A-Za-z]",
        concept
    ):

        return False

    return True


# ============================================================
# EXTRACT CONCEPTS FROM CHUNKS
# ============================================================

def extract_context_concepts(
    chunks
):

    concepts = []

    seen = set()

    def add_concept(value):

        value = _normalize_concept(
            value
        )

        if not _valid_concept(
            value
        ):

            return

        key = value.casefold()

        if key in seen:

            return

        seen.add(
            key
        )

        concepts.append(
            value
        )

    for chunk in chunks:

        if not isinstance(
            chunk,
            dict
        ):

            continue

        # ----------------------------------------------------
        # Explicit topics
        # ----------------------------------------------------

        topic = chunk.get(
            "topic"
        )

        if topic:

            add_concept(
                topic
            )

        # ----------------------------------------------------
        # Extracted topics list
        # ----------------------------------------------------

        topics = chunk.get(
            "topics",
            []
        )

        if isinstance(
            topics,
            list
        ):

            for topic in topics:

                add_concept(
                    topic
                )

        # ----------------------------------------------------
        # Unit title
        # ----------------------------------------------------

        unit_title = chunk.get(
            "unit_title"
        )

        if unit_title:

            add_concept(
                unit_title
            )

    return concepts


# ============================================================
# BUILD CONTEXT POOL
# ============================================================

def build_context_pool(
    retrieved_chunks
):

    """
    Create an ordered context pool.

    The pool is intentionally broader than the number
    of requested questions.

    Example:

        10 questions
        ↓
        30 retrieved chunks
        ↓
        broad context pool
    """

    if not retrieved_chunks:

        return []

    pool = []

    seen = set()

    for chunk in retrieved_chunks:

        if not isinstance(
            chunk,
            dict
        ):

            continue

        text = str(
            chunk.get(
                "text",
                ""
            )
        ).strip()

        if not text:

            continue

        # Prefer chunk_id when available.
        chunk_id = chunk.get(
            "chunk_id"
        )

        if chunk_id is not None:

            key = (
                "id",
                str(chunk_id)
            )

        else:

            key = (
                "text",
                normalize_question(
                    text
                )
            )

        if key in seen:

            continue

        seen.add(
            key
        )

        pool.append(
            chunk
        )

    return pool


# ============================================================
# BUILD QUESTION-SPECIFIC CONTEXT
# ============================================================

def build_question_context(
    context_pool,
    question_index,
    total_questions
):

    if not context_pool:

        return []

    total_chunks = len(
        context_pool
    )

    # --------------------------------------------------------
    # Rotate through the entire pool.
    #
    # This prevents every question from using the same
    # first chunk.
    # --------------------------------------------------------

    primary_index = (
        question_index
        % total_chunks
    )

    selected = [
        context_pool[
            primary_index
        ]
    ]

    # --------------------------------------------------------
    # Add a nearby chunk for additional grounding.
    # --------------------------------------------------------

    if total_chunks > 1:

        next_index = (
            primary_index + 1
        ) % total_chunks

        if next_index != primary_index:

            selected.append(
                context_pool[
                    next_index
                ]
            )

    # --------------------------------------------------------
    # Add previous chunk.
    # --------------------------------------------------------

    if total_chunks > 2:

        previous_index = (
            primary_index - 1
        ) % total_chunks

        if (
            previous_index
            != primary_index
        ):

            if context_pool[
                previous_index
            ] not in selected:

                selected.append(
                    context_pool[
                        previous_index
                    ]
                )

    return selected


# ============================================================
# QUESTION VALIDATION
# ============================================================

def validate_question(
    question,
    expected_type=None
):

    if not isinstance(
        question,
        dict
    ):

        return False

    question_text = str(
        question.get(
            "question",
            ""
        )
    ).strip()

    if not question_text:

        return False

    words = question_text.split()

    if len(words) < 5:

        return False

    if len(words) > 80:

        return False

    lower_question = (
        question_text.casefold()
    )

    # ========================================================
    # BAD MODEL OUTPUT
    # ========================================================

    for phrase in BAD_QUESTION_FRAGMENTS:

        if phrase in lower_question:

            return False

    if lower_question.startswith(
        (
            "or ",
            "and ",
            "because ",
            "including ",
        )
    ):

        return False

    # ========================================================
    # QUESTION TYPE
    # ========================================================

    question_type = normalize_question_type(
        question.get(
            "type"
        )
    )

    if question_type == "ALL":

        return False

    # ========================================================
    # EXPECTED TYPE
    # ========================================================

    if expected_type:

        expected_type = normalize_question_type(
            expected_type
        )

        if question_type != expected_type:

            return False

    # ========================================================
    # CONCEPT
    # ========================================================

    concept = _normalize_concept(
        question.get(
            "concept",
            ""
        )
    )

    if concept and not _valid_concept(
        concept
    ):

        return False

    # ========================================================
    # MCQ
    # ========================================================

    if question_type == "MCQ":

        options = question.get(
            "options",
            []
        )

        if not isinstance(
            options,
            list
        ):

            return False

        if len(options) != 4:

            return False

        cleaned_options = []

        for option in options:

            if option is None:

                return False

            option_text = str(
                option
            ).strip()

            if not option_text:

                return False

            if len(
                option_text.split()
            ) > 8:

                return False

            option_lower = (
                option_text.casefold()
            )

            if option_lower in {
                "it",
                "what",
                "this",
                "that",
                "these",
                "those",
                "or",
                "and",
                "the",
                "a",
                "an",
                "security",
                "cyber",
                "information",
            }:

                return False

            if option_lower.startswith(
                (
                    "or ",
                    "and ",
                    "what ",
                    "this ",
                    "that ",
                )
            ):

                return False

            cleaned_options.append(
                option_lower
            )

        if len(
            set(cleaned_options)
        ) != 4:

            return False

        correct_answer = str(
            question.get(
                "correct_answer",
                ""
            )
        ).strip()

        if not correct_answer:

            return False

        if (
            correct_answer.casefold()
            not in cleaned_options
        ):

            return False

        return True

    # ========================================================
    # FILL IN THE BLANK
    # ========================================================

    if question_type == "FILL_IN_THE_BLANKS":

        answer = question.get(
            "correct_answer"
        )

        if not answer:

            answer = question.get(
                "answer"
            )

        if not answer:

            return False

        if not str(
            answer
        ).strip():

            return False

        if (
            "____" not in question_text
            and "___" not in question_text
        ):

            return False

        return True

    # ========================================================
    # TRUE / FALSE
    # ========================================================

    if question_type == "TRUE_FALSE":

        answer = question.get(
            "correct_answer"
        )

        if not answer:

            return False

        answer = str(
            answer
        ).strip().casefold()

        if answer not in {
            "true",
            "false"
        }:

            return False

        if "?" in question_text:

            return False

        return True

    # ========================================================
    # SHORT ANSWER
    # ========================================================

    if question_type == "SHORT_ANSWER":

        answer = question.get(
            "answer"
        )

        if not answer:

            answer = question.get(
                "correct_answer"
            )

        if not answer:

            return False

        return bool(
            str(answer).strip()
        )

    # ========================================================
    # LONG ANSWER
    # ========================================================

    if question_type == "LONG_ANSWER":

        answer = question.get(
            "answer"
        )

        if not answer:

            answer = question.get(
                "correct_answer"
            )

        if not answer:

            return False

        return bool(
            str(answer).strip()
        )

    return False


# ============================================================
# RETRIEVAL
# ============================================================

def retrieve_question_context(
    chunks,
    query="",
    top_k=DEFAULT_RETRIEVAL_TOP_K
):

    if not chunks:

        print(
            "[QP] No document chunks available."
        )

        return []

    retrieval_query = str(
        query or ""
    ).strip()

    if not retrieval_query:

        retrieval_query = (
            "important concepts definitions "
            "principles methods applications "
            "key information"
        )

    print()
    print(
        "[QP] Retrieving broad context..."
    )

    print(
        "[QP] Query:",
        retrieval_query
    )

    print(
        "[QP] Available chunks:",
        len(chunks)
    )

    from modules.retriever import (
        retrieve_relevant_chunks
    )

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Retrieve more than the number of questions.
    # --------------------------------------------------------

    top_k = max(
        int(top_k),
        DEFAULT_RETRIEVAL_TOP_K
    )

    retrieved_chunks = (
        retrieve_relevant_chunks(
            chunks=chunks,
            query=retrieval_query,
            top_k=top_k
        )
    )

    print(
        "[QP] Retrieved chunks:",
        len(retrieved_chunks)
    )

    return retrieved_chunks


# ============================================================
# GENERATE SINGLE QUESTION
# ============================================================

def generate_single_question(
    context_chunks,
    q_type="MCQ",
    difficulty="Medium",
    bloom_level="Understand",
    attempt_idx=0
):

    if not context_chunks:

        return None

    q_type = normalize_question_type(
        q_type
    )

    difficulty = normalize_difficulty(
        difficulty
    )

    bloom_level = normalize_bloom_level(
        bloom_level
    )

    if q_type == "ALL":

        print(
            "[QP] ERROR: ALL reached "
            "generate_single_question."
        )

        return None

    if q_type not in QUESTION_TYPES:

        print(
            "[QP] Unsupported question type:",
            q_type
        )

        return None

    question = (
        generate_question_from_context(
            context_chunks,

            q_type=q_type,

            difficulty=difficulty,

            bloom_level=bloom_level,

            attempt_idx=attempt_idx
        )
    )

    if not question:

        return None

    generated_type = normalize_question_type(
        question.get(
            "type"
        )
    )

    question["type"] = (
        generated_type
    )

    if not validate_question(
        question,
        expected_type=q_type
    ):

        print(
            "[QP] Generated question "
            "failed validation."
        )

        return None

    return question


# ============================================================
# SELECT QUESTION TYPE
# ============================================================

def select_question_type(
    requested_type,
    question_number
):

    requested_type = normalize_question_type(
        requested_type
    )

    if requested_type != "ALL":

        return requested_type

    index = (
        question_number - 1
    ) % len(
        QUESTION_TYPES
    )

    return QUESTION_TYPES[
        index
    ]


# ============================================================
# CONCEPT INFORMATION
# ============================================================

def get_question_concept(
    question
):

    if not isinstance(
        question,
        dict
    ):

        return ""

    return _normalize_concept(
        question.get(
            "concept",
            ""
        )
    )


# ============================================================
# GENERATE QUESTION PAPER
# ============================================================

def generate_question_paper(
    chunks,
    num_questions=5,
    q_type="MCQ",
    difficulty="Medium",
    bloom_level="Understand",
    query="",
    retrieval_top_k=DEFAULT_RETRIEVAL_TOP_K
):

    # ========================================================
    # INPUT VALIDATION
    # ========================================================

    if not chunks:

        return {
            "success": False,

            "questions": [],

            "total_questions": 0,

            "requested_questions":
                num_questions,

            "error":
                "No document chunks available."
        }

    try:

        num_questions = int(
            num_questions
        )

    except (
        ValueError,
        TypeError
    ):

        return {
            "success": False,

            "questions": [],

            "total_questions": 0,

            "requested_questions":
                num_questions,

            "error":
                "Number of questions must be an integer."
        }

    if num_questions <= 0:

        return {
            "success": False,

            "questions": [],

            "total_questions": 0,

            "requested_questions":
                num_questions,

            "error":
                "Number of questions must be greater than zero."
        }

    # ========================================================
    # NORMALIZE INPUT
    # ========================================================

    requested_q_type = (
        normalize_question_type(
            q_type
        )
    )

    difficulty = normalize_difficulty(
        difficulty
    )

    bloom_level = normalize_bloom_level(
        bloom_level
    )

    print()
    print(
        "========================================"
    )

    print(
        "[QP] SMART Q GEN"
    )

    print(
        "[QP] QUESTION PAPER GENERATION"
    )

    print(
        "========================================"
    )

    print(
        "[QP] Requested questions:",
        num_questions
    )

    print(
        "[QP] Question type:",
        requested_q_type
    )

    print(
        "[QP] Difficulty:",
        difficulty
    )

    print(
        "[QP] Bloom level:",
        bloom_level
    )

    # ========================================================
    # QUESTION TYPE VALIDATION
    # ========================================================

    if requested_q_type not in (
        QUESTION_TYPES + ["ALL"]
    ):

        return {
            "success": False,

            "questions": [],

            "total_questions": 0,

            "requested_questions":
                num_questions,

            "question_type":
                requested_q_type,

            "difficulty":
                difficulty,

            "bloom_level":
                bloom_level,

            "error":
                "Unsupported question type: "
                + str(q_type)
        }

    # ========================================================
    # RETRIEVAL
    # ========================================================

    # Always give the retriever a broad enough candidate pool.
    retrieval_top_k = max(
        int(retrieval_top_k),
        DEFAULT_RETRIEVAL_TOP_K
    )

    context_chunks = (
        retrieve_question_context(
            chunks=chunks,

            query=query,

            top_k=retrieval_top_k
        )
    )

    if not context_chunks:

        return {
            "success": False,

            "questions": [],

            "total_questions": 0,

            "requested_questions":
                num_questions,

            "question_type":
                requested_q_type,

            "difficulty":
                difficulty,

            "bloom_level":
                bloom_level,

            "query":
                query,

            "error":
                "No relevant document context was found."
        }

    # ========================================================
    # BUILD CONTEXT POOL
    # ========================================================

    context_pool = build_context_pool(
        context_chunks
    )

    print()
    print(
        "[QP] Context pool:",
        len(context_pool)
    )

    # ========================================================
    # CONCEPT POOL
    # ========================================================

    concepts = extract_context_concepts(
        context_pool
    )

    print(
        "[QP] Valid metadata concepts:",
        len(concepts)
    )

    if concepts:

        print(
            "[QP] Concept pool:"
        )

        for concept in concepts:

            print(
                "  -",
                concept
            )

    # ========================================================
    # GENERATION
    # ========================================================

    questions = []

    max_attempts = max(
        num_questions
        * MAX_ATTEMPTS_MULTIPLIER,

        MINIMUM_MAX_ATTEMPTS
    )

    attempt = 0

    # Track concepts only for reporting/diversity.
    # It is NOT a hard rejection rule.
    used_concepts = set()

    # ========================================================
    # MAIN LOOP
    # ========================================================

    while (
        len(questions)
        < num_questions
        and attempt < max_attempts
    ):

        question_number = (
            len(questions) + 1
        )

        current_q_type = (
            select_question_type(
                requested_q_type,

                question_number
            )
        )

        print()
        print(
            "----------------------------------------"
        )

        print(
            f"[QP] Target question: "
            f"{question_number}/{num_questions}"
        )

        print(
            "[QP] Type:",
            current_q_type
        )

        print(
            "[QP] Attempt:",
            attempt + 1,
            "/",
            max_attempts
        )

        # ====================================================
        # SELECT ROTATING CONTEXT
        # ====================================================

        question_context = (
            build_question_context(
                context_pool=context_pool,

                question_index=attempt,

                total_questions=num_questions
            )
        )

        if not question_context:

            attempt += 1

            continue

        print(
            "[QP] Context chunks:",
            len(question_context)
        )

        # ====================================================
        # GENERATE
        # ====================================================

        question = (
            generate_single_question(
                context_chunks=question_context,

                q_type=current_q_type,

                difficulty=difficulty,

                bloom_level=bloom_level,

                attempt_idx=attempt
            )
        )

        attempt += 1

        # ====================================================
        # GENERATION FAILED
        # ====================================================

        if question is None:

            print(
                "[QP] Generation failed."
            )

            continue

        # ====================================================
        # FINAL VALIDATION
        # ====================================================

        if not validate_question(
            question,

            expected_type=current_q_type
        ):

            print(
                "[QP] Rejected: validation failed."
            )

            continue

        # ====================================================
        # DUPLICATE QUESTION CHECK
        #
        # IMPORTANT:
        # We ONLY reject the exact same question.
        #
        # We DO NOT reject a question just because
        # the concept was used before.
        # ====================================================

        if is_duplicate_question(
            question,

            questions
        ):

            print(
                "[QP] Rejected: duplicate question."
            )

            continue

        # ====================================================
        # CONCEPT
        # ====================================================

        concept = get_question_concept(
            question
        )

        if concept:

            used_concepts.add(
                concept.casefold()
            )

            print(
                "[QP] Concept:",
                concept
            )

        # ====================================================
        # NUMBER
        # ====================================================

        question[
            "question_number"
        ] = (
            len(questions) + 1
        )

        # ====================================================
        # ADD QUESTION
        # ====================================================

        questions.append(
            question
        )

        print(
            "[QP] ACCEPTED"
        )

        print(
            "[QP] Question:",
            question.get(
                "question"
            )
        )

        print(
            "[QP] Method:",
            question.get(
                "generation_method"
            )
        )

    # ========================================================
    # FINAL STATUS
    # ========================================================

    success = (
        len(questions)
        == num_questions
    )

    if success:

        error = None

        print()
        print(
            "========================================"
        )

        print(
            "[QP] QUESTION PAPER GENERATED"
        )

        print(
            "[QP] Requested:",
            num_questions
        )

        print(
            "[QP] Generated:",
            len(questions)
        )

        print(
            "[QP] Attempts:",
            attempt
        )

        print(
            "[QP] Unique concepts used:",
            len(used_concepts)
        )

        print(
            "========================================"
        )

    else:

        error = (
            f"Could generate only "
            f"{len(questions)} of "
            f"{num_questions} "
            f"requested questions."
        )

        print()
        print(
            "========================================"
        )

        print(
            "[QP] GENERATION INCOMPLETE"
        )

        print(
            "[QP]",
            error
        )

        print(
            "[QP] Attempts:",
            attempt
        )

        print(
            "[QP] Context pool:",
            len(context_pool)
        )

        print(
            "[QP] Unique concepts used:",
            len(used_concepts)
        )

        print(
            "========================================"
        )

    # ========================================================
    # RETURN
    # ========================================================

    return {

        "success":
            success,

        "questions":
            questions,

        "total_questions":
            len(questions),

        "requested_questions":
            num_questions,

        "question_type":
            requested_q_type,

        "difficulty":
            difficulty,

        "bloom_level":
            bloom_level,

        "query":
            query,

        "error":
            error
    }


# ============================================================
# PRINT QUESTION PAPER
# ============================================================

def print_question_paper(
    paper
):

    if not paper:

        print(
            "No question paper generated."
        )

        return

    print()

    print(
        "=" * 70
    )

    print(
        "GENERATED QUESTION PAPER"
    )

    print(
        "=" * 70
    )

    print(
        "Question Type:",
        paper.get(
            "question_type"
        )
    )

    print(
        "Difficulty:",
        paper.get(
            "difficulty"
        )
    )

    print(
        "Bloom Level:",
        paper.get(
            "bloom_level"
        )
    )

    print(
        "Requested:",
        paper.get(
            "requested_questions"
        )
    )

    print(
        "Generated:",
        paper.get(
            "total_questions"
        )
    )

    print(
        "=" * 70
    )

    for question in paper.get(
        "questions",
        []
    ):

        number = question.get(
            "question_number"
        )

        question_type = question.get(
            "type",
            ""
        )

        text = question.get(
            "question",
            ""
        )

        print()

        print(
            f"Q{number}. "
            f"[{question_type}] "
            f"{text}"
        )

        # ----------------------------------------------------
        # MCQ
        # ----------------------------------------------------

        if question_type == "MCQ":

            options = question.get(
                "options",
                []
            )

            labels = [
                "A",
                "B",
                "C",
                "D"
            ]

            for index, option in enumerate(
                options
            ):

                if index < 4:

                    print(
                        f"({labels[index]}) "
                        f"{option}"
                    )

        # ----------------------------------------------------
        # ANSWER
        # ----------------------------------------------------

        answer = question.get(
            "correct_answer"
        )

        if not answer:

            answer = question.get(
                "answer"
            )

        if answer:

            print(
                "Answer:",
                answer
            )

    print()

    print(
        "=" * 70
    )

    if paper.get(
        "success"
    ):

        print(
            "QUESTION PAPER GENERATION SUCCESSFUL"
        )

    else:

        print(
            "QUESTION PAPER GENERATION INCOMPLETE"
        )

        if paper.get(
            "error"
        ):

            print(
                "Reason:",
                paper.get(
                    "error"
                )
            )

    print(
        "=" * 70
    )


# ============================================================
# MODULE TEST
# ============================================================

if __name__ == "__main__":

    print(
        "========================================"
    )

    print(
        "SMART Q GEN"
    )

    print(
        "QUESTION PAPER GENERATOR"
    )

    print(
        "========================================"
    )

    print(
        "\nSupported question types:"
    )

    for question_type in QUESTION_TYPES:

        print(
            "-",
            question_type
        )

    print(
        "- ALL"
    )

    print(
        "\nALL mode:"
    )

    for number in range(
        1,
        11
    ):

        print(
            f"Q{number} ->",
            select_question_type(
                "ALL",
                number
            )
        )

    print()

    print(
        "Difficulty:"
    )

    for value in [
        "Easy",
        "Medium",
        "Hard",
        "invalid"
    ]:

        print(
            value,
            "->",
            normalize_difficulty(
                value
            )
        )

    print()

    print(
        "Bloom:"
    )

    for value in [
        "Remember",
        "Understand",
        "Apply",
        "Analyze",
        "Evaluate",
        "Create",
        "invalid"
    ]:

        print(
            value,
            "->",
            normalize_bloom_level(
                value
            )
        )

    print()

    print(
        "========================================"
    )

    print(
        "TEST COMPLETED"
    )

    print(
        "========================================"
    )