from django.contrib import admin

from .models import MedDraTerm


@admin.register(MedDraTerm)
class MedDraTermAdmin(admin.ModelAdmin):
    list_display = ('meddra_concept_code', 'term_type', 'meddra_id', 'term_name')
    search_fields = ('meddra_concept_code', 'meddra_id', 'term_name')
    list_filter = ('term_type',)