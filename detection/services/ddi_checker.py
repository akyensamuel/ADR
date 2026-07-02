from dataclasses import dataclass


@dataclass(frozen=True)
class InteractionCheckResult:
    is_risky: bool
    severity: str = ''
    description: str = ''


def check_pair(source_drug_name: str, target_drug_name: str) -> InteractionCheckResult:
    return InteractionCheckResult(
        is_risky=False,
        description=f'Interaction checking is not implemented yet for {source_drug_name} and {target_drug_name}.',
    )