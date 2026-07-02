from dataclasses import dataclass
import re


COMMON_SYMPTOMS = {
    'chest pain': 'chest pain',
    'dizziness': 'dizziness',
    'diarrhea': 'diarrhea',
    'fatigue': 'fatigue',
    'fever': 'fever',
    'headache': 'headache',
    'nausea': 'nausea',
    'rash': 'rash',
    'shortness of breath': 'shortness of breath',
    'swelling': 'swelling',
    'vomiting': 'vomiting',
}


@dataclass(frozen=True)
class SymptomExtractionResult:
    symptoms: list[str]
    raw_text: str


def extract_symptoms(text: str) -> SymptomExtractionResult:
    normalized_text = text.strip()
    lowered_text = normalized_text.lower()
    symptoms = []

    for phrase, canonical_name in COMMON_SYMPTOMS.items():
        if re.search(rf'\b{re.escape(phrase)}\b', lowered_text):
            symptoms.append(canonical_name)

    return SymptomExtractionResult(symptoms=sorted(set(symptoms)), raw_text=normalized_text)