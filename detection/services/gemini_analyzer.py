"""
Gemini-powered ADR analysis service.

Sends a structured prompt to the Gemini API and returns a parsed
AnalysisResult containing drugs, symptoms, interactions and safer
alternatives — all inferred by the language model from the user's
free-text clinical description.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

import google.genai as genai
from google.genai import types as genai_types
from decouple import config

# ── Configuration ────────────────────────────────────────────────────────────

_API_KEY = config("GEMINI_API_KEY", default="")
_CLIENT: genai.Client | None = None


def _get_client() -> genai.Client:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = genai.Client(api_key=_API_KEY)
    return _CLIENT

# ── Result dataclasses (mirrors unified_analyzer.AnalysisResult) ─────────────

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
    alternatives: dict[str, list[str]] = field(default_factory=dict)
    error: str = ""

    @property
    def has_interactions(self) -> bool:
        return bool(self.interactions)

    @property
    def has_results(self) -> bool:
        return bool(self.drugs_found or self.symptoms_found)


# ── Prompt ───────────────────────────────────────────────────────────────────

_PROMPT_TEMPLATE = """
You are a clinical pharmacology assistant specialising in adverse drug reactions (ADRs) and drug-drug interactions (DDIs).

Analyse the following patient clinical description and return a JSON object — nothing else, no markdown fences, just raw JSON.

The JSON must have exactly these keys:
- "drugs_found":    list of drug names mentioned or implied in the text
- "symptoms_found": list of adverse reaction / symptom terms (use MedDRA preferred terms where possible)
- "interactions":   list of objects, one per drug pair with a known interaction:
    {{ "drug_a": str, "drug_b": str, "severity": "high"|"moderate"|"low", "description": str }}
- "alternatives":   object mapping each drug involved in an interaction to a list of 3-5 safer alternative drug names:
    {{ "DrugName": ["Alt1", "Alt2", ...], ... }}

Rules:
- Only report interactions that are clinically established.
- If no interactions exist, return an empty list for "interactions" and an empty object for "alternatives".
- All drug and symptom names should be in English.
- Do not include any explanation outside the JSON.

Clinical description:
\"\"\"
{clinical_text}
\"\"\"
""".strip()

# ── Public API ────────────────────────────────────────────────────────────────

def analyze(clinical_text: str) -> AnalysisResult:
    """
    Run the full Gemini-powered ADR analysis on *clinical_text*.

    Returns an AnalysisResult. If the API key is missing or the call fails,
    returns an AnalysisResult with a non-empty ``error`` field.
    """
    result = AnalysisResult(raw_text=clinical_text.strip())

    if not _API_KEY:
        result.error = (
            "GEMINI_API_KEY is not set. Please add it to your .env file."
        )
        return result

    prompt = _PROMPT_TEMPLATE.format(clinical_text=clinical_text.strip())

    try:
        client = _get_client()
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        raw = response.text.strip()

        # Strip markdown fences if the model wraps anyway
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)

        data = json.loads(raw)

        result.drugs_found = [str(d) for d in data.get("drugs_found", [])]
        result.symptoms_found = [str(s) for s in data.get("symptoms_found", [])]

        for ixn in data.get("interactions", []):
            result.interactions.append(
                DrugInteractionSummary(
                    drug_a=str(ixn.get("drug_a", "")),
                    drug_b=str(ixn.get("drug_b", "")),
                    severity=str(ixn.get("severity", "")).lower(),
                    description=str(ixn.get("description", "")),
                )
            )

        for drug_name, alts in data.get("alternatives", {}).items():
            result.alternatives[str(drug_name)] = [str(a) for a in alts]

    except json.JSONDecodeError as exc:
        result.error = f"Could not parse Gemini response as JSON: {exc}"
    except Exception as exc:  # noqa: BLE001
        result.error = f"Gemini API error: {exc}"

    return result
