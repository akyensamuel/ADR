from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages

from .models import PatientMedicationRecord
from .forms import PatientMedicationRecordForm


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


def record_create(request):
    if request.method == 'POST':
        form = PatientMedicationRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.source_filename = "Manual Entry"
            record.save()
            messages.success(request, f"Patient record {record.patient_id} created successfully.")
            return redirect('patient-record-detail', patient_id=record.patient_id)
    else:
        form = PatientMedicationRecordForm()
        
    return render(request, 'patients/record_form.html', {'form': form})


def record_detail(request, patient_id):
    record = get_object_or_404(PatientMedicationRecord, patient_id=patient_id)
    return render(request, 'patients/record_detail.html', {'record': record})