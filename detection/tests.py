from django.test import TestCase

from detection.services.ddi_checker import check_pair
from detection.services.nlp_extractor import extract_symptoms
from meddra.models import MedDraTerm
from drugs.models import Drug, DrugInteraction


class DetectionServiceTests(TestCase):
	def test_check_pair_returns_risky_for_known_interaction(self):
		source = Drug.objects.create(name='Drug A')
		target = Drug.objects.create(name='Drug B')
		DrugInteraction.objects.create(
			source_drug=source,
			target_drug=target,
			severity='high',
			description='Do not combine',
		)

		result = check_pair('Drug A', 'Drug B')

		self.assertTrue(result.is_risky)
		self.assertEqual('high', result.severity)
		self.assertEqual('Do not combine', result.description)

	def test_check_pair_matches_reverse_order(self):
		source = Drug.objects.create(name='Drug A')
		target = Drug.objects.create(name='Drug B')
		DrugInteraction.objects.create(
			source_drug=source,
			target_drug=target,
			severity='moderate',
			description='Use caution',
		)

		result = check_pair('Drug B', 'Drug A')

		self.assertTrue(result.is_risky)
		self.assertEqual('moderate', result.severity)

	def test_check_pair_returns_safe_when_missing(self):
		result = check_pair('Drug A', 'Drug B')

		self.assertFalse(result.is_risky)
		self.assertIn('No known interaction found', result.description)

	def test_extract_symptoms_detects_common_terms(self):
		MedDraTerm.objects.create(
			meddra_concept_code='C0004057',
			term_type='PT',
			meddra_id='10028813',
			term_name='Nausea',
			normalized_name='nausea',
		)
		MedDraTerm.objects.create(
			meddra_concept_code='C0012833',
			term_type='LT',
			meddra_id='10013755',
			term_name='Chest pain',
			normalized_name='chest pain',
		)
		MedDraTerm.objects.create(
			meddra_concept_code='C0012833',
			term_type='PT',
			meddra_id='10013573',
			term_name='Dizziness',
			normalized_name='dizziness',
		)

		result = extract_symptoms('Patient reports nausea, dizziness, and chest pain after the medication.')

		self.assertEqual(['Chest pain', 'Dizziness', 'Nausea'], result.symptoms)
		self.assertEqual('Patient reports nausea, dizziness, and chest pain after the medication.', result.raw_text)
