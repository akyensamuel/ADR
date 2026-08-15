"""
Drug name extractor — spaCy PhraseMatcher over the Drug database.

Mirrors the design of nlp_extractor.py:
- Loads all Drug names from the database as tokenised phrase patterns.
- Matches case-insensitively using the LOWER token attribute.
- The matcher and vocabulary are cached at module level so they are only
  built once per server process.
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

import spacy
from spacy.matcher import PhraseMatcher

if TYPE_CHECKING:
    from spacy.language import Language

SPACY_MODEL = "en_core_web_sm"


@lru_cache(maxsize=1)
def _get_nlp_and_matcher() -> tuple["Language", PhraseMatcher, dict[int, str]]:
    """
    Build and cache the spaCy pipeline + PhraseMatcher over Drug names.

    Returns
    -------
    nlp
        The loaded spaCy Language object (tokeniser only).
    matcher
        PhraseMatcher pre-loaded with every Drug name.
    match_id_to_name
        Maps spaCy integer match-id → canonical Drug.name string.
    """
    nlp: "Language" = spacy.load(SPACY_MODEL, disable=["parser", "ner", "lemmatizer"])
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    match_id_to_name: dict[int, str] = {}

    for drug_name in _get_drug_names():
        if not drug_name:
            continue
        key = f"DRUG_{drug_name.upper()}"
        pattern = nlp.make_doc(drug_name)
        matcher.add(key, [pattern])
        string_id = nlp.vocab.strings[key]
        match_id_to_name[string_id] = drug_name

    return nlp, matcher, match_id_to_name


@lru_cache(maxsize=1)
def _get_drug_names() -> tuple[str, ...]:
    """Fetch all active Drug names from the database (cached)."""
    from drugs.models import Drug  # local import avoids app-registry issues
    return tuple(Drug.objects.filter(is_active=True).values_list("name", flat=True))


def extract_drugs(text: str) -> list[str]:
    """
    Return a sorted list of Drug names found in *text*.

    Matching is case-insensitive and token-boundary aware.
    """
    text = text.strip()
    if not text:
        return []

    nlp, matcher, match_id_to_name = _get_nlp_and_matcher()
    doc = nlp(text)

    found: set[str] = set()
    for match_id, _start, _end in matcher(doc):
        name = match_id_to_name.get(match_id)
        if name:
            found.add(name)

    return sorted(found)


def clear_drug_cache() -> None:
    """Invalidate cached drug names and matcher (e.g. after importing new drugs)."""
    _get_drug_names.cache_clear()
    _get_nlp_and_matcher.cache_clear()
