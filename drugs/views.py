from django.shortcuts import get_object_or_404, render

from .models import Drug


def drug_list(request):
	drugs = (
		Drug.objects.filter(is_active=True)
		.prefetch_related('adverse_reactions', 'interactions_as_source', 'interactions_as_target')
		.order_by('name')
	)
	return render(request, 'drugs/drug_list.html', {'drugs': drugs})


def drug_detail(request, pk):
	drug = get_object_or_404(
		Drug.objects.prefetch_related('adverse_reactions', 'interactions_as_source__target_drug', 'interactions_as_target__source_drug'),
		pk=pk,
	)
	return render(request, 'drugs/drug_detail.html', {'drug': drug})
