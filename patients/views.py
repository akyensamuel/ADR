from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import PatientMedicationRecord


def record_list(request):
    query = request.GET.get('q', '').strip()
    records = PatientMedicationRecord.objects.all().order_by('patient_id')

    if query:
        records = records.filter(
            Q(patient_id__icontains=query)
            | Q(diagnosis__icontains=query)
            | Q(symptoms__icontains=query)
            | Q(recommended_medication__icontains=query)
            | Q(chronic_conditions__icontains=query)
        )

    return render(request, 'patients/record_list.html', {'records': records, 'query': query})


def record_detail(request, patient_id):
    record = get_object_or_404(PatientMedicationRecord, patient_id=patient_id)
    return render(request, 'patients/record_detail.html', {'record': record})