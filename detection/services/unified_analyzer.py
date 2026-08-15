"""
Unified ADR Analysis Pipeline.

Given a single free-text clinical description, this service:

1.  Extracts drug names     → drug_extractor  (spaCy PhraseMatcher over Drug DB)
2.  Extracts MedDRA symptoms → nlp_extractor   (spaCy PhraseMatcher over MedDRA DB)
3.  Checks every drug pair  → ddi_checker      (DrugInteraction lookups)
4.  Suggests safer alternatives for each interacting drug → recommender.services

Returns a single AnalysisResult dataclass.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations

from .drug_extractor import extract_drugs
from .nlp_extractor import extract_symptoms
from .ddi_checker import check_pair, InteractionCheckResult
from recommender.services import recommend_safer_alternatives


@dataclass(frozen=True)
class DrugInteractionSummary:
    drug_a: str
    drug_b: str
    severity: str
    description: str


@dataclass
class AnalysisResult:
    raw_text: str = ""
    drugs_found: list[str] = field(default_factory=list)
    symptoms_found: list[str] = field(default_factory=list)
    interactions: list[DrugInteractionSummary] = field(default_factory=list)
    # drug_name → list of safer alternative names
    alternatives: dict[str, list[str]] = field(default_factory=dict)

    # Convenience helpers used in templates
    @property
    def has_interactions(self) -> bool:
        return bool(self.interactions)

    @property
    def has_results(self) -> bool:
        return bool(self.drugs_found or self.symptoms_found)


def analyze(text: str, alternatives_limit: int = 5) -> AnalysisResult:
    """
    Run the full unified analysis pipeline on *text*.

    Parameters
    ----------
    text:
        Free-text clinical description supplied by the user.
    alternatives_limit:
        Maximum number of safer alternative drugs to suggest per drug.
    """
    result = AnalysisResult(raw_text=text.strip())

    # ── 1. Extract drug names ──────────────────────────────────────────────
    result.drugs_found = extract_drugs(text)

    # ── 2. Extract MedDRA symptom terms ───────────────────────────────────
    symptom_result = extract_symptoms(text)
    result.symptoms_found = symptom_result.symptoms

    # ── 3. Check every unique drug pair for interactions ──────────────────
    interacting_drugs: set[str] = set()

    for drug_a, drug_b in combinations(result.drugs_found, 2):
        check: InteractionCheckResult = check_pair(drug_a, drug_b)
        if check.is_risky:
            result.interactions.append(
                DrugInteractionSummary(
                    drug_a=drug_a,
                    drug_b=drug_b,
                    severity=check.severity,
                    description=check.description,
                )
            )
            interacting_drugs.add(drug_a)
            interacting_drugs.add(drug_b)

    # ── 4. Suggest safer alternatives for each drug in an interaction ─────
    for drug_name in sorted(interacting_drugs):
        alts = recommend_safer_alternatives(drug_name, limit=alternatives_limit)
        result.alternatives[drug_name] = alts

    return result
