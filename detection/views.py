from django.shortcuts import render
from .services.ddi_checker import check_pair
from .services.nlp_extractor import extract_symptoms
from .services.gemini_analyzer import analyze


def interaction_check(request):
    result = None
    source_drug = ''
    target_drug = ''

    if request.method == 'POST':
        source_drug = request.POST.get('source_drug', '').strip()
        target_drug = request.POST.get('target_drug', '').strip()
        if source_drug and target_drug:
            result = check_pair(source_drug, target_drug)

    return render(request, 'detection/interaction_check.html', {
        'result': result,
        'source_drug': source_drug,
        'target_drug': target_drug
    })


def symptom_extraction(request):
    result = None
    clinical_notes = ''

    if request.method == 'POST':
        clinical_notes = request.POST.get('clinical_notes', '').strip()
        if clinical_notes:
            result = extract_symptoms(clinical_notes)

    return render(request, 'detection/symptom_extraction.html', {
        'result': result,
        'clinical_notes': clinical_notes
    })


def unified_analysis(request):
    result = None
    clinical_text = ''

    if request.method == 'POST':
        clinical_text = request.POST.get('clinical_text', '').strip()
        if clinical_text:
            result = analyze(clinical_text)

    return render(request, 'detection/unified_analysis.html', {
        'result': result,
        'clinical_text': clinical_text,
    })
