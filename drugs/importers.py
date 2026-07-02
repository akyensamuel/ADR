from __future__ import annotations

from collections.abc import Iterable

from django.core.management.base import CommandError

from drugs.models import AdverseReaction, Drug, DrugInteraction


class ImportMappingError(CommandError):
    pass


def import_drugbank_drugs(rows: Iterable[dict[str, str]]) -> tuple[int, int]:
    created = 0
    updated = 0

    for row in rows:
        name = _required(row, 'name', 'drug_name', 'generic_name', 'product_name')
        defaults = {
            'rxnorm_code': _value(row, 'rxnorm_code', 'rxnorm', 'rxnorm_id'),
            'atc_code': _value(row, 'atc_code', 'atc', 'atc_class'),
            'manufacturer': _value(row, 'manufacturer', 'maker', 'company', 'supplier'),
            'description': _value(row, 'description', 'notes', 'summary', 'indication'),
            'is_active': _boolean(_value(row, 'is_active', 'active', 'status', default='true')),
        }
        _, was_created = Drug.objects.update_or_create(name=name, defaults=defaults)
        created += int(was_created)
        updated += int(not was_created)

    return created, updated


def import_sider_reactions(rows: Iterable[dict[str, str]]) -> tuple[int, int]:
    created = 0
    updated = 0

    for row in rows:
        drug = _resolve_drug(_required(row, 'drug_name', 'drug', 'drug_generic_name', 'compound'))
        reaction_name = _required(
            row,
            'name',
            'side_effect_name',
            'adverse_reaction',
            'reaction',
            'effect',
            'side_effect',
        )
        defaults = {
            'meddra_code': _value(row, 'meddra_code', 'meddra_id', 'meddra'),
            'severity': _value(row, 'severity', 'frequency', 'seriousness'),
            'description': _value(row, 'description', 'notes', 'comment', 'source'),
        }
        _, was_created = AdverseReaction.objects.update_or_create(
            drug=drug,
            name=reaction_name,
            defaults=defaults,
        )
        created += int(was_created)
        updated += int(not was_created)

    return created, updated


def import_drugbank_interactions(rows: Iterable[dict[str, str]]) -> tuple[int, int]:
    created = 0
    updated = 0

    for row in rows:
        source_drug = _resolve_drug(_required(row, 'source_drug_name', 'drug_a', 'drug_1', 'drug_name_1'))
        target_drug = _resolve_drug(_required(row, 'target_drug_name', 'drug_b', 'drug_2', 'drug_name_2'))
        defaults = {
            'severity': _value(row, 'severity', 'interaction_severity', 'risk'),
            'description': _value(row, 'description', 'interaction', 'notes', 'effect'),
            'evidence_source': _value(row, 'evidence_source', 'source', 'reference', 'citation'),
        }
        _, was_created = DrugInteraction.objects.update_or_create(
            source_drug=source_drug,
            target_drug=target_drug,
            defaults=defaults,
        )
        created += int(was_created)
        updated += int(not was_created)

    return created, updated


def _resolve_drug(drug_name: str) -> Drug:
    try:
        return Drug.objects.get(name__iexact=drug_name)
    except Drug.DoesNotExist as exc:
        raise ImportMappingError(f'Drug not found: {drug_name}') from exc


def _required(row: dict[str, str], *keys: str) -> str:
    value = _value(row, *keys)
    if not value:
        raise ImportMappingError(f'Missing required CSV column or value: {", ".join(keys)}')
    return value


def _value(row: dict[str, str], *keys: str, default: str = '') -> str:
    for key in keys:
        value = row.get(key, '')
        if isinstance(value, str):
            value = value.strip()
        if value:
            return value
    return default


def _boolean(value: str) -> bool:
    normalized = str(value).strip().lower()
    return normalized in {'1', 'true', 'yes', 'y', 'active', 'approved'}