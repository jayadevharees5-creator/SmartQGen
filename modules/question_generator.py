2345678

import re
import random
from typing import Any, Dict, List, Optional


# ============================================================
# OPTIONAL IMPORTS
# ============================================================

try:
    import torch
except Exception:
    torch = None

try:
    from transformers import pipeline
except Exception:
    pipeline = None


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MODEL_NAME = "google/flan-t5-small"

_GENERATOR = None

# FLAN-T5-Small has a limited input length.
# Keep the actual prompt comfortably small.
MAX_CONTEXT_WORDS = 180
MAX_DEFINITION_WORDS = 60
MAX_NEW_TOKENS = 64


# ============================================================
# SUPPORTED SETTINGS
# ============================================================

SUPPORTED_DIFFICULTIES = {
    "Easy",
    "Medium",
    "Hard",
}

SUPPORTED_BLOOM = {
    "Remember",
    "Understand",
    "Apply",
    "Analyze",
    "Evaluate",
    "Create",
}

QUESTION_TYPES = [
    "MCQ",
    "FILL_IN_THE_BLANKS",
    "TRUE_FALSE",
    "SHORT_ANSWER",
    "LONG_ANSWER",
]


# ============================================================
# GENERIC WORDS
# ============================================================

GENERIC_WORDS = {
    "it",
    "this",
    "that",
    "these",
    "those",
    "they",
    "them",
    "he",
    "she",
    "we",
    "you",
    "what",
    "why",
    "when",
    "where",
    "which",
    "who",
    "how",
    "there",
    "one",
    "some",
    "many",
    "example",
    "examples",
    "following",
    "above",
    "below",
    "system",
    "systems",
    "method",
    "methods",
    "process",
    "processes",
    "approach",
    "way",
    "type",
    "types",
    "result",
    "results",
    "information",
    "data",
    "problem",
    "solution",
    "application",
    "applications",
    "thing",
    "things",
    "people",
    "users",
    "others",
    "now",
    "term",
    "concept",
    "general",
    "etc",
}


BAD_CONCEPT_PHRASES = {
    "data that",
    "term ",
    "main concept",
    "what is",
    "which is",
    "how to",
    "why ",
    "because ",
    "for example",
    "such as",
    "the following",
    "listed below",
    "listed above",
    "or cyber",
    "and cyber",
    "it also",
    "whereby a",
    "up of two words",
}


BAD_CONCEPT_STARTS = {
    "often", "some", "many", "few", "most", "more", "less",
    "now", "also", "using", "used", "use", "protecting",
    "providing", "ensuring", "maintaining", "related", "based",
    "known", "called", "designed", "carried", "trying", "including",
}

PDF_NOISE_PATTERNS = [
    r"^s\.?\s*no\.?\s+unit\s+topic\s+page",
    r"^cyber\s+security\s+iii\s+year",
    r"^cyber\s+security\s*\(professional elective",
    r"^l\s*t\s*/\s*p\s*/\s*d",
    r"^page\s+\d+\s*$",
    r"^contents$",
    r"^table\s+of\s+contents$",
]


BAD_QUESTION_PHRASES = {
    "what is the main concept",
    "what is it",
    "what is this",
    "what is that",
    "according to the prompt",
    "according to the document",
    "according to the source",
    "according to the study material",
    "as an ai",
    "i cannot",
    "two words that make up",
}


# ============================================================
# BASIC HELPERS
# ============================================================

def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _clean_text(text: Any) -> str:
    text = _safe_text(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\u200b", "")
    cleaned = []
    for raw in text.split("\n"):
        line = re.sub(r"[ \t]+", " ", raw).strip()
        if not line:
            continue
        lower = line.casefold()
        if any(re.search(pat, lower, flags=re.I) for pat in PDF_NOISE_PATTERNS):
            continue
        if len(re.findall(r"\b\d+\b", line)) >= 4 and len(line.split()) >= 7:
            continue
        cleaned.append(line)
    text = "\n".join(cleaned)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _normalize_spaces(text: Any) -> str:
    return re.sub(
        r"\s+",
        " ",
        _safe_text(text)
    ).strip()


def _limit_words(
    text: Any,
    max_words: int
) -> str:

    words = _safe_text(text).split()

    if len(words) <= max_words:
        return " ".join(words)

    return " ".join(words[:max_words])


# ============================================================
# SUBJECT NORMALIZATION
# ============================================================

def _normalize_subject(value: Any) -> str:

    subject = _safe_text(value).strip()

    # Remove numbering
    subject = re.sub(
        r"^\s*(?:\d+(?:\.\d+)*[.)-]?\s*)",
        "",
        subject
    )

    # Remove bullets
    subject = re.sub(
        r"^\s*[-*•]\s*",
        "",
        subject
    )

    # Remove articles
    subject = re.sub(
        r"^(?:a|an|the)\s+",
        "",
        subject,
        flags=re.I
    )

    subject = subject.strip(
        " \t\r\n.,;:!?-"
    )

    subject = _normalize_spaces(subject)

    return subject


# ============================================================
# SUBJECT VALIDATION
# ============================================================

def _valid_subject(value: Any) -> bool:

    subject = _normalize_subject(value)

    if not subject:
        return False

    if len(subject) < 2:
        return False

    if len(subject) > 60:
        return False

    words = subject.split()

    # Educational concept should normally be short.
    if len(words) > 5:
        return False

    cleaned_words = [
        re.sub(
            r"[^a-z0-9]",
            "",
            word.lower()
        )
        for word in words
    ]

    if (
        len(cleaned_words) == 1
        and cleaned_words[0] in GENERIC_WORDS
    ):
        return False

    lower = subject.casefold()
    first_word = lower.split()[0] if lower.split() else ""
    if first_word in BAD_CONCEPT_STARTS:
        return False
    # Common OCR / PDF extraction fragments.
    if re.match(
        r"^(?:vailability|ttackers|ntegrity|onfidentiality|"
        r"yber|ybersecurity|ecurity|nformation|uthorized|ccess)$",
        lower
    ):
        return False

    # A concept should not look like a sentence fragment.
    if len(words) >= 2 and re.search(
        r"\b(?:carried|used|using|protecting|providing|ensuring|"
        r"maintaining|designed|known|called|based|related|performed|"
        r"available|accessible|possible|responsible)\b",
        lower
    ):
        return False

    # Bad phrases
    for phrase in BAD_CONCEPT_PHRASES:
        if phrase in lower:
            return False

    # Bad starting words
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

    # Cannot be a sentence
    if "?" in subject or "!" in subject:
        return False

    # Cannot contain grammatical connector words
    if re.search(
        r"\b(?:is|are|was|were|that|which|who|"
        r"when|where|because|include|includes|including)\b",
        lower
    ):
        return False

    # Cannot end with a connector
    if re.search(
        r"\b(?:of|for|with|from|and|or|to|that|which|who)$",
        lower
    ):
        return False

    # Must contain letters
    if not re.search(
        r"[A-Za-z]",
        subject
    ):
        return False

    return True


# ============================================================
# DEFINITION VALIDATION
# ============================================================

def _valid_definition(value: Any) -> bool:

    definition = _safe_text(value).strip()

    if not definition:
        return False

    words = definition.split()

    # Very short definitions are normally bad extraction.
    if len(words) < 5:
        return False

    if len(words) > 120:
        return False

    return True


# ============================================================
# CLEAN DEFINITION
# ============================================================

def _clean_definition(value: Any) -> str:

    definition = _normalize_spaces(value)

    definition = re.sub(
        r"^(?:is|are|means|refers to|is defined as)\s+",
        "",
        definition,
        flags=re.I
    )

    # Stop at obvious unrelated examples.
    definition = re.split(
        r"\s+(?:for example|such as|including the following)\b",
        definition,
        maxsplit=1,
        flags=re.I
    )[0]

    definition = definition.strip(
        " .;:-"
    )

    return definition


# ============================================================
# CONCEPT QUALITY SCORE
# ============================================================

def _concept_quality_score(
    subject: str,
    definition: str,
    pattern_type: str
) -> int:

    score = 0

    if _valid_subject(subject):
        score += 5

    if _valid_definition(definition):
        score += 5

    # Strong definition patterns get higher priority.
    if pattern_type == "defined_as":
        score += 5

    elif pattern_type == "refers_to":
        score += 4

    elif pattern_type == "means":
        score += 4

    elif pattern_type == "is":
        score += 2

    elif pattern_type == "are":
        score += 2

    word_count = len(subject.split())

    if 1 <= word_count <= 4:
        score += 2

    # Prefer definitions with useful length.
    if len(definition.split()) >= 8:
        score += 2

    return score


# ============================================================
# CONCEPT REPAIR
# ============================================================

def _repair_subject(subject: str, sentence: str) -> str:
    subject = _normalize_subject(subject)
    repairs = {
        "vailability": "Availability",
        "ttackers": "Attackers",
        "ntegrity": "Integrity",
        "onfidentiality": "Confidentiality",
    }
    repaired = repairs.get(subject.casefold())
    if repaired and re.search(rf"\b{re.escape(repaired)}\b", sentence, flags=re.I):
        return repaired
    return subject


# ============================================================
# EXTRACT CONCEPT FROM SENTENCE
# ============================================================

def _extract_from_sentence(
    sentence: str
) -> Optional[Dict[str, Any]]:

    sentence = _normalize_spaces(sentence)

    if not sentence:
        return None

    # --------------------------------------------------------
    # Reject obvious list sentences
    # --------------------------------------------------------

    if re.search(
        r"\b(?:types?|kinds?|categories?|examples?|"
        r"measures?|steps?|methods?)\b"
        r".*\b(?:include|includes|are)\b",
        sentence,
        flags=re.I
    ):
        return None

    # --------------------------------------------------------
    # Strong definition patterns
    # --------------------------------------------------------

    patterns = [

        (
            "defined_as",
            r"^\s*(?:a|an|the)?\s*"
            r"([A-Za-z][A-Za-z0-9/&().-]*(?:\s+[A-Za-z0-9/&().-]+){0,3})"
            r"\s+is\s+defined\s+as\s+(.+?)\s*$"
        ),

        (
            "refers_to",
            r"^\s*(?:a|an|the)?\s*"
            r"([A-Za-z][A-Za-z0-9/&().-]*(?:\s+[A-Za-z0-9/&().-]+){0,3})"
            r"\s+refers\s+to\s+(.+?)\s*$"
        ),

        (
            "means",
            r"^\s*(?:a|an|the)?\s*"
            r"([A-Za-z][A-Za-z0-9/&().-]*(?:\s+[A-Za-z0-9/&().-]+){0,3})"
            r"\s+means\s+(.+?)\s*$"
        ),

        # Example:
        # "Cyber security is the protection..."
        (
            "is",
            r"^\s*(?:a|an|the)?\s*"
            r"([A-Za-z][A-Za-z0-9/&().-]*(?:\s+[A-Za-z0-9/&().-]+){0,2})"
            r"\s+is\s+(.+?)\s*$"
        ),

        # Example:
        # "Viruses are malicious programs..."
        (
            "are",
            r"^\s*(?:a|an|the)?\s*"
            r"([A-Za-z][A-Za-z0-9/&().-]*(?:\s+[A-Za-z0-9/&().-]+){0,2})"
            r"\s+are\s+(.+?)\s*$"
        ),
    ]

    for pattern_type, pattern in patterns:

        match = re.match(
            pattern,
            sentence,
            flags=re.I
        )

        if not match:
            continue

        subject = _repair_subject(
            match.group(1),
            sentence
        )

        definition = _clean_definition(
            match.group(2)
        )

        if not _valid_subject(subject):
            continue

        if not _valid_definition(definition):
            continue

        score = _concept_quality_score(
            subject,
            definition,
            pattern_type
        )

        return {
            "subject": subject,
            "definition": definition,
            "quality_score": score,
            "pattern": pattern_type,
        }

    return None


# ============================================================
# GENERIC CONCEPT EXTRACTION
# ============================================================

def _extract_generic_concepts(
    text: str
) -> List[Dict[str, Any]]:

    text = _clean_text(text)

    if not text:
        return []

    # Convert line breaks to spaces.
    normalized = _normalize_spaces(text)

    # Split into sentences.
    sentences = re.split(
        r"(?<=[.!?])\s+",
        normalized
    )

    concepts = []
    seen = set()

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        concept = _extract_from_sentence(
            sentence
        )

        if not concept:
            continue

        subject = concept["subject"]

        key = subject.casefold()

        if key in seen:
            continue

        seen.add(key)

        concepts.append(
            concept
        )

    # Highest quality first.
    concepts.sort(
        key=lambda item: item.get(
            "quality_score",
            0
        ),
        reverse=True
    )

    return concepts


# ============================================================
# HEADING EXTRACTION
# ============================================================

def _extract_heading_concepts(
    text: str
) -> List[Dict[str, Any]]:

    results = []
    seen = set()

    for line in _safe_text(text).splitlines():

        line = line.strip()

        if not line:
            continue

        # Remove numbering.
        heading = re.sub(
            r"^\s*\d+(?:\.\d+)*[\s.)-]+",
            "",
            line
        ).strip()

        if not heading:
            continue

        # Headings should be short.
        if len(heading.split()) > 5:
            continue

        # Do not use complete sentences as headings.
        if re.search(
            r"[.!?]$",
            heading
        ):
            continue

        heading = _normalize_subject(
            heading
        )

        if not _valid_subject(heading):
            continue

        key = heading.casefold()

        if key in seen:
            continue

        seen.add(key)

        results.append(
            {
                "subject": heading,
                "definition": "",
                "quality_score": 1,
            }
        )

    return results


# ============================================================
# PUBLIC CONCEPT EXTRACTION
# ============================================================

def extract_educational_concepts(
    context: Any,
    max_concepts: int = 25
) -> List[Dict[str, Any]]:
    """
    Extract only definition-backed concepts.

    Heading-only concepts are intentionally ignored because
    they do not contain enough factual information for
    grounded question generation.
    """

    context = _clean_text(context)

    if not context:
        return []

    concepts = _extract_generic_concepts(
        context
    )

    result = []
    seen = set()

    for concept in concepts:

        subject = _normalize_subject(
            concept.get(
                "subject",
                ""
            )
        )

        definition = _clean_definition(
            concept.get(
                "definition",
                ""
            )
        )

        if not _valid_subject(subject):
            continue

        if not _valid_definition(definition):
            continue

        key = subject.casefold()

        if key in seen:
            continue

        seen.add(key)

        result.append(
            {
                "subject": subject,
                "definition": definition,
                "quality_score": concept.get(
                    "quality_score",
                    10
                ),
            }
        )

        if len(result) >= max_concepts:
            break

    return result


# ============================================================
# CHUNK HELPERS
# ============================================================

def _combine_chunks(
    chunks: Any
) -> str:

    if not chunks:
        return ""

    if isinstance(chunks, str):
        return chunks

    if isinstance(chunks, dict):
        return _safe_text(
            chunks.get(
                "text",
                ""
            )
        )

    parts = []

    for chunk in chunks:

        if isinstance(chunk, dict):
            value = _safe_text(
                chunk.get(
                    "text",
                    ""
                )
            )
        else:
            value = _safe_text(
                chunk
            )

        if value.strip():
            parts.append(
                value.strip()
            )

    return "\n\n".join(parts)


def _get_metadata(
    chunks: Any
) -> Dict[str, Any]:

    metadata = {
        "source_page": None,
        "source_chapter": None,
        "source_topic": None,
    }

    if not isinstance(
        chunks,
        list
    ):
        return metadata

    for chunk in chunks:

        if not isinstance(
            chunk,
            dict
        ):
            continue

        metadata["source_page"] = (
            chunk.get("page")
            or chunk.get("page_number")
        )

        metadata["source_chapter"] = (
            chunk.get("chapter")
        )

        metadata["source_topic"] = (
            chunk.get("topic")
        )

        break

    return metadata


# ============================================================
# BUILD SMALL MODEL CONTEXT
# ============================================================

def _build_small_context(
    concept: Dict[str, Any],
    source_context: str
) -> str:

    subject = _normalize_subject(
        concept.get(
            "subject",
            ""
        )
    )

    definition = _limit_words(
        concept.get(
            "definition",
            ""
        ),
        MAX_DEFINITION_WORDS
    )

    # Do NOT send the complete retrieved PDF context to FLAN.
    # Retrieved chunks can contain headers, page numbers and unrelated
    # concepts. The selected concept + definition is enough to generate
    # a grounded question.
    return (
        f"Concept: {subject}\n"
        f"Definition: {definition}"
    )


# ============================================================
# MODEL LOADING
# ============================================================

def _get_generator():

    global _GENERATOR

    if _GENERATOR is not None:
        return _GENERATOR

    if pipeline is None:

        print(
            "[QG] Transformers package unavailable."
        )

        return None

    try:

        print(
            "\n[QG] Loading FLAN-T5-SMALL..."
        )

        if (
            torch is not None
            and torch.cuda.is_available()
        ):

            device = 0
            device_name = "CUDA"

        elif (
            torch is not None
            and hasattr(
                torch.backends,
                "mps"
            )
            and torch.backends.mps.is_available()
        ):

            device = "mps"
            device_name = "MPS"

        else:

            device = -1
            device_name = "CPU"

        print(
            "[QG] Using device:",
            device_name
        )

        _GENERATOR = pipeline(
            "text2text-generation",
            model=MODEL_NAME,
            device=device
        )

        print(
            "[QG] FLAN-T5-SMALL loaded successfully."
        )

        return _GENERATOR

    except Exception as exc:

        print(
            "[QG] Model loading failed:",
            exc
        )

        _GENERATOR = None

        return None


# ============================================================
# BLOOM TASK
# ============================================================

def _get_bloom_task(
    q_type: str,
    bloom_level: str
) -> str:

    tasks = {

        "MCQ": {
            "Remember":
                "Test direct recall of the concept.",
            "Understand":
                "Test understanding of the concept.",
            "Apply":
                "Test simple application of the concept.",
            "Analyze":
                "Test distinction or analysis involving the concept.",
            "Evaluate":
                "Test evaluation using source-supported information.",
            "Create":
                "Test formulation of a solution involving the concept.",
        },

        "FILL_IN_THE_BLANKS": {
            "Remember":
                "Test direct recall.",
            "Understand":
                "Test understanding of the definition.",
            "Apply":
                "Test recognition in a simple application.",
            "Analyze":
                "Test identification from a described situation.",
            "Evaluate":
                "Test source-supported recognition.",
            "Create":
                "Test recognition in a simple scenario.",
        },

        "TRUE_FALSE": {
            "Remember":
                "Create a directly stated factual statement.",
            "Understand":
                "Create a statement about the meaning.",
            "Apply":
                "Create a source-supported application statement.",
            "Analyze":
                "Create a source-supported analytical statement.",
            "Evaluate":
                "Create a source-supported evaluative statement.",
            "Create":
                "Create a source-supported scenario statement.",
        },

        "SHORT_ANSWER": {
            "Remember":
                "Ask for definition or identification.",
            "Understand":
                "Ask for an explanation of meaning.",
            "Apply":
                "Ask how the concept can be applied.",
            "Analyze":
                "Ask for analysis of the concept.",
            "Evaluate":
                "Ask for evaluation using source information.",
            "Create":
                "Ask for a source-supported use or solution.",
        },

        "LONG_ANSWER": {
            "Remember":
                "Ask for definition and key facts.",
            "Understand":
                "Ask for detailed explanation.",
            "Apply":
                "Ask for detailed application.",
            "Analyze":
                "Ask for detailed analysis.",
            "Evaluate":
                "Ask for detailed evaluation.",
            "Create":
                "Ask for a detailed source-supported solution.",
        },
    }

    return tasks.get(
        q_type,
        {}
    ).get(
        bloom_level,
        "Ask an academic question about the concept."
    )


# ============================================================
# FLAN PROMPT
# ============================================================

def _build_flan_prompt(
    concept,
    q_type,
    difficulty,
    bloom_level,
    source_context
):
    """
    Build a very small FLAN prompt.

    Important:
    FLAN receives only the selected concept and its definition.
    It must not see the complete PDF/retrieval context because that
    causes it to copy headers, university information and other topics.
    """

    subject = _normalize_subject(
        concept.get("subject", "")
    )

    definition = _limit_words(
        concept.get("definition", ""),
        MAX_DEFINITION_WORDS
    )

    if not subject or not definition:
        return None

    task = _get_bloom_task(
        q_type,
        bloom_level
    )

    type_rules = {
        "MCQ":
            "Write one question ending with ?. Do not write options.",
        "FILL_IN_THE_BLANKS":
            "Write one sentence with exactly one __________ blank. "
            "The blank must replace the concept name.",
        "TRUE_FALSE":
            "Write one factual statement. Do not write True or False.",
        "SHORT_ANSWER":
            "Write one question ending with ?. Use the exact concept name.",
        "LONG_ANSWER":
            "Write one question ending with ?. Use the exact concept name.",
    }

    prompt = f"""
You are an examination question generator.

Generate exactly ONE {q_type} question.

CONCEPT:
{subject}

DEFINITION:
{definition}

DIFFICULTY:
{difficulty}

BLOOM LEVEL:
{bloom_level}

TASK:
{task}

STRICT RULES:
1. The question must be about {subject}.
2. Use the exact words "{subject}" in the output.
3. Use only the definition above.
4. Do not introduce another topic or concept.
5. Do not mention a university, course, semester, page, document, source, syllabus, or PDF.
6. Do not output options.
7. Do not output the answer.
8. Do not output explanations.
9. Return only one question or statement.
10. Never start with "The document", "According to", or "What is the main concept".

FORMAT:
{type_rules.get(q_type, "Write one academic question.")}

OUTPUT:
""".strip()

    return prompt

# ============================================================
# CLEAN MODEL OUTPUT
# ============================================================

def _clean_generated_question(
    text: Any
) -> str:

    text = _clean_text(text)

    text = re.sub(
        r"^(?:question|q)\s*:\s*",
        "",
        text,
        flags=re.I
    )

    text = re.split(
        r"\bOptions?\s*:",
        text,
        maxsplit=1,
        flags=re.I
    )[0]

    text = re.split(
        r"\b(?:Answer|Correct answer)\s*:",
        text,
        maxsplit=1,
        flags=re.I
    )[0]

    text = re.sub(
        r"^\s*(?:[-*•]|\d+[.)])\s*",
        "",
        text
    )

    return _normalize_spaces(
        text
    ).strip(
        " \"'"
    )


# ============================================================
# QUESTION CONCEPT MATCH
# ============================================================

def _question_mentions_subject(
    question: str,
    subject: str
) -> bool:

    q = _safe_text(
        question
    ).casefold()

    s = _normalize_subject(
        subject
    ).casefold()

    if not q or not s:
        return False

    words = re.findall(
        r"[a-z0-9]+",
        s
    )

    if not words:
        return False

    if len(words) == 1:

        return bool(
            re.search(
                rf"\b{re.escape(words[0])}\b",
                q
            )
        )

    pattern = r"\s+".join(
        re.escape(word)
        for word in words
    )

    return bool(
        re.search(
            pattern,
            q
        )
    )


# ============================================================
# MODEL OUTPUT VALIDATION
# ============================================================

def _is_bad_model_output(
    text: str
) -> bool:

    text = _clean_generated_question(
        text
    )

    if not text:
        return True

    if len(text) < 10:
        return True

    if len(text.split()) > 50:
        return True

    lower = text.casefold()

    for phrase in BAD_QUESTION_PHRASES:

        if phrase in lower:
            return True

    if re.search(
        r"\b(?:iii\s+year|ii\s+sem|s\.?\s*no\.?\s+unit\s+topic|page\s+no|professional\s+elective|l\s*t\s*/\s*p\s*/\s*d)\b",
        lower
    ):
        return True

    if lower.startswith(
        (
            "or ",
            "and ",
            "because ",
            "including ",
        )
    ):
        return True

    if "options:" in lower:
        return True

    if "answer:" in lower:
        return True

    return False


# ============================================================
# QUESTION TYPE VALIDATION
# ============================================================

def _validate_generated_question_type(
    question: str,
    subject: str,
    q_type: str
) -> bool:

    question = _clean_generated_question(
        question
    )

    if not question:
        return False

    if q_type == "MCQ":

        return (
            "?" in question
            or question.lower().startswith(
                (
                    "which ",
                    "what ",
                    "identify ",
                    "select ",
                )
            )
        )

    if q_type == "FILL_IN_THE_BLANKS":

        return (
            "__________" in question
            and not _question_mentions_subject(
                question,
                subject
            )
        )

    if q_type == "TRUE_FALSE":

        return "?" not in question

    if q_type in {
        "SHORT_ANSWER",
        "LONG_ANSWER"
    }:

        return (
            _question_mentions_subject(
                question,
                subject
            )
            and "?" in question
        )

    return False


# ============================================================
# FLAN GENERATION
# ============================================================

def _try_local_model(
    concept,
    q_type,
    difficulty,
    bloom_level,
    source_context=""
):

    generator = _get_generator()

    if generator is None:
        return None

    prompt = _build_flan_prompt(
        concept,
        q_type,
        difficulty,
        bloom_level,
        source_context
    )

    if not prompt:
        return None

    try:

        result = generator(
            prompt,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            num_beams=2,
            truncation=True
        )

        if not result:
            return None

        generated = _clean_generated_question(
            result[0].get(
                "generated_text",
                ""
            )
        )

        print(
            "[QG] FLAN-T5-SMALL generated:",
            generated
        )

        if _is_bad_model_output(
            generated
        ):

            print(
                "[QG] Rejected FLAN output: invalid format."
            )

            return None

        if q_type != "FILL_IN_THE_BLANKS":

            if not _question_mentions_subject(
                generated,
                concept.get(
                    "subject",
                    ""
                )
            ):

                print(
                    "[QG] Rejected FLAN output: wrong concept."
                )

                print(
                    "[QG] Expected:",
                    concept.get(
                        "subject",
                        ""
                    )
                )

                return None

        if not _validate_generated_question_type(
            generated,
            concept.get(
                "subject",
                ""
            ),
            q_type
        ):

            print(
                "[QG] Rejected FLAN output: wrong type."
            )

            return None

        return generated

    except Exception as exc:

        print(
            "[QG] FLAN generation failed:",
            exc
        )

        return None


# ============================================================
# MCQ OPTION VALIDATION
# ============================================================

def _valid_option(
    value: Any,
    correct_answer: str = ""
) -> bool:

    value = _normalize_subject(
        value
    )

    if not value:
        return False

    if len(value.split()) > 5:
        return False

    if value.casefold() == _safe_text(
        correct_answer
    ).strip().casefold():

        return False

    if value.casefold() in GENERIC_WORDS:
        return False

    if value.casefold() in {
        "security",
        "cyber",
        "information",
    }:
        return False

    return True


# ============================================================
# SOURCE-GROUNDED DISTRACTORS
# ============================================================

def generate_plausible_distractors(
    correct_answer,
    concepts=None,
    count=3,
    definition="",
    source_context=""
):

    correct = _normalize_subject(
        correct_answer
    )

    candidates = []

    # --------------------------------------------------------
    # First: use real concepts from source.
    # --------------------------------------------------------

    for concept in concepts or []:

        if not isinstance(
            concept,
            dict
        ):
            continue

        subject = _normalize_subject(
            concept.get(
                "subject",
                ""
            )
        )

        concept_definition = _safe_text(
            concept.get(
                "definition",
                ""
            )
        )

        if not _valid_subject(subject):
            continue

        if not _valid_definition(
            concept_definition
        ):
            continue

        if subject.casefold() == correct.casefold():
            continue

        if _valid_option(
            subject,
            correct
        ):

            candidates.append(
                subject
            )

    # Remove duplicates.
    unique = []
    seen = set()

    for candidate in candidates:

        key = candidate.casefold()

        if key in seen:
            continue

        seen.add(key)

        unique.append(
            candidate
        )

    # Only return actual source concepts.
    return unique[:count]


# ============================================================
# SOURCE-GROUNDED QUESTION HELPERS
# ============================================================

def _build_mcq_stem(definition: str) -> str:
    """Ask the learner to identify a concept from its source definition."""
    definition = _limit_words(_clean_definition(definition), MAX_DEFINITION_WORDS)
    return f"Which concept is described by the following statement: {definition}?"


def _build_true_false_item(subject, definition, concepts=None, attempt_idx=0):
    """Alternate true statements with false statements using another source definition."""
    subject = _normalize_subject(subject)
    definition = _clean_definition(definition)
    alternatives = [
        item for item in (concepts or [])
        if isinstance(item, dict)
        and _normalize_subject(item.get("subject", "")).casefold() != subject.casefold()
        and _valid_definition(item.get("definition", ""))
    ]
    if attempt_idx % 2 == 1 and alternatives:
        other = alternatives[(attempt_idx // 2) % len(alternatives)]
        statement = f"{subject} is defined as {_clean_definition(other.get('definition', ''))}."
        return statement, "False"
    return f"{subject} is defined as {definition}.", "True"


# ============================================================
# RULE-BASED QUESTION
# ============================================================

def _rule_based_question(
    concept,
    concepts,
    q_type,
    difficulty,
    bloom_level,
    metadata,
    attempt_idx,
    source_context=""
):
    """
    Deterministic fallback.

    This is deliberately reliable: if FLAN produces an unrelated
    question, the system still produces a source-grounded question.
    """

    subject = _normalize_subject(
        concept.get("subject", "")
    )

    definition = _clean_definition(
        concept.get("definition", "")
    )

    if not _valid_subject(subject):
        return None

    if not _valid_definition(definition):
        return None

    base = {
        "difficulty": difficulty,
        "bloom_level": bloom_level,
        "source_page": metadata.get("source_page"),
        "source_chapter": metadata.get("source_chapter"),
        "source_topic": metadata.get("source_topic"),
        "concept": subject,
        "definition": definition,
        "generation_method": "RULE_BASED",
    }

    variant = attempt_idx % 4

    # --------------------------------------------------------
    # MCQ
    # --------------------------------------------------------

    if q_type == "MCQ":
        distractors = generate_plausible_distractors(
            subject, concepts, 3, definition, source_context
        )
        if len(distractors) != 3:
            return None

        options = distractors + [subject]
        random.Random(
            attempt_idx + sum(ord(c) for c in subject)
        ).shuffle(options)

        return {
            **base,
            "question": _build_mcq_stem(definition),
            "type": "MCQ",
            "question_type": "MCQ",
            "q_type": "MCQ",
            "options": options,
            "correct_answer": subject,
            "answer": subject,
        }

    # --------------------------------------------------------
    # FILL IN THE BLANKS
    # --------------------------------------------------------

    if q_type == "FILL_IN_THE_BLANKS":
        return {
            **base,
            "question":
                f"__________ is defined as {definition}.",
            "type": "FILL_IN_THE_BLANKS",
            "question_type": "FILL_IN_THE_BLANKS",
            "q_type": "FILL_IN_THE_BLANKS",
            "options": [],
            "correct_answer": subject,
            "answer": subject,
        }

    # --------------------------------------------------------
    # TRUE / FALSE
    # --------------------------------------------------------

    if q_type == "TRUE_FALSE":
        statement, tf_answer = _build_true_false_item(
            subject, definition, concepts, attempt_idx
        )
        return {
            **base,
            "question": statement,
            "type": "TRUE_FALSE",
            "question_type": "TRUE_FALSE",
            "q_type": "TRUE_FALSE",
            "options": ["True", "False"],
            "correct_answer": tf_answer,
            "answer": tf_answer,
        }

    # --------------------------------------------------------
    # SHORT ANSWER
    # --------------------------------------------------------

    if q_type == "SHORT_ANSWER":
        short_templates = [
            f"What is {subject}?",
            f"How would you define {subject}?",
            f"How would you explain the meaning of {subject}?",
            f"What does {subject} mean?",
        ]

        return {
            **base,
            "question": short_templates[variant],
            "type": "SHORT_ANSWER",
            "question_type": "SHORT_ANSWER",
            "q_type": "SHORT_ANSWER",
            "options": [],
            "correct_answer": definition,
            "answer": definition,
        }

    # --------------------------------------------------------
    # LONG ANSWER
    # --------------------------------------------------------

    if q_type == "LONG_ANSWER":
        long_templates = [
            f"How would you explain {subject} in detail?",
            f"How would you describe {subject} and its meaning?",
            f"How would you discuss {subject} with reference to its definition?",
            f"How would you explain the concept of {subject} and its definition?",
        ]

        return {
            **base,
            "question": long_templates[variant],
            "type": "LONG_ANSWER",
            "question_type": "LONG_ANSWER",
            "q_type": "LONG_ANSWER",
            "options": [],
            "correct_answer": definition,
            "answer": definition,
        }

    return None

# ============================================================
# QUESTION VALIDATION
# ============================================================

def _valid_question_text(
    text: Any
) -> bool:

    text = _clean_generated_question(
        text
    )

    if len(text) < 10:
        return False

    if len(text) > 500:
        return False

    if len(text.split()) < 4:
        return False

    if len(text.split()) > 80:
        return False

    lower = text.casefold()

    for phrase in BAD_QUESTION_PHRASES:

        if phrase in lower:
            return False

    return True


def validate_question(
    question: Any,
    expected_type=None
) -> bool:

    if not isinstance(
        question,
        dict
    ):
        return False

    question_text = _safe_text(
        question.get(
            "question",
            ""
        )
    ).strip()

    if not _valid_question_text(
        question_text
    ):
        return False

    q_type = _safe_text(
        question.get(
            "type",
            ""
        )
    ).strip().upper()

    if expected_type:

        expected_type = _safe_text(
            expected_type
        ).strip().upper()

        if q_type != expected_type:
            return False

    concept = _normalize_subject(
        question.get(
            "concept",
            ""
        )
    )

    if concept and not _valid_subject(
        concept
    ):
        return False

    # --------------------------------------------------------
    # MCQ
    # --------------------------------------------------------

    if q_type == "MCQ":

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

        cleaned = []

        for option in options:

            option_text = _normalize_subject(
                option
            )

            if not _valid_option(
                option_text
            ):
                return False

            cleaned.append(
                option_text.casefold()
            )

        if len(set(cleaned)) != 4:
            return False

        answer = _normalize_subject(
            question.get(
                "correct_answer",
                ""
            )
        )

        if not answer:
            return False

        if answer.casefold() not in set(cleaned):
            return False

        return True

    # --------------------------------------------------------
    # FILL
    # --------------------------------------------------------

    if q_type == "FILL_IN_THE_BLANKS":

        answer = _safe_text(
            question.get(
                "correct_answer",
                ""
            )
        ).strip()

        return (
            bool(answer)
            and "__________" in question_text
        )

    # --------------------------------------------------------
    # TRUE / FALSE
    # --------------------------------------------------------

    if q_type == "TRUE_FALSE":

        answer = _safe_text(
            question.get(
                "correct_answer",
                ""
            )
        ).strip().casefold()

        return (
            answer in {
                "true",
                "false"
            }
            and "?" not in question_text
        )

    # --------------------------------------------------------
    # SHORT / LONG
    # --------------------------------------------------------

    if q_type in {
        "SHORT_ANSWER",
        "LONG_ANSWER"
    }:

        answer = _safe_text(
            question.get(
                "answer",
                question.get(
                    "correct_answer",
                    ""
                )
            )
        ).strip()

        if not answer:
            return False

        if concept:
            if not _question_mentions_subject(
                question_text,
                concept
            ):
                return False

        return "?" in question_text

    return False


# ============================================================
# SELECT BEST CONCEPT
# ============================================================

def _select_concept(
    concepts: List[Dict[str, Any]],
    attempt_idx: int
) -> Optional[Dict[str, Any]]:

    if not concepts:
        return None

    # Rotate through all validated concepts. This prevents the
    # generator from repeatedly selecting only the first few concepts.
    candidates = concepts[:25]

    return candidates[
        attempt_idx % len(candidates)
    ]


# ============================================================
# GENERATE ONE QUESTION
# ============================================================

def generate_question_from_context(
    retrieved_chunks,
    q_type="MCQ",
    difficulty="Medium",
    bloom_level="Understand",
    attempt_idx=0,
    question_type=None,
    **kwargs
):

    # --------------------------------------------------------
    # Question type
    # --------------------------------------------------------

    if question_type:
        q_type = question_type

    q_type = _safe_text(
        q_type
    ).strip().upper()

    aliases = {
        "MULTIPLE_CHOICE": "MCQ",
        "MULTIPLE CHOICE": "MCQ",

        "FILL":
            "FILL_IN_THE_BLANKS",

        "FILL_BLANKS":
            "FILL_IN_THE_BLANKS",

        "FILL IN THE BLANKS":
            "FILL_IN_THE_BLANKS",

        "TRUE/FALSE":
            "TRUE_FALSE",

        "TRUE / FALSE":
            "TRUE_FALSE",

        "SHORT":
            "SHORT_ANSWER",

        "SHORT ANSWER":
            "SHORT_ANSWER",

        "LONG":
            "LONG_ANSWER",

        "LONG ANSWER":
            "LONG_ANSWER",
    }

    q_type = aliases.get(
        q_type,
        q_type
    )

    if q_type == "ALL":

        q_type = QUESTION_TYPES[
            attempt_idx
            % len(QUESTION_TYPES)
        ]

    if q_type not in QUESTION_TYPES:
        q_type = "MCQ"

    # --------------------------------------------------------
    # Difficulty
    # --------------------------------------------------------

    difficulty = _safe_text(
        difficulty
    ).strip().capitalize()

    if difficulty not in SUPPORTED_DIFFICULTIES:
        difficulty = "Medium"

    # --------------------------------------------------------
    # Bloom
    # --------------------------------------------------------

    bloom_level = _safe_text(
        bloom_level
    ).strip().capitalize()

    if bloom_level not in SUPPORTED_BLOOM:
        bloom_level = "Understand"

    # --------------------------------------------------------
    # Context
    # --------------------------------------------------------

    context = _combine_chunks(
        retrieved_chunks
    )

    if not context:
        print(
            "[QG] No retrieved context."
        )
        return None

    # --------------------------------------------------------
    # Extract concepts
    # --------------------------------------------------------

    concepts = extract_educational_concepts(
        context,
        max_concepts=25
    )

    if not concepts:

        print(
            "[QG] No valid definition-backed concepts found."
        )

        return None

    # --------------------------------------------------------
    # Select clean concept
    # --------------------------------------------------------

    concept = _select_concept(
        concepts,
        attempt_idx
    )

    if not concept:
        return None

    subject = concept["subject"]
    definition = concept["definition"]

    print(
        "[QG] Selected source concept:",
        subject
    )

    print(
        "[QG] Concept definition:",
        _limit_words(
            definition,
            30
        )
    )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata = _get_metadata(
        retrieved_chunks
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # Only send a small context to FLAN.
    # --------------------------------------------------------

    small_context = _build_small_context(
        concept,
        ""
    )

    # --------------------------------------------------------
    # FLAN-T5
    # --------------------------------------------------------

    generated = _try_local_model(
        concept,
        q_type,
        difficulty,
        bloom_level,
        small_context
    )

    # --------------------------------------------------------
    # If FLAN succeeds
    # --------------------------------------------------------

    if generated:

        question = {
            "question":
                generated,

            "type":
                q_type,

            "question_type":
                q_type,

            "q_type":
                q_type,

            "options": [],

            "correct_answer": "",

            "answer": "",

            "difficulty":
                difficulty,

            "bloom_level":
                bloom_level,

            "source_page":
                metadata["source_page"],

            "source_chapter":
                metadata["source_chapter"],

            "source_topic":
                metadata["source_topic"],

            "concept":
                subject,

            "definition":
                definition,

            "generation_method":
                "FLAN-T5-SMALL",
        }

        # ----------------------------------------------------
        # MCQ
        # ----------------------------------------------------

        if q_type == "MCQ":
            distractors = generate_plausible_distractors(
                subject, concepts, 3, definition, context
            )
            if len(distractors) == 3:
                options = distractors + [subject]
                random.Random(
                    attempt_idx + sum(ord(c) for c in subject)
                ).shuffle(options)
                question["question"] = _build_mcq_stem(definition)
                question["options"] = options
                question["correct_answer"] = subject
                question["answer"] = subject
            else:
                question = None

        # ----------------------------------------------------
        # FILL
        # ----------------------------------------------------

        elif q_type == "FILL_IN_THE_BLANKS":

            question["correct_answer"] = subject
            question["answer"] = subject

        # ----------------------------------------------------
        # TRUE/FALSE
        # ----------------------------------------------------

        elif q_type == "TRUE_FALSE":
            statement, tf_answer = _build_true_false_item(
                subject, definition, concepts, attempt_idx
            )
            question["question"] = statement
            question["options"] = ["True", "False"]
            question["correct_answer"] = tf_answer
            question["answer"] = tf_answer

        # ----------------------------------------------------
        # SHORT/LONG
        # ----------------------------------------------------

        else:

            question["correct_answer"] = (
                definition
            )

            question["answer"] = (
                definition
            )

        # ----------------------------------------------------
        # Validate
        # ----------------------------------------------------

        if (
            question is not None
            and validate_question(
                question,
                q_type
            )
        ):

            question["quality_score"] = 1.0 if validate_question(question, q_type) else 0.0

            print(
                "[QG] FLAN question validated."
            )

            return question

        print(
            "[QG] FLAN question rejected."
        )

    # ========================================================
    # RULE-BASED FALLBACK
    # ========================================================

    print(
        "[QG] Using rule-based fallback."
    )

    fallback = _rule_based_question(
        concept,
        concepts,
        q_type,
        difficulty,
        bloom_level,
        metadata,
        attempt_idx,
        context
    )

    if (
        fallback
        and validate_question(
            fallback,
            q_type
        )
    ):

        fallback["quality_score"] = 1.0 if validate_question(fallback, q_type) else 0.0

        print(
            "[QG] Rule-based question accepted."
        )

        return fallback

    print(
        "[QG] Rule-based fallback rejected by validation."
    )
    print(
        "[QG] Fallback type:",
        q_type,
        "| Concept:",
        subject
    )
    print(
        "[QG] Fallback question:",
        fallback.get("question") if fallback else None
    )

    return None


# ============================================================
# GENERATE MULTIPLE QUESTIONS
# ============================================================

def generate_multiple_questions(
    retrieved_chunks,
    number_of_questions=5,
    q_type="MCQ",
    difficulty="Medium",
    bloom_level="Understand"
):

    questions = []
    used_questions = set()

    max_attempts = max(
        number_of_questions * 12,
        60
    )

    for attempt_idx in range(
        max_attempts
    ):

        if len(questions) >= number_of_questions:
            break

        question = generate_question_from_context(
            retrieved_chunks,
            q_type=q_type,
            difficulty=difficulty,
            bloom_level=bloom_level,
            attempt_idx=attempt_idx
        )

        if not question:
            continue

        question_text = _clean_generated_question(
            question.get(
                "question",
                ""
            )
        )

        question_key = question_text.casefold()

        if question_key in used_questions:
            print(
                "[QG] Duplicate question rejected."
            )
            continue

        # Reusing a concept is allowed when the requested paper
        # contains more questions than unique source concepts.
        # Exact duplicate questions are still rejected.
        used_questions.add(
            question_key
        )

        question["question_number"] = (
            len(questions) + 1
        )

        questions.append(
            question
        )

    return questions


# ============================================================
# DIAGNOSTIC
# ============================================================

def diagnose_context(retrieved_chunks):
    context = _combine_chunks(retrieved_chunks)
    concepts = extract_educational_concepts(context, max_concepts=50)
    print("\n[QG] DIAGNOSTIC VALID CONCEPTS")
    print("-" * 50)
    for i, concept in enumerate(concepts, 1):
        print(f"{i}. {concept['subject']} -> {concept['definition'][:120]}")
    if not concepts:
        print("[QG] No valid concepts found.")
    return concepts


# ============================================================
# SELF TEST
# ============================================================

if __name__ == "__main__":

    sample_text = """
    Cyber security is defined as the protection of
    Internet-connected systems, including hardware,
    software, and data from cyber attacks.

    Confidentiality refers to keeping sensitive
    information private and accessible only to
    authorized parties.

    Integrity means maintaining the accuracy and
    consistency of data.

    Availability means ensuring that information
    and systems are accessible when required.

    Malware is defined as software designed to
    damage, disrupt, or gain unauthorized access
    to computer systems.
    """

    print(
        "=" * 60
    )

    print(
        "SMART Q GEN"
    )

    print(
        "QUESTION GENERATOR SELF TEST"
    )

    print(
        "=" * 60
    )

    concepts = extract_educational_concepts(
        sample_text
    )

    print(
        "\nExtracted concepts:"
    )

    for concept in concepts:

        print(
            "-",
            concept["subject"]
        )

        print(
            "  Definition:",
            concept["definition"]
        )

        print(
            "  Score:",
            concept["quality_score"]
        )

    print(
        "\nModel:",
        MODEL_NAME
    )

    print(
        "\nSelf-test completed."
    )