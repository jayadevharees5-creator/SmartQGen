# modules/retriever.py
# Smart Q Gen
#
# ============================================================
# HYBRID RETRIEVAL
#
# BM25 + FAISS + RRF
#
# Complete document retrieval.
#
# IMPORTANT:
#
# Unit / Topic / Chapter are NOT used as filters.
#
# They are only metadata preserved in the retrieved chunks.
#
# Flow:
#
# Complete Document
#       ↓
# BM25
#       +
# FAISS
#       ↓
# RRF
#       ↓
# Top relevant chunks
#       ↓
# Question Generation
# ============================================================


import re
from typing import Any, Dict, List

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURATION
# ============================================================

EMBEDDING_MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)


# ------------------------------------------------------------
# IMPORTANT CHANGE
#
# Retrieve more candidate chunks before RRF.
#
# This gives the question generator access to more
# concepts from the uploaded document.
# ------------------------------------------------------------

BM25_TOP_K = 40

FAISS_TOP_K = 40

RRF_K = 60

DEFAULT_TOP_K = 30


# ------------------------------------------------------------
# Safety limits
# ------------------------------------------------------------

MIN_RETRIEVAL_TOP_K = 5

MAX_RETRIEVAL_TOP_K = 50


# ------------------------------------------------------------
# Cached embedding model
# ------------------------------------------------------------

_embedding_model = None


# ============================================================
# TEXT UTILITIES
# ============================================================

def _safe_text(value: Any) -> str:
    """
    Convert any value safely into text.
    """

    if value is None:
        return ""

    return str(value)


# ============================================================

def _normalize_text(text: Any) -> str:
    """
    Normalize text for comparison and duplicate detection.
    """

    text = _safe_text(
        text
    ).lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================

def _tokenize(text: Any) -> List[str]:
    """
    Tokenize text for BM25.
    """

    text = _normalize_text(
        text
    )

    return re.findall(
        r"\b[a-zA-Z0-9]+\b",
        text
    )


# ============================================================

def _get_chunk_text(
    chunk: Dict[str, Any]
) -> str:
    """
    Get the actual retrieval text from a chunk.
    """

    return _safe_text(
        chunk.get(
            "text",
            ""
        )
    )


# ============================================================
# SAFE TOP-K
# ============================================================

def _safe_top_k(
    value,
    default=DEFAULT_TOP_K
):
    """
    Normalize retrieval top_k.
    """

    try:

        value = int(
            value
        )

    except (
        ValueError,
        TypeError
    ):

        value = default

    if value < MIN_RETRIEVAL_TOP_K:

        value = MIN_RETRIEVAL_TOP_K

    if value > MAX_RETRIEVAL_TOP_K:

        value = MAX_RETRIEVAL_TOP_K

    return value


# ============================================================
# PREPARE CHUNKS
# ============================================================

def _prepare_chunks(
    chunks: List[Any]
) -> List[Dict[str, Any]]:
    """
    Prepare all document chunks.

    Every chunk receives a stable internal index.

    BM25 and FAISS use the same chunk collection.
    This allows RRF to identify the same chunk
    across both retrieval methods.
    """

    prepared = []

    for index, chunk in enumerate(
        chunks
    ):

        if isinstance(
            chunk,
            dict
        ):

            item = dict(
                chunk
            )

        else:

            item = {
                "text": _safe_text(
                    chunk
                )
            }

        item[
            "_chunk_index"
        ] = index

        prepared.append(
            item
        )

    return prepared


# ============================================================
# BM25 RETRIEVAL
# ============================================================

def bm25_search(
    chunks: List[Dict[str, Any]],
    query: str,
    top_k: int = BM25_TOP_K,
) -> List[Dict[str, Any]]:
    """
    Perform lexical retrieval using BM25.

    BM25 is useful when the query contains exact
    terminology from the document.
    """

    if not chunks:

        return []

    top_k = _safe_top_k(
        top_k,
        BM25_TOP_K
    )

    # --------------------------------------------------------
    # Tokenize complete document
    # --------------------------------------------------------

    documents = []

    for chunk in chunks:

        tokens = _tokenize(
            _get_chunk_text(
                chunk
            )
        )

        documents.append(
            tokens
        )

    if not any(
        documents
    ):

        return []

    # --------------------------------------------------------
    # Tokenize query
    # --------------------------------------------------------

    query_tokens = _tokenize(
        query
    )

    if not query_tokens:

        return []

    # --------------------------------------------------------
    # Build BM25
    # --------------------------------------------------------

    bm25 = BM25Okapi(
        documents
    )

    # --------------------------------------------------------
    # Calculate scores
    # --------------------------------------------------------

    scores = bm25.get_scores(
        query_tokens
    )

    # Highest score first.
    ranked_indices = np.argsort(
        scores
    )[::-1]

    results = []

    # --------------------------------------------------------
    # Collect candidates
    # --------------------------------------------------------

    for index in ranked_indices:

        index = int(
            index
        )

        score = float(
            scores[index]
        )

        # Ignore completely unrelated chunks.
        if score <= 0:

            continue

        chunk = dict(
            chunks[index]
        )

        chunk[
            "_bm25_score"
        ] = score

        results.append(
            chunk
        )

        if len(results) >= top_k:

            break

    return results


# ============================================================
# SENTENCE TRANSFORMER MODEL
# ============================================================

def _get_embedding_model():
    """
    Load SentenceTransformer only once.
    """

    global _embedding_model

    if _embedding_model is None:

        print()
        print(
            "[Retriever] Loading embedding model..."
        )

        print(
            EMBEDDING_MODEL_NAME
        )

        _embedding_model = (
            SentenceTransformer(
                EMBEDDING_MODEL_NAME
            )
        )

        print(
            "[Retriever] Embedding model loaded."
        )

    return _embedding_model


# ============================================================
# FAISS SEMANTIC RETRIEVAL
# ============================================================

def faiss_search(
    chunks: List[Dict[str, Any]],
    query: str,
    top_k: int = FAISS_TOP_K,
) -> List[Dict[str, Any]]:
    """
    Perform semantic retrieval using:

        SentenceTransformer
                ↓
        normalized embeddings
                ↓
        FAISS IndexFlatIP
    """

    if not chunks:

        return []

    top_k = _safe_top_k(
        top_k,
        FAISS_TOP_K
    )

    model = _get_embedding_model()

    # --------------------------------------------------------
    # Get complete document texts
    # --------------------------------------------------------

    texts = []

    valid_positions = []

    for position, chunk in enumerate(
        chunks
    ):

        text = _get_chunk_text(
            chunk
        ).strip()

        if not text:

            continue

        texts.append(
            text
        )

        valid_positions.append(
            position
        )

    if not texts:

        return []

    print(
        "[Retriever] Creating chunk embeddings..."
    )

    # --------------------------------------------------------
    # Encode all chunks
    # --------------------------------------------------------

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    if (
        embeddings.ndim != 2
        or embeddings.shape[0] == 0
    ):

        return []

    # --------------------------------------------------------
    # FAISS index
    # --------------------------------------------------------

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(
        embeddings
    )

    # --------------------------------------------------------
    # Encode query
    # --------------------------------------------------------

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    search_k = min(
        top_k,
        len(texts)
    )

    scores, indices = index.search(
        query_embedding,
        search_k
    )

    results = []

    # --------------------------------------------------------
    # Convert FAISS positions back to original chunks
    # --------------------------------------------------------

    for score, local_position in zip(
        scores[0],
        indices[0]
    ):

        local_position = int(
            local_position
        )

        if local_position < 0:

            continue

        if local_position >= len(
            valid_positions
        ):

            continue

        original_position = (
            valid_positions[
                local_position
            ]
        )

        chunk = dict(
            chunks[
                original_position
            ]
        )

        chunk[
            "_faiss_score"
        ] = float(
            score
        )

        results.append(
            chunk
        )

    return results


# ============================================================
# RECIPROCAL RANK FUSION
# ============================================================

def reciprocal_rank_fusion(
    bm25_results: List[Dict[str, Any]],
    faiss_results: List[Dict[str, Any]],
    top_k: int = DEFAULT_TOP_K,
) -> List[Dict[str, Any]]:
    """
    Combine BM25 and FAISS using Reciprocal Rank Fusion.

    Formula:

        RRF = 1 / (RRF_K + rank)

    A chunk appearing in both systems receives
    a stronger combined score.
    """

    top_k = _safe_top_k(
        top_k,
        DEFAULT_TOP_K
    )

    fused = {}

    # ========================================================
    # BM25
    # ========================================================

    for rank, chunk in enumerate(
        bm25_results,
        start=1
    ):

        chunk_index = chunk.get(
            "_chunk_index"
        )

        if chunk_index is None:

            continue

        if chunk_index not in fused:

            fused[
                chunk_index
            ] = {

                "chunk": chunk,

                "score": 0.0,

                "bm25_rank": None,

                "faiss_rank": None
            }

        fused[
            chunk_index
        ][
            "score"
        ] += (
            1.0
            / (
                RRF_K + rank
            )
        )

        fused[
            chunk_index
        ][
            "bm25_rank"
        ] = rank

    # ========================================================
    # FAISS
    # ========================================================

    for rank, chunk in enumerate(
        faiss_results,
        start=1
    ):

        chunk_index = chunk.get(
            "_chunk_index"
        )

        if chunk_index is None:

            continue

        if chunk_index not in fused:

            fused[
                chunk_index
            ] = {

                "chunk": chunk,

                "score": 0.0,

                "bm25_rank": None,

                "faiss_rank": None
            }

        fused[
            chunk_index
        ][
            "score"
        ] += (
            1.0
            / (
                RRF_K + rank
            )
        )

        fused[
            chunk_index
        ][
            "faiss_rank"
        ] = rank

    # ========================================================
    # SORT
    # ========================================================

    ranked = sorted(
        fused.values(),
        key=lambda item:
            item["score"],
        reverse=True
    )

    results = []

    for item in ranked[:top_k]:

        chunk = dict(
            item["chunk"]
        )

        chunk[
            "_rrf_score"
        ] = item[
            "score"
        ]

        chunk[
            "_bm25_rank"
        ] = item[
            "bm25_rank"
        ]

        chunk[
            "_faiss_rank"
        ] = item[
            "faiss_rank"
        ]

        results.append(
            chunk
        )

    return results


# ============================================================
# REMOVE INTERNAL FIELDS
# ============================================================

def _remove_internal_fields(
    chunks: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Remove temporary retrieval fields.

    Document metadata remains untouched.
    """

    internal_fields = {

        "_chunk_index",

        "_bm25_score",

        "_faiss_score",

        "_rrf_score",

        "_bm25_rank",

        "_faiss_rank"
    }

    cleaned = []

    for chunk in chunks:

        item = dict(
            chunk
        )

        for field in internal_fields:

            item.pop(
                field,
                None
            )

        cleaned.append(
            item
        )

    return cleaned


# ============================================================
# MAIN HYBRID RETRIEVER
# ============================================================

def retrieve_relevant_chunks(
    chunks: List[Any],
    query: str,
    top_k: int = DEFAULT_TOP_K,
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant chunks from the COMPLETE document.

    No Unit filtering.
    No Topic filtering.
    No Chapter filtering.

    All chunks participate.

    The returned chunks retain:

        page
        chapter
        chapter_title
        unit
        unit_title
        topic
        topics
        text
    """

    print()
    print(
        "========================================"
    )

    print(
        "HYBRID RAG RETRIEVAL"
    )

    print(
        "========================================"
    )

    print(
        "Query:",
        query
    )

    if not chunks:

        print(
            "[Retriever] No chunks available."
        )

        return []

    if not query or not str(
        query
    ).strip():

        print(
            "[Retriever] Empty query."
        )

        return []

    top_k = _safe_top_k(
        top_k,
        DEFAULT_TOP_K
    )

    # --------------------------------------------------------
    # Prepare complete document.
    # --------------------------------------------------------

    prepared_chunks = _prepare_chunks(
        chunks
    )

    print(
        "[Retriever] Total document chunks:",
        len(prepared_chunks)
    )

    # ========================================================
    # BM25
    # ========================================================

    print()
    print(
        "[Retriever] 1. BM25 retrieval..."
    )

    bm25_results = bm25_search(
        prepared_chunks,
        query,
        top_k=BM25_TOP_K
    )

    print(
        "[Retriever] BM25 candidates:",
        len(bm25_results)
    )

    # ========================================================
    # FAISS
    # ========================================================

    print()
    print(
        "[Retriever] 2. FAISS semantic retrieval..."
    )

    faiss_results = faiss_search(
        prepared_chunks,
        query,
        top_k=FAISS_TOP_K
    )

    print(
        "[Retriever] FAISS candidates:",
        len(faiss_results)
    )

    # ========================================================
    # RRF
    # ========================================================

    print()
    print(
        "[Retriever] 3. RRF fusion..."
    )

    fused_results = reciprocal_rank_fusion(
        bm25_results,
        faiss_results,
        top_k=top_k
    )

    # ========================================================
    # DUPLICATE PROTECTION
    # ========================================================

    final_results = []

    seen_indices = set()

    seen_text = set()

    for chunk in fused_results:

        chunk_index = chunk.get(
            "_chunk_index"
        )

        text_key = _normalize_text(
            chunk.get(
                "text",
                ""
            )
        )

        # Prefer stable chunk index.
        if chunk_index is not None:

            if chunk_index in seen_indices:

                continue

            seen_indices.add(
                chunk_index
            )

        elif text_key:

            if text_key in seen_text:

                continue

            seen_text.add(
                text_key
            )

        final_results.append(
            chunk
        )

    # ========================================================
    # DISPLAY
    # ========================================================

    print()

    print(
        "[Retriever] Final chunks:",
        len(final_results)
    )

    print()

    print(
        "[Retriever] Retrieved concepts:"
    )

    concepts = []

    for index, chunk in enumerate(
        final_results,
        start=1
    ):

        topics = chunk.get(
            "topics",
            []
        )

        if isinstance(
            topics,
            list
        ):

            concepts.extend(
                topics
            )

        page = chunk.get(
            "page",
            "N/A"
        )

        unit = chunk.get(
            "unit",
            "N/A"
        )

        topic = chunk.get(
            "topic",
            "N/A"
        )

        rrf_score = chunk.get(
            "_rrf_score",
            0.0
        )

        print(
            f"{index}. "
            f"Page={page} | "
            f"Unit={unit} | "
            f"Topic={topic} | "
            f"RRF={rrf_score:.6f}"
        )

    # --------------------------------------------------------
    # Unique concept display
    # --------------------------------------------------------

    unique_concepts = []

    seen_concepts = set()

    for concept in concepts:

        concept = str(
            concept
        ).strip()

        if not concept:

            continue

        key = concept.casefold()

        if key in seen_concepts:

            continue

        seen_concepts.add(
            key
        )

        unique_concepts.append(
            concept
        )

    print()

    print(
        "[Retriever] Unique concepts in retrieved chunks:",
        len(unique_concepts)
    )

    print(
        unique_concepts
    )

    print(
        "========================================"
    )

    return _remove_internal_fields(
        final_results
    )


# ============================================================
# MULTI-QUERY RETRIEVAL
# ============================================================

def retrieve_from_multiple_queries(
    chunks: List[Any],
    queries: List[str],
    top_k: int = DEFAULT_TOP_K,
) -> List[Dict[str, Any]]:
    """
    Retrieve using multiple queries.

    Results are merged by chunk index/text.

    This is useful when the question generator wants
    broader coverage of a document.
    """

    if not chunks:

        return []

    if not queries:

        return []

    top_k = _safe_top_k(
        top_k,
        DEFAULT_TOP_K
    )

    merged = []

    seen_indices = set()

    seen_text = set()

    for query in queries:

        if not query:

            continue

        results = retrieve_relevant_chunks(
            chunks,
            query,
            top_k=top_k
        )

        for chunk in results:

            chunk_index = chunk.get(
                "chunk_id"
            )

            text_key = _normalize_text(
                chunk.get(
                    "text",
                    ""
                )
            )

            if (
                chunk_index is not None
                and chunk_index in seen_indices
            ):

                continue

            if (
                chunk_index is None
                and text_key in seen_text
            ):

                continue

            if chunk_index is not None:

                seen_indices.add(
                    chunk_index
                )

            if text_key:

                seen_text.add(
                    text_key
                )

            merged.append(
                chunk
            )

            # Allow enough chunks for concept
            # extraction before stopping.

            if len(merged) >= top_k:

                return merged

    return merged


# ============================================================
# SELF TEST
# ============================================================

if __name__ == "__main__":

    print(
        "========================================"
    )

    print(
        "SMART Q GEN - RETRIEVER TEST"
    )

    print(
        "========================================"
    )

    sample_chunks = [

        {
            "chunk_id": 1,

            "text": (
                "A database is an organized collection "
                "of related data."
            ),

            "page": 1,

            "chapter": "Chapter 1",

            "unit": "Unit 1",

            "topic": "Database",

            "topics": [
                "Database"
            ]
        },

        {
            "chunk_id": 2,

            "text": (
                "A primary key is a field that uniquely "
                "identifies a record."
            ),

            "page": 2,

            "chapter": "Chapter 1",

            "unit": "Unit 1",

            "topic": "Primary Key",

            "topics": [
                "Primary Key"
            ]
        },

        {
            "chunk_id": 3,

            "text": (
                "Normalization organizes data to reduce "
                "redundancy and improve database design."
            ),

            "page": 3,

            "chapter": "Chapter 1",

            "unit": "Unit 2",

            "topic": "Normalization",

            "topics": [
                "Normalization"
            ]
        },

        {
            "chunk_id": 4,

            "text": (
                "A transaction is a sequence of operations "
                "treated as one logical unit."
            ),

            "page": 4,

            "chapter": "Chapter 2",

            "unit": "Unit 3",

            "topic": "Transaction",

            "topics": [
                "Transaction"
            ]
        }
    ]

    results = retrieve_relevant_chunks(
        sample_chunks,
        "primary key uniquely identifies record",
        top_k=3
    )

    print()

    print(
        "Retrieved results:"
    )

    for index, result in enumerate(
        results,
        start=1
    ):

        print()

        print(
            index,
            result.get(
                "topic"
            )
        )

        print(
            result.get(
                "text"
            )
        )

    print()

    print(
        "========================================"
    )

    print(
        "RETRIEVER TEST COMPLETED"
    )

    print(
        "========================================"
    )