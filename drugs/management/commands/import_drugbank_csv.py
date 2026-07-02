import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from drugs.importers import import_drugbank_drugs, import_drugbank_interactions


class Command(BaseCommand):
    help = 'Import DrugBank-style CSV data into the database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--kind',
            choices=('drug', 'interaction'),
            required=True,
            help='Type of DrugBank CSV data to import.',
        )
        parser.add_argument(
            '--path',
            required=True,
            help='Path to the CSV file to import.',
        )

    def handle(self, *args, **options):
        kind = options['kind']
        csv_path = Path(options['path'])

        if not csv_path.exists():
            raise CommandError(f'CSV file does not exist: {csv_path}')

        with csv_path.open('r', encoding='utf-8-sig', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            if kind == 'drug':
                created, updated = import_drugbank_drugs(reader)
            else:
                created, updated = import_drugbank_interactions(reader)

        self.stdout.write(self.style.SUCCESS(
            f'Imported DrugBank {kind} data from {csv_path}: {created} created, {updated} updated.'
        ))