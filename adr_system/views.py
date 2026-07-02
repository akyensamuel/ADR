from django.shortcuts import render

from adr_system.forms import InteractionCheckForm, RecommendationForm
from detection.services.ddi_checker import check_pair
from drugs.models import Drug
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
    }
    return render(request, 'adr_system/home.html', context)