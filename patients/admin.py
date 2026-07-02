from django.contrib import admin

from .models import PatientMedicationRecord


@admin.register(PatientMedicationRecord)
class PatientMedicationRecordAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'age', 'gender', 'diagnosis', 'recommended_medication', 'treatment_effectiveness')
    search_fields = ('patient_id', 'diagnosis', 'symptoms', 'recommended_medication')
    list_filter = ('gender', 'treatment_effectiveness', 'adverse_reactions')