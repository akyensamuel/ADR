import csv
import io
from tempfile import NamedTemporaryFile

from django.contrib import messages
from django.shortcuts import redirect, render

from adr_system.forms import DatasetImportForm, InteractionCheckForm, RecommendationForm
from detection.services.ddi_checker import check_pair
from drugs.importers import import_drugbank_drugs, import_drugbank_interactions, import_sider_reactions
from drugs.models import Drug
from meddra.models import MedDraTerm
from meddra.importers import import_meddra_terms
from patients.models import PatientMedicationRecord
from patients.importers import import_personalized_medication_dataset
from recommender.services import recommend_safer_alternatives


def home(request):
    interaction_result = None
    recommendations = None

    interaction_query_present = any(key.startswith('interaction-') for key in request.GET)
    recommendation_query_present = any(key.startswith('recommendation-') for key in request.GET)

    interaction_form = InteractionCheckForm(request.GET if interaction_query_present else None, prefix='interaction')
    recommendation_form = RecommendationForm(request.GET if recommendation_query_present else None, prefix='recommendation')

    if interaction_form.is_valid():
        interaction_result = check_pair(
            interaction_form.cleaned_data['source_drug_name'],
            interaction_form.cleaned_data['target_drug_name'],
        )

    if recommendation_form.is_valid():
        recommendations = recommend_safer_alternatives(recommendation_form.cleaned_data['drug_name'])

    context = {
        'interaction_form': interaction_form,
        'recommendation_form': recommendation_form,
        'interaction_result': interaction_result,
        'recommendations': recommendations,
        'active_drugs': Drug.objects.filter(is_active=True).order_by('name'),
        'patient_record_count': PatientMedicationRecord.objects.count(),
        'meddra_term_count': MedDraTerm.objects.count(),
    }
    return render(request, 'adr_system/home.html', context)


def import_data(request):
    if request.method == 'POST':
        form = DatasetImportForm(request.POST, request.FILES)
        if form.is_valid():
            dataset_type = form.cleaned_data['dataset_type']
            data_file = form.cleaned_data['data_file']
            created, updated = _import_uploaded_dataset(dataset_type, data_file)
            messages.success(request, f'Imported {dataset_type}: {created} created, {updated} updated.')
            return redirect('import-data')
    else:
        form = DatasetImportForm()

    return render(
        request,
        'adr_system/import_data.html',
        {
            'form': form,
            'recent_counts': {
                'drugs': Drug.objects.count(),
                'patients': PatientMedicationRecord.objects.count(),
                'meddra_terms': MedDraTerm.objects.count(),
            },
        },
    )


def _import_uploaded_dataset(dataset_type, uploaded_file):
    if dataset_type == 'meddra-terms':
        stream = io.TextIOWrapper(uploaded_file.file, encoding='utf-8-sig', newline='')
        reader = csv.reader(stream, delimiter='\t')
        return import_meddra_terms(reader)

    stream = io.TextIOWrapper(uploaded_file.file, encoding='utf-8-sig', newline='')

    if dataset_type == 'patient-medication':
        reader = csv.DictReader(stream)
        return import_personalized_medication_dataset(reader, source_filename=uploaded_file.name)

    reader = csv.DictReader(stream)

    if dataset_type == 'drugbank-drugs':
        return import_drugbank_drugs(reader)
    if dataset_type == 'drugbank-interactions':
        return import_drugbank_interactions(reader)
    if dataset_type == 'sider-reactions':
        return import_sider_reactions(reader)

    raise ValueError(f'Unsupported dataset type: {dataset_type}')