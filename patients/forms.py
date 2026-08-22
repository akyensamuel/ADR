from django import forms
from .models import PatientMedicationRecord

class PatientMedicationRecordForm(forms.ModelForm):
    class Meta:
        model = PatientMedicationRecord
        fields = '__all__'
        exclude = ['source_filename']
        widgets = {
            'chronic_conditions': forms.Textarea(attrs={'rows': 3}),
            'drug_allergies': forms.Textarea(attrs={'rows': 3}),
            'genetic_disorders': forms.Textarea(attrs={'rows': 3}),
            'symptoms': forms.Textarea(attrs={'rows': 4}),
        }
