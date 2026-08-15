from __future__ import annotations

from collections.abc import Iterable

from django.core.management.base import CommandError

from detection.services import nlp_extractor
from .models import MedDraTerm, _normalize


def import_meddra_terms(rows: Iterable[list[str]], clean: bool = False) -> tuple[int, int]:
    if clean:
        MedDraTerm.objects.all().delete()
        
    created = 0
    updated = 0
    batch_size = 5000
    batch = []

    for row in rows:
        if len(row) < 4:
            raise CommandError('MedDRA TSV rows must contain at least 4 columns.')

        concept_code, term_type, meddra_id, term_name = [value.strip() for value in row[:4]]
        if not all([concept_code, term_type, meddra_id, term_name]):
            raise CommandError('MedDRA TSV contains an empty required field.')

        term = MedDraTerm(
            meddra_concept_code=concept_code,
            term_type=term_type,
            meddra_id=meddra_id,
            term_name=term_name,
            normalized_name=_normalize(term_name),
        )
        batch.append(term)
        
        if len(batch) >= batch_size:
            MedDraTerm.objects.bulk_create(batch, ignore_conflicts=True)
            created += len(batch)
            batch.clear()

    if batch:
        MedDraTerm.objects.bulk_create(batch, ignore_conflicts=True)
        created += len(batch)

    nlp_extractor.clear_meddra_term_cache()
    return created, updated