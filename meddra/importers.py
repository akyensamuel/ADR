from __future__ import annotations

from collections.abc import Iterable

from django.core.management.base import CommandError

from detection.services import nlp_extractor
from .models import MedDraTerm


def import_meddra_terms(rows: Iterable[list[str]]) -> tuple[int, int]:
    created = 0
    updated = 0

    for row in rows:
        if len(row) < 4:
            raise CommandError('MedDRA TSV rows must contain at least 4 columns.')

        concept_code, term_type, meddra_id, term_name = [value.strip() for value in row[:4]]
        if not all([concept_code, term_type, meddra_id, term_name]):
            raise CommandError('MedDRA TSV contains an empty required field.')

        _, was_created = MedDraTerm.objects.update_or_create(
            meddra_concept_code=concept_code,
            term_type=term_type,
            meddra_id=meddra_id,
            term_name=term_name,
            defaults={},
        )
        created += int(was_created)
        updated += int(not was_created)

    nlp_extractor.clear_meddra_term_cache()
    return created, updated