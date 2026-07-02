from dataclasses import dataclass
import re
from functools import lru_cache

from meddra.models import MedDraTerm


SUPPORTED_TERM_TYPES = ('PT', 'LT')


@dataclass(frozen=True)
class SymptomExtractionResult:
    symptoms: list[str]
    raw_text: str


def extract_symptoms(text: str) -> SymptomExtractionResult:
    normalized_text = text.strip()
    lowered_text = normalized_text.lower()
    matched_terms = []

    for normalized_name, term_name in _get_meddra_terms():
        if _matches_phrase(lowered_text, normalized_name):
            matched_terms.append(term_name)

    return SymptomExtractionResult(symptoms=sorted(set(matched_terms)), raw_text=normalized_text)


@lru_cache(maxsize=1)
def _get_meddra_terms() -> tuple[tuple[str, str], ...]:
    return tuple(
        MedDraTerm.objects.filter(term_type__in=SUPPORTED_TERM_TYPES)
        .values_list('normalized_name', 'term_name')
        .distinct()
    )


def clear_meddra_term_cache() -> None:
    _get_meddra_terms.cache_clear()


def _matches_phrase(text: str, phrase: str) -> bool:
    if not phrase:
        return False
    return re.search(rf'\b{re.escape(phrase)}\b', text) is not None