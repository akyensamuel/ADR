from __future__ import annotations

from collections.abc import Iterable

from django.core.management.base import CommandError

from drugs.models import Drug
from patients.models import PatientMedicationRecord


def import_personalized_medication_dataset(rows: Iterable[dict[str, str]], source_filename: str = '') -> tuple[int, int]:
    created = 0
    updated = 0

    for row in rows:
        defaults = {
            'age': _positive_int(row, 'Age'),
            'gender': _required(row, 'Gender'),
            'weight_kg': _decimal_string(row, 'Weight_kg'),
            'height_cm': _decimal_string(row, 'Height_cm'),
            'bmi': _decimal_string(row, 'BMI'),
            'chronic_conditions': _optional(row, 'Chronic_Conditions'),
            'drug_allergies': _optional(row, 'Drug_Allergies'),
            'genetic_disorders': _optional(row, 'Genetic_Disorders'),
            'diagnosis': _required(row, 'Diagnosis'),
            'symptoms': _optional(row, 'Symptoms'),
            'recommended_medication': _optional(row, 'Recommended_Medication'),
            'dosage': _optional(row, 'Dosage'),
            'duration': _optional(row, 'Duration'),
            'treatment_effectiveness': _optional(row, 'Treatment_Effectiveness'),
            'adverse_reactions': _optional(row, 'Adverse_Reactions'),
            'recovery_time_days': _optional_positive_int(row, 'Recovery_Time_Days'),
            'source_filename': source_filename,
        }
        record, was_created = PatientMedicationRecord.objects.update_or_create(
            patient_id=_required(row, 'Patient_ID'),
            defaults=defaults,
        )
        _link_recommended_medication(record.recommended_medication)
        created += int(was_created)
        updated += int(not was_created)

    return created, updated


def _link_recommended_medication(drug_name: str) -> None:
    if not drug_name:
        return
    Drug.objects.update_or_create(name=drug_name, defaults={'is_active': True})


def _required(row: dict[str, str], key: str) -> str:
    value = _optional(row, key)
    if not value:
        raise CommandError(f'Missing required CSV column or value: {key}')
    return value


def _optional(row: dict[str, str], key: str) -> str:
    value = row.get(key, '')
    if value is None:
        return ''
    return value.strip() if isinstance(value, str) else str(value)


def _positive_int(row: dict[str, str], key: str) -> int:
    value = _required(row, key)
    try:
        return int(value)
    except ValueError as exc:
        raise CommandError(f'Invalid integer for {key}: {value}') from exc


def _optional_positive_int(row: dict[str, str], key: str):
    value = _optional(row, key)
    if not value:
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise CommandError(f'Invalid integer for {key}: {value}') from exc


def _decimal_string(row: dict[str, str], key: str) -> str:
    value = _required(row, key)
    try:
        return f'{float(value):.1f}'
    except ValueError as exc:
        raise CommandError(f'Invalid decimal for {key}: {value}') from exc