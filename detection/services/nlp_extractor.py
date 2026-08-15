"""
NLP-based symptom extractor.

Uses a spaCy PhraseMatcher loaded with every PT/LT MedDRA term so that
adverse-reaction descriptions are tokenised properly before matching —
catching plurals, mixed case, punctuation boundaries, and multi-word
expressions that simple substring search would miss.

The spaCy model and PhraseMatcher are built once and cached at module level
for zero per-request overhead after the first call.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import TYPE_CHECKING

import spacy
from spacy.matcher import PhraseMatcher

if TYPE_CHECKING:
    from spacy.language import Language

# Only Preferred Terms and Lower-Level Terms carry useful clinical meaning.
SUPPORTED_TERM_TYPES: tuple[str, ...] = ("PT", "LT")

# spaCy model to use for tokenisation.
# en_core_web_sm is compact and sufficient for tokenisation; swap to
# en_core_web_lg or a scispacy model later for richer embeddings.
SPACY_MODEL = "en_core_web_sm"


@dataclass(frozen=True)
class SymptomExtractionResult:
    symptoms: list[str] = field(default_factory=list)
    raw_text: str = ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_symptoms(text: str) -> SymptomExtractionResult:
    """Return MedDRA terms found in *text* using NLP-based phrase matching."""
    normalized_text = text.strip()
    if not normalized_text:
        return SymptomExtractionResult(symptoms=[], raw_text=normalized_text)

    nlp, matcher, match_id_to_term = _get_nlp_pipeline()
    doc = nlp(normalized_text)

    found: set[str] = set()
    for match_id, _start, _end in matcher(doc):
        term_name = match_id_to_term.get(match_id)
        if term_name:
            found.add(term_name)

    return SymptomExtractionResult(
        symptoms=sorted(found),
        raw_text=normalized_text,
    )


def clear_meddra_term_cache() -> None:
    """Invalidate the cached NLP pipeline (e.g. after a MedDRA re-import)."""
    _get_meddra_terms.cache_clear()
    _get_nlp_pipeline.cache_clear()


# ---------------------------------------------------------------------------
# Private helpers (cached)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _get_nlp_pipeline() -> tuple["Language", PhraseMatcher, dict[int, str]]:
    """
    Build and cache the spaCy NLP pipeline + PhraseMatcher.

    Returns
    -------
    nlp
        The loaded spaCy Language model.
    matcher
        A PhraseMatcher pre-loaded with all supported MedDRA terms.
        Matching is performed on the ``LOWER`` token attribute so that
        capitalisation differences are handled automatically.
    match_id_to_term
        Mapping of the integer match-id that spaCy returns back to the
        human-readable MedDRA term name.
    """
    # Disable heavy components we do not need — just the tokeniser is enough.
    nlp: "Language" = spacy.load(SPACY_MODEL, disable=["parser", "ner", "lemmatizer"])

    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    match_id_to_term: dict[int, str] = {}

    for normalized_name, term_name in _get_meddra_terms():
        if not normalized_name:
            continue
        # Each term gets a unique string key so we can recover the display name.
        key = f"MEDDRA_{term_name}"
        pattern = nlp.make_doc(normalized_name)
        matcher.add(key, [pattern])
        string_id = nlp.vocab.strings[key]
        match_id_to_term[string_id] = term_name

    return nlp, matcher, match_id_to_term


@lru_cache(maxsize=1)
def _get_meddra_terms() -> tuple[tuple[str, str], ...]:
    """Fetch (normalized_name, term_name) pairs from the database (cached)."""
    from meddra.models import MedDraTerm  # local import avoids app-registry issues

    return tuple(
        MedDraTerm.objects
        .filter(term_type__in=SUPPORTED_TERM_TYPES)
        .values_list("normalized_name", "term_name")
        .distinct()
    )