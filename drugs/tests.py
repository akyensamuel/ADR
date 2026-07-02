import csv
from io import StringIO
from pathlib import Path
from tempfile import NamedTemporaryFile

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from drugs.models import AdverseReaction, Drug, DrugInteraction


class DrugCatalogViewTests(TestCase):
	def test_drug_list_shows_active_drugs(self):
		active = Drug.objects.create(name='Aspirin', description='Pain relief')
		Drug.objects.create(name='Inactive', is_active=False)

		response = self.client.get(reverse('drug-list'))

		self.assertEqual(200, response.status_code)
		self.assertContains(response, active.name)
		self.assertNotContains(response, 'Inactive')

	def test_drug_detail_shows_related_data(self):
		source = Drug.objects.create(name='Drug A', description='Source')
		target = Drug.objects.create(name='Drug B', description='Target')
		AdverseReaction.objects.create(drug=source, name='Nausea', severity='mild')
		DrugInteraction.objects.create(
			source_drug=source,
			target_drug=target,
			severity='high',
			description='Avoid together',
		)

		response = self.client.get(reverse('drug-detail', args=[source.pk]))

		self.assertEqual(200, response.status_code)
		self.assertContains(response, 'Nausea')
		self.assertContains(response, 'Avoid together')
		self.assertContains(response, target.name)


class ImportDrugCsvCommandTests(TestCase):
	def _write_csv(self, fieldnames, rows):
		tmp = NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='', encoding='utf-8')
		writer = csv.DictWriter(tmp, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(rows)
		tmp.close()
		self.addCleanup(lambda: Path(tmp.name).unlink(missing_ok=True))
		return tmp.name

	def test_import_drugs_creates_and_updates_records(self):
		path = self._write_csv(
			['name', 'rxnorm_code', 'atc_code', 'manufacturer', 'description', 'is_active'],
			[
				{
					'name': 'Aspirin',
					'rxnorm_code': '1191',
					'atc_code': 'B01AC06',
					'manufacturer': 'Acme',
					'description': 'Pain relief',
					'is_active': 'true',
				}
			],
		)

		out = StringIO()
		call_command('import_drug_csv', kind='drug', path=path, stdout=out)

		aspirin = Drug.objects.get(name='Aspirin')
		self.assertEqual(1, Drug.objects.count())
		self.assertEqual('1191', aspirin.rxnorm_code)
		self.assertTrue(aspirin.is_active)
		self.assertIn('1 created, 0 updated', out.getvalue())

		path = self._write_csv(
			['name', 'rxnorm_code', 'atc_code', 'manufacturer', 'description', 'is_active'],
			[
				{
					'name': 'Aspirin',
					'rxnorm_code': 'UPDATED',
					'atc_code': 'B01AC06',
					'manufacturer': 'Acme',
					'description': 'Updated description',
					'is_active': 'false',
				}
			],
		)

		call_command('import_drug_csv', kind='drug', path=path, stdout=StringIO())

		aspirin.refresh_from_db()
		self.assertEqual('UPDATED', aspirin.rxnorm_code)
		self.assertFalse(aspirin.is_active)

	def test_import_reactions_links_to_existing_drug(self):
		Drug.objects.create(name='Metformin')
		path = self._write_csv(
			['drug_name', 'name', 'meddra_code', 'severity', 'description'],
			[
				{
					'drug_name': 'Metformin',
					'name': 'Nausea',
					'meddra_code': '10028813',
					'severity': 'mild',
					'description': 'Common side effect',
				}
			],
		)

		call_command('import_drug_csv', kind='reaction', path=path, stdout=StringIO())

		reaction = AdverseReaction.objects.get(drug__name='Metformin', name='Nausea')
		self.assertEqual('10028813', reaction.meddra_code)
		self.assertEqual('mild', reaction.severity)

	def test_import_interactions_links_existing_drugs(self):
		Drug.objects.create(name='Drug A')
		Drug.objects.create(name='Drug B')
		path = self._write_csv(
			['source_drug_name', 'target_drug_name', 'severity', 'description', 'evidence_source'],
			[
				{
					'source_drug_name': 'Drug A',
					'target_drug_name': 'Drug B',
					'severity': 'high',
					'description': 'Avoid together',
					'evidence_source': 'test',
				}
			],
		)

		call_command('import_drug_csv', kind='interaction', path=path, stdout=StringIO())

		interaction = DrugInteraction.objects.get(source_drug__name='Drug A', target_drug__name='Drug B')
		self.assertEqual('high', interaction.severity)
		self.assertEqual('test', interaction.evidence_source)

	def test_import_drugbank_csv_supports_alias_columns(self):
		path = self._write_csv(
			['drug_name', 'rxnorm', 'atc', 'maker', 'summary', 'status'],
			[
				{
					'drug_name': 'Lisinopril',
					'rxnorm': '29046',
					'atc': 'C09AA03',
					'maker': 'Demo Pharma',
					'summary': 'ACE inhibitor',
					'status': 'approved',
				}
			],
		)

		call_command('import_drugbank_csv', kind='drug', path=path, stdout=StringIO())

		lisinopril = Drug.objects.get(name='Lisinopril')
		self.assertEqual('29046', lisinopril.rxnorm_code)
		self.assertEqual('C09AA03', lisinopril.atc_code)
		self.assertEqual('Demo Pharma', lisinopril.manufacturer)
		self.assertEqual('ACE inhibitor', lisinopril.description)
		self.assertTrue(lisinopril.is_active)

	def test_import_sider_csv_supports_side_effect_aliases(self):
		Drug.objects.create(name='Metformin')
		path = self._write_csv(
			['drug', 'side_effect_name', 'meddra_id', 'frequency', 'notes'],
			[
				{
					'drug': 'Metformin',
					'side_effect_name': 'Diarrhea',
					'meddra_id': '10012757',
					'frequency': 'common',
					'notes': 'Expected gastrointestinal effect',
				}
			],
		)

		call_command('import_sider_csv', path=path, stdout=StringIO())

		reaction = AdverseReaction.objects.get(drug__name='Metformin', name='Diarrhea')
		self.assertEqual('10012757', reaction.meddra_code)
		self.assertEqual('common', reaction.severity)
		self.assertEqual('Expected gastrointestinal effect', reaction.description)
