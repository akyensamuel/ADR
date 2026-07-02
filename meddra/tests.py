import csv
from pathlib import Path
from tempfile import NamedTemporaryFile

from django.core.management import call_command
from django.test import TestCase

from meddra.models import MedDraTerm


class MedDraImportTests(TestCase):
    def _write_tsv(self, rows):
        tmp = NamedTemporaryFile(mode='w', suffix='.tsv', delete=False, newline='', encoding='utf-8')
        writer = csv.writer(tmp, delimiter='\t')
        writer.writerows(rows)
        tmp.close()
        self.addCleanup(lambda: Path(tmp.name).unlink(missing_ok=True))
        return tmp.name

    def test_import_meddra_tsv_creates_terms(self):
        path = self._write_tsv([
            ['C0000727', 'LT', '10000647', 'Acute abdomen'],
            ['C0000727', 'PT', '10000647', 'Acute abdomen'],
        ])

        call_command('import_meddra_tsv', path=path)

        self.assertEqual(2, MedDraTerm.objects.count())
        self.assertTrue(MedDraTerm.objects.filter(term_name='Acute abdomen', term_type='PT').exists())