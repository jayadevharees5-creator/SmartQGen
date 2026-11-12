# modules/bloom_controller.py
# Smart Q Gen
# Bloom's Taxonomy Directives and Action Verbs Controller


# ============================================================
# BLOOM'S TAXONOMY LEVELS
# ============================================================

BLOOM_LEVELS = {

    "Remember": {

        "action_verbs": [
            "define",
            "identify",
            "list",
            "recall",
            "name",
            "state",
            "label"
        ],

        "instruction": (
            "Focus on direct recall of definitions, key terms, "
            "facts, or named concepts from the context."
        )
    },

    "Understand": {

        "action_verbs": [
            "explain",
            "describe",
            "summarize",
            "interpret",
            "classify",
            "discuss"
        ],

        "instruction": (
            "Focus on comprehension, explaining why or how concepts "
            "function, and summarizing relationships."
        )
    },

    "Apply": {

        "action_verbs": [
            "solve",
            "calculate",
            "demonstrate",
            "apply",
            "use",
            "compute",
            "implement"
        ],

        "instruction": (
            "Focus on applying formulas, rules, methods, or procedures "
            "to specific problem instances."
        )
    },

    "Analyze": {

        "action_verbs": [
            "compare",
            "differentiate",
            "analyze",
            "contrast",
            "distinguish",
            "deconstruct"
        ],

        "instruction": (
            "Focus on breaking down concepts, comparing differences, "
            "analyzing components, and recognizing patterns."
        )
    },

    "Evaluate": {

        "action_verbs": [
            "justify",
            "assess",
            "evaluate",
            "critique",
            "judge",
            "defend",
            "recommend"
        ],

        "instruction": (
            "Focus on evaluating choices, justifying solutions, "
            "assessing validity, or critiquing statements."
        )
    },

    "Create": {

        "action_verbs": [
            "design",
            "construct",
            "develop",
            "formulate",
            "propose",
            "synthesize"
        ],

        "instruction": (
            "Focus on synthesizing ideas, designing solutions, "
            "or creating original formulations based on context."
        )
    }
}


# ============================================================
# DEFAULT BLOOM LEVEL
# ============================================================

DEFAULT_BLOOM_LEVEL = "Understand"


# ============================================================
# GET BLOOM INFORMATION
# ============================================================

def get_bloom_info(level: str) -> dict:
    """
    Return the complete Bloom's Taxonomy information
    for the requested level.

    If the supplied level is invalid, Understand is used.
    """

    if not level:
        level = DEFAULT_BLOOM_LEVEL

    # Normalize first letter/casing
    normalized_level = str(level).strip()

    if normalized_level not in BLOOM_LEVELS:
        normalized_level = DEFAULT_BLOOM_LEVEL

    return BLOOM_LEVELS[
        normalized_level
    ]


# ============================================================
# GET BLOOM DIRECTIVE
# ============================================================

def get_bloom_directive(level: str) -> str:
    """
    Build the instruction that will be passed to the
    question-generation stage.
    """

    normalized_level = (
        str(level).strip()
        if level
        else DEFAULT_BLOOM_LEVEL
    )

    if normalized_level not in BLOOM_LEVELS:
        normalized_level = DEFAULT_BLOOM_LEVEL

    info = BLOOM_LEVELS[
        normalized_level
    ]

    verbs = ", ".join(
        info["action_verbs"]
    )

    return (
        f"Bloom's Level ({normalized_level}): "
        f"{info['instruction']} "
        f"Action verbs to use: {verbs}."
    )


# ============================================================
# GET BLOOM ACTION VERBS
# ============================================================

def get_bloom_verbs(level: str) -> list:
    """
    Return the action verbs associated with a
    Bloom's Taxonomy level.
    """

    info = get_bloom_info(
        level
    )

    return list(
        info["action_verbs"]
    )


# ============================================================
# GET SUPPORTED LEVELS
# ============================================================

def get_supported_bloom_levels() -> list:
    """
    Return all supported Bloom's Taxonomy levels.
    """

    return list(
        BLOOM_LEVELS.keys()
    )


# ============================================================
# SELF TEST
# ============================================================

if __name__ == "__main__":

    print(
        "========================================"
    )

    print(
        "SMART Q GEN - BLOOM CONTROLLER TEST"
    )

    print(
        "========================================"
    )

    for level in get_supported_bloom_levels():

        print()
        print(
            "Level:",
            level
        )

        print(
            "Verbs:",
            ", ".join(
                get_bloom_verbs(level)
            )
        )

        print(
            "Directive:"
        )

        print(
            get_bloom_directive(level)
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