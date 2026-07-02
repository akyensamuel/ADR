from django.test import TestCase

from detection.services.ddi_checker import check_pair
from detection.services.nlp_extractor import extract_symptoms
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
		result = extract_symptoms('Patient reports nausea, dizziness, and chest pain after the medication.')

		self.assertEqual(['chest pain', 'dizziness', 'nausea'], result.symptoms)
		self.assertEqual('Patient reports nausea, dizziness, and chest pain after the medication.', result.raw_text)
