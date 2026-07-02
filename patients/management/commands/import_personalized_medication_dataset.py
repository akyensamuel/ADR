from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from patients.importers import import_personalized_medication_dataset


class Command(BaseCommand):
    help = 'Import the personalized medication Kaggle dataset into patient records.'

    def add_arguments(self, parser):
        parser.add_argument('--path', required=True, help='Path to personalized_medication_dataset.csv')

    def handle(self, *args, **options):
        csv_path = Path(options['path'])
        if not csv_path.exists():
            raise CommandError(f'CSV file does not exist: {csv_path}')

        import csv

        with csv_path.open('r', encoding='utf-8-sig', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            created, updated = import_personalized_medication_dataset(reader, source_filename=csv_path.name)

        self.stdout.write(self.style.SUCCESS(
            f'Imported personalized medication dataset from {csv_path}: {created} created, {updated} updated.'
        ))