from django.db import models


class MedDraTerm(models.Model):
    meddra_concept_code = models.CharField(max_length=16)
    term_type = models.CharField(max_length=8)
    meddra_id = models.CharField(max_length=16)
    term_name = models.CharField(max_length=255)
    normalized_name = models.CharField(max_length=255, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['meddra_concept_code', 'term_type', 'meddra_id', 'term_name'],
                name='unique_meddra_term_row',
            )
        ]
        indexes = [
            models.Index(fields=['normalized_name']),
            models.Index(fields=['term_type']),
        ]

    def save(self, *args, **kwargs):
        self.normalized_name = _normalize(self.term_name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.term_name} ({self.term_type})'


def _normalize(value: str) -> str:
    return ' '.join(value.strip().lower().split())