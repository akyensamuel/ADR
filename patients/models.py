from django.db import models


class PatientMedicationRecord(models.Model):
    patient_id = models.CharField(max_length=32, unique=True)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=16)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=1)
    height_cm = models.DecimalField(max_digits=5, decimal_places=1)
    bmi = models.DecimalField(max_digits=4, decimal_places=1)
    chronic_conditions = models.TextField(blank=True)
    drug_allergies = models.TextField(blank=True)
    genetic_disorders = models.TextField(blank=True)
    diagnosis = models.CharField(max_length=255)
    symptoms = models.TextField(blank=True)
    recommended_medication = models.CharField(max_length=255, blank=True)
    dosage = models.CharField(max_length=64, blank=True)
    duration = models.CharField(max_length=64, blank=True)
    treatment_effectiveness = models.CharField(max_length=64, blank=True)
    adverse_reactions = models.CharField(max_length=16, blank=True)
    recovery_time_days = models.PositiveIntegerField(null=True, blank=True)
    source_filename = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return self.patient_id