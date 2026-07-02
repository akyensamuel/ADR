import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from drugs.importers import import_sider_reactions


class Command(BaseCommand):
    help = 'Import SIDER-style adverse reaction CSV data into the database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            required=True,
            help='Path to the SIDER CSV file to import.',
        )

    def handle(self, *args, **options):
        csv_path = Path(options['path'])

        if not csv_path.exists():
            raise CommandError(f'CSV file does not exist: {csv_path}')

        with csv_path.open('r', encoding='utf-8-sig', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            created, updated = import_sider_reactions(reader)

        self.stdout.write(self.style.SUCCESS(
            f'Imported SIDER reaction data from {csv_path}: {created} created, {updated} updated.'
        ))