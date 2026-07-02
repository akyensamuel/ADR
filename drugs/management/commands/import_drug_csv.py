import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from drugs.models import AdverseReaction, Drug, DrugInteraction


class Command(BaseCommand):
    help = 'Import drug-related CSV data into the database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--kind',
            choices=('drug', 'reaction', 'interaction'),
            required=True,
            help='Type of CSV data to import.',
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
                created, updated = self._import_drugs(reader)
            elif kind == 'reaction':
                created, updated = self._import_reactions(reader)
            else:
                created, updated = self._import_interactions(reader)

        self.stdout.write(self.style.SUCCESS(
            f'Imported {kind} data from {csv_path}: {created} created, {updated} updated.'
        ))

    def _import_drugs(self, reader):
        created = 0
        updated = 0

        for row in reader:
            name = self._required_value(row, 'name')
            defaults = {
                'rxnorm_code': self._value(row, 'rxnorm_code'),
                'atc_code': self._value(row, 'atc_code'),
                'manufacturer': self._value(row, 'manufacturer'),
                'description': self._value(row, 'description'),
                'is_active': self._boolean_value(row.get('is_active', 'true')),
            }
            _, was_created = Drug.objects.update_or_create(name=name, defaults=defaults)
            created += int(was_created)
            updated += int(not was_created)

        return created, updated

    def _import_reactions(self, reader):
        created = 0
        updated = 0

        for row in reader:
            drug = self._resolve_drug(self._required_value(row, 'drug_name'))
            reaction_name = self._required_value(row, 'name')
            defaults = {
                'meddra_code': self._value(row, 'meddra_code'),
                'severity': self._value(row, 'severity'),
                'description': self._value(row, 'description'),
            }
            _, was_created = AdverseReaction.objects.update_or_create(
                drug=drug,
                name=reaction_name,
                defaults=defaults,
            )
            created += int(was_created)
            updated += int(not was_created)

        return created, updated

    def _import_interactions(self, reader):
        created = 0
        updated = 0

        for row in reader:
            source_drug = self._resolve_drug(self._required_value(row, 'source_drug_name'))
            target_drug = self._resolve_drug(self._required_value(row, 'target_drug_name'))
            defaults = {
                'severity': self._value(row, 'severity'),
                'description': self._value(row, 'description'),
                'evidence_source': self._value(row, 'evidence_source'),
            }
            _, was_created = DrugInteraction.objects.update_or_create(
                source_drug=source_drug,
                target_drug=target_drug,
                defaults=defaults,
            )
            created += int(was_created)
            updated += int(not was_created)

        return created, updated

    def _resolve_drug(self, drug_name):
        try:
            return Drug.objects.get(name=drug_name)
        except Drug.DoesNotExist as exc:
            raise CommandError(f'Drug not found: {drug_name}') from exc

    def _required_value(self, row, key):
        value = self._value(row, key)
        if not value:
            raise CommandError(f'Missing required CSV column or value: {key}')
        return value

    def _value(self, row, key):
        value = row.get(key, '')
        return value.strip() if isinstance(value, str) else value

    def _boolean_value(self, value):
        normalized = str(value).strip().lower()
        return normalized in {'1', 'true', 'yes', 'y'}