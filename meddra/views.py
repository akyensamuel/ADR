from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import MedDraTerm


def term_search(request):
    query = request.GET.get('q', '').strip()
    term_type = request.GET.get('term_type', '').strip().upper()
    terms = MedDraTerm.objects.all().order_by('term_name')

    if query:
        terms = terms.filter(Q(term_name__icontains=query) | Q(normalized_name__icontains=query))

    if term_type in {'PT', 'LT'}:
        terms = terms.filter(term_type=term_type)

    return render(
        request,
        'meddra/term_search.html',
        {
            'terms': terms[:200],
            'query': query,
            'term_type': term_type,
            'term_count': MedDraTerm.objects.count(),
        },
    )


def term_detail(request, pk):
    term = get_object_or_404(MedDraTerm, pk=pk)
    return render(request, 'meddra/term_detail.html', {'term': term})