from django.contrib import admin

from .models import AdverseReaction, Drug, DrugInteraction


@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
	list_display = ('name', 'rxnorm_code', 'atc_code', 'is_active')
	search_fields = ('name', 'rxnorm_code', 'atc_code')


@admin.register(AdverseReaction)
class AdverseReactionAdmin(admin.ModelAdmin):
	list_display = ('drug', 'name', 'severity', 'meddra_code')
	search_fields = ('drug__name', 'name', 'meddra_code')


@admin.register(DrugInteraction)
class DrugInteractionAdmin(admin.ModelAdmin):
	list_display = ('source_drug', 'target_drug', 'severity', 'evidence_source')
	search_fields = ('source_drug__name', 'target_drug__name', 'evidence_source')
