import csv
from io import StringIO
from pathlib import Path
from tempfile import NamedTemporaryFile

from django.core.management import call_command
from django.test import TestCase

from drugs.models import AdverseReaction, Drug, DrugInteraction


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
