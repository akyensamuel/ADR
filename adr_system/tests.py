from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from drugs.models import Drug, DrugInteraction
from meddra.models import MedDraTerm
from patients.models import PatientMedicationRecord


class ImportViewTests(TestCase):
    def test_import_page_renders(self):
        response = self.client.get(reverse('import-data'))

        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Import Data')

    def test_import_patient_dataset_from_browser(self):
        csv_content = (
            'Patient_ID,Age,Gender,Weight_kg,Height_cm,BMI,Chronic_Conditions,Drug_Allergies,Genetic_Disorders,Diagnosis,Symptoms,Recommended_Medication,Dosage,Duration,Treatment_Effectiveness,Adverse_Reactions,Recovery_Time_Days\n'
            'P1000,45,Female,70.0,170.0,24.2,None,None,None,Inflammation,Fever,Amlodipine,5 mg,7 days,Effective,No,10\n'
        )
        upload = SimpleUploadedFile(
            'personalized_medication_dataset.csv',
            csv_content.encode('utf-8'),
            content_type='text/csv',
        )

        response = self.client.post(
            reverse('import-data'),
            {'dataset_type': 'patient-medication', 'data_file': upload},
            follow=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertTrue(PatientMedicationRecord.objects.filter(patient_id='P1000').exists())
        self.assertTrue(Drug.objects.filter(name='Amlodipine').exists())

    def test_import_meddra_dataset_from_browser(self):
        tsv_content = 'C0000727\tPT\t10000647\tAcute abdomen\nC0000729\tLT\t10000057\tAbdominal cramps\n'
        upload = SimpleUploadedFile(
            'meddra.tsv',
            tsv_content.encode('utf-8'),
            content_type='text/tab-separated-values',
        )

        response = self.client.post(
            reverse('import-data'),
            {'dataset_type': 'meddra-terms', 'data_file': upload},
            follow=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertTrue(MedDraTerm.objects.filter(term_name='Acute abdomen').exists())


class HomeViewTests(TestCase):
    def test_home_page_renders(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Adverse Drug Reaction Detection')

    def test_home_page_shows_interaction_result(self):
        Drug.objects.create(name='Drug A')
        Drug.objects.create(name='Drug B')
        DrugInteraction.objects.create(
            source_drug=Drug.objects.get(name='Drug A'),
            target_drug=Drug.objects.get(name='Drug B'),
            severity='high',
            description='Avoid together',
        )

        response = self.client.get(
            reverse('home'),
            {
                'interaction-source_drug_name': 'Drug A',
                'interaction-target_drug_name': 'Drug B',
            },
        )

        self.assertContains(response, 'Known interaction detected')
        self.assertContains(response, 'Avoid together')
