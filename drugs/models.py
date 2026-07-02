from django.db import models


class Drug(models.Model):
	name = models.CharField(max_length=255, unique=True)
	rxnorm_code = models.CharField(max_length=64, blank=True)
	atc_code = models.CharField(max_length=32, blank=True)
	manufacturer = models.CharField(max_length=255, blank=True)
	description = models.TextField(blank=True)
	is_active = models.BooleanField(default=True)

	def __str__(self) -> str:
		return self.name


class AdverseReaction(models.Model):
	drug = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name='adverse_reactions')
	name = models.CharField(max_length=255)
	meddra_code = models.CharField(max_length=64, blank=True)
	severity = models.CharField(max_length=32, blank=True)
	description = models.TextField(blank=True)

	class Meta:
		unique_together = ('drug', 'name')

	def __str__(self) -> str:
		return f'{self.drug} - {self.name}'


class DrugInteraction(models.Model):
	source_drug = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name='interactions_as_source')
	target_drug = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name='interactions_as_target')
	severity = models.CharField(max_length=32, blank=True)
	description = models.TextField(blank=True)
	evidence_source = models.CharField(max_length=255, blank=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['source_drug', 'target_drug'],
				name='unique_drug_interaction_pair',
			)
		]

	def __str__(self) -> str:
		return f'{self.source_drug} ↔ {self.target_drug}'
