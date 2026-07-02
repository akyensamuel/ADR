from dataclasses import dataclass

from drugs.models import DrugInteraction


@dataclass(frozen=True)
class InteractionCheckResult:
    is_risky: bool
    severity: str = ''
    description: str = ''


def check_pair(source_drug_name: str, target_drug_name: str) -> InteractionCheckResult:
    interaction = (
        DrugInteraction.objects.select_related('source_drug', 'target_drug')
        .filter(
            source_drug__name__iexact=source_drug_name,
            target_drug__name__iexact=target_drug_name,
        )
        .first()
    )

    if interaction is None:
        interaction = (
            DrugInteraction.objects.select_related('source_drug', 'target_drug')
            .filter(
                source_drug__name__iexact=target_drug_name,
                target_drug__name__iexact=source_drug_name,
            )
            .first()
        )

    if interaction is None:
        return InteractionCheckResult(
            is_risky=False,
            description=f'No known interaction found for {source_drug_name} and {target_drug_name}.',
        )

    return InteractionCheckResult(
        is_risky=True,
        severity=interaction.severity,
        description=interaction.description or f'Known interaction recorded for {source_drug_name} and {target_drug_name}.',
    )