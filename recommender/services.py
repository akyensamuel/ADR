from drugs.models import Drug, DrugInteraction


def recommend_safer_alternatives(drug_name: str, limit: int = 5) -> list[str]:
    try:
        drug = Drug.objects.get(name__iexact=drug_name)
    except Drug.DoesNotExist:
        return []

    interacting_drug_ids = DrugInteraction.objects.filter(
        source_drug=drug,
    ).values_list('target_drug_id', flat=True)
    interacting_drug_ids = interacting_drug_ids.union(
        DrugInteraction.objects.filter(target_drug=drug).values_list('source_drug_id', flat=True)
    )

    safe_alternatives = (
        Drug.objects.filter(is_active=True)
        .exclude(id=drug.id)
        .exclude(id__in=interacting_drug_ids)
        .order_by('name')
        .values_list('name', flat=True)[:limit]
    )

    return list(safe_alternatives)