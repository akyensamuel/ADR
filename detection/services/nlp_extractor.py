from dataclasses import dataclass


@dataclass(frozen=True)
class SymptomExtractionResult:
    symptoms: list[str]
    raw_text: str


def extract_symptoms(text: str) -> SymptomExtractionResult:
    normalized_text = text.strip()
    return SymptomExtractionResult(symptoms=[], raw_text=normalized_text)