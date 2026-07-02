import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from meddra.importers import import_meddra_terms


class Command(BaseCommand):
    help = 'Import MedDRA terminology TSV data into the database.'

    def add_arguments(self, parser):
        parser.add_argument('--path', required=True, help='Path to meddra.tsv')

    def handle(self, *args, **options):
        tsv_path = Path(options['path'])
        if not tsv_path.exists():
            raise CommandError(f'TSV file does not exist: {tsv_path}')

        with tsv_path.open('r', encoding='utf-8-sig', newline='') as tsv_file:
            reader = csv.reader(tsv_file, delimiter='\t')
            created, updated = import_meddra_terms(reader)

        self.stdout.write(self.style.SUCCESS(
            f'Imported MedDRA data from {tsv_path}: {created} created, {updated} updated.'
        ))