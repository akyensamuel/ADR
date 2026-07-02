from django.test import TestCase
from django.urls import reverse

from drugs.models import Drug, DrugInteraction


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