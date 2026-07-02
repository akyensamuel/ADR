from django.test import TestCase

from drugs.models import Drug, DrugInteraction
from recommender.services import recommend_safer_alternatives


class RecommenderServiceTests(TestCase):
	def test_recommendations_exclude_queried_and_interacting_drugs(self):
		queried = Drug.objects.create(name='Drug A')
		interacting = Drug.objects.create(name='Drug B')
		safe_one = Drug.objects.create(name='Drug C')
		safe_two = Drug.objects.create(name='Drug D', is_active=False)
		Drug.objects.create(name='Drug E')

		DrugInteraction.objects.create(source_drug=queried, target_drug=interacting, severity='high')

		recommendations = recommend_safer_alternatives('Drug A', limit=10)

		self.assertEqual(['Drug C', 'Drug E'], recommendations)
		self.assertNotIn('Drug A', recommendations)
		self.assertNotIn('Drug B', recommendations)
		self.assertNotIn('Drug D', recommendations)

	def test_recommendations_return_empty_for_unknown_drug(self):
		self.assertEqual([], recommend_safer_alternatives('Unknown Drug'))
