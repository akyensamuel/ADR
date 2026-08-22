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
        return bool(self.drugs_found or self.symptoms_found) or bool(self.error)


@dataclass(frozen=True)
class InteractionCheckResult:
    is_risky: bool
    severity: str = ''
    description: str = ''
    alternatives: list[str] = field(default_factory=list)
    error: str = ""


@dataclass(frozen=True)
class SymptomExtractionResult:
    symptoms: list[str] = field(default_factory=list)
    raw_text: str = ""
    error: str = ""


@dataclass(frozen=True)
class SaferAlternativesResult:
    alternatives: list[str] = field(default_factory=list)
    error: str = ""


# ── Prompts ───────────────────────────────────────────────────────────────────

_PROMPT_UNIFIED = """
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

_PROMPT_INTERACTION = """
You are a clinical pharmacology assistant. Check for known drug-drug interactions between the following two drugs:
Drug A: {drug_a}
Drug B: {drug_b}

Return a JSON object — nothing else, no markdown fences, just raw JSON.

The JSON must have exactly these keys:
- "is_risky": boolean (true if there is a known clinical interaction, false otherwise)
- "severity": string ("high", "moderate", "low", or "" if no interaction)
- "description": string (explain the interaction mechanism and risk, or state that none is known)
- "alternatives": list of strings (if there is an interaction, suggest 2-4 safer alternatives for one of the drugs; otherwise empty list)

Do not include any explanation outside the JSON.
""".strip()

_PROMPT_SYMPTOMS = """
You are a clinical pharmacology assistant. Extract all adverse drug reaction symptoms from the following clinical notes.

Return a JSON object — nothing else, no markdown fences, just raw JSON.

The JSON must have exactly this key:
- "symptoms": list of strings (map the extracted symptoms to standard MedDRA preferred terms where possible. e.g. "headache", "nausea")

Clinical notes:
\"\"\"
{clinical_notes}
\"\"\"
""".strip()

_PROMPT_ALTERNATIVES = """
You are a clinical pharmacology assistant. Provide a list of 3-5 safer therapeutic alternatives for the following drug:
Drug: {drug_name}

Return a JSON object — nothing else, no markdown fences, just raw JSON.

The JSON must have exactly this key:
- "alternatives": list of strings (the names of the alternative drugs)

Do not include any explanation outside the JSON.
""".strip()


# ── Internal Helpers ──────────────────────────────────────────────────────────

def _call_gemini_json(prompt: str) -> dict | str:
    """Helper to call Gemini and parse JSON, returning dict on success or string on error."""
    if not _API_KEY:
        return "GEMINI_API_KEY is not set. Please add it to your .env file."
        
    try:
        client = _get_client()
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        raw = response.text.strip()
        
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)
        
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        return f"Could not parse Gemini response as JSON: {exc}"
    except Exception as exc:  # noqa: BLE001
        return f"Gemini API error: {exc}"


# ── Public API ────────────────────────────────────────────────────────────────

def analyze(clinical_text: str) -> AnalysisResult:
    """Run the full Gemini-powered ADR analysis on *clinical_text*."""
    result = AnalysisResult(raw_text=clinical_text.strip())
    
    prompt = _PROMPT_UNIFIED.format(clinical_text=clinical_text.strip())
    data_or_err = _call_gemini_json(prompt)
    
    if isinstance(data_or_err, str):
        result.error = data_or_err
        return result

    result.drugs_found = [str(d) for d in data_or_err.get("drugs_found", [])]
    result.symptoms_found = [str(s) for s in data_or_err.get("symptoms_found", [])]

    for ixn in data_or_err.get("interactions", []):
        result.interactions.append(
            DrugInteractionSummary(
                drug_a=str(ixn.get("drug_a", "")),
                drug_b=str(ixn.get("drug_b", "")),
                severity=str(ixn.get("severity", "")).lower(),
                description=str(ixn.get("description", "")),
            )
        )

    for drug_name, alts in data_or_err.get("alternatives", {}).items():
        result.alternatives[str(drug_name)] = [str(a) for a in alts]

    return result


def check_interaction_pair(drug_a: str, drug_b: str) -> InteractionCheckResult:
    """Check specifically for an interaction between two drugs using Gemini."""
    prompt = _PROMPT_INTERACTION.format(drug_a=drug_a.strip(), drug_b=drug_b.strip())
    data_or_err = _call_gemini_json(prompt)
    
    if isinstance(data_or_err, str):
        return InteractionCheckResult(is_risky=False, error=data_or_err)
        
    return InteractionCheckResult(
        is_risky=bool(data_or_err.get("is_risky", False)),
        severity=str(data_or_err.get("severity", "")).lower(),
        description=str(data_or_err.get("description", "")),
        alternatives=[str(a) for a in data_or_err.get("alternatives", [])]
    )


def extract_symptoms(clinical_notes: str) -> SymptomExtractionResult:
    """Extract symptoms from text using Gemini."""
    normalized_text = clinical_notes.strip()
    
    prompt = _PROMPT_SYMPTOMS.format(clinical_notes=normalized_text)
    data_or_err = _call_gemini_json(prompt)
    
    if isinstance(data_or_err, str):
        return SymptomExtractionResult(raw_text=normalized_text, error=data_or_err)
        
    return SymptomExtractionResult(
        symptoms=[str(s) for s in data_or_err.get("symptoms", [])],
        raw_text=normalized_text
    )


def get_safer_alternatives(drug_name: str) -> SaferAlternativesResult:
    """Get safer alternatives for a drug using Gemini."""
    prompt = _PROMPT_ALTERNATIVES.format(drug_name=drug_name.strip())
    data_or_err = _call_gemini_json(prompt)
    
    if isinstance(data_or_err, str):
        return SaferAlternativesResult(error=data_or_err)
        
    return SaferAlternativesResult(
        alternatives=[str(a) for a in data_or_err.get("alternatives", [])]
    )

