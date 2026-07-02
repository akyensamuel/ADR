import csv
from io import StringIO
from pathlib import Path
from tempfile import NamedTemporaryFile

from django.core.management import call_command
from django.test import TestCase

from patients.models import PatientMedicationRecord


class PatientMedicationRecordTests(TestCase):
    def test_str_returns_patient_id(self):
        record = PatientMedicationRecord.objects.create(
            patient_id='P0001',
            age=45,
            gender='Female',
            weight_kg='70.0',
            height_cm='170.0',
            bmi='24.2',
            chronic_conditions='None',
            drug_allergies='None',
            genetic_disorders='None',
            diagnosis='Inflammation',
            symptoms='Fever',
            recommended_medication='Amlodipine',
            dosage='5 mg',
            duration='7 days',
            treatment_effectiveness='Effective',
            adverse_reactions='Yes',
            recovery_time_days=10,
        )

        self.assertEqual('P0001', str(record))


class PersonalizedMedicationDatasetImportTests(TestCase):
    def _write_csv(self, fieldnames, rows):
        tmp = NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='', encoding='utf-8')
        writer = csv.DictWriter(tmp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        tmp.close()
        self.addCleanup(lambda: Path(tmp.name).unlink(missing_ok=True))
        return tmp.name

    def test_import_creates_patient_records_and_placeholder_drugs(self):
        path = self._write_csv(
            [
                'Patient_ID', 'Age', 'Gender', 'Weight_kg', 'Height_cm', 'BMI',
                'Chronic_Conditions', 'Drug_Allergies', 'Genetic_Disorders', 'Diagnosis',
                'Symptoms', 'Recommended_Medication', 'Dosage', 'Duration',
                'Treatment_Effectiveness', 'Adverse_Reactions', 'Recovery_Time_Days',
            ],
            [
                {
                    'Patient_ID': 'P0001',
                    'Age': '78',
                    'Gender': 'Other',
                    'Weight_kg': '88.7',
                    'Height_cm': '196.3',
                    'BMI': '21.1',
                    'Chronic_Conditions': 'None',
                    'Drug_Allergies': 'Penicillin',
                    'Genetic_Disorders': 'Cystic Fibrosis',
                    'Diagnosis': 'Inflammation',
                    'Symptoms': 'Fever',
                    'Recommended_Medication': 'Amlodipine',
                    'Dosage': 'None',
                    'Duration': '30 days',
                    'Treatment_Effectiveness': 'Effective',
                    'Adverse_Reactions': 'Yes',
                    'Recovery_Time_Days': '18',
                }
            ],
        )

        out = StringIO()
        call_command('import_personalized_medication_dataset', path=path, stdout=out)

        record = PatientMedicationRecord.objects.get(patient_id='P0001')
        self.assertEqual(1, PatientMedicationRecord.objects.count())
        self.assertEqual('Inflammation', record.diagnosis)
        self.assertEqual('Amlodipine', record.recommended_medication)
        self.assertIn('1 created, 0 updated', out.getvalue())

        self.assertTrue(record.source_filename.endswith('csv'))


class PatientRecordsViewTests(TestCase):
    def test_patient_list_and_detail_render(self):
        record = PatientMedicationRecord.objects.create(
            patient_id='P0002',
            age=57,
            gender='Female',
            weight_kg='90.5',
            height_cm='195.6',
            bmi='30.2',
            chronic_conditions='Hypertension',
            drug_allergies='None',
            genetic_disorders='None',
            diagnosis='Depression',
            symptoms='Fatigue, Headache, Dizziness',
            recommended_medication='Amoxicillin',
            dosage='5 mg',
            duration='None',
            treatment_effectiveness='Neutral',
            adverse_reactions='No',
            recovery_time_days=24,
        )

        response = self.client.get('/patients/')
        self.assertEqual(200, response.status_code)
        self.assertContains(response, record.patient_id)

        detail = self.client.get(f'/patients/{record.patient_id}/')
        self.assertEqual(200, detail.status_code)
        self.assertContains(detail, record.diagnosis)
