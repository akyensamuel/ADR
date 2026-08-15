from django.shortcuts import render
from .services import recommend_safer_alternatives

def safer_alternatives(request):
    recommendations = None
    drug_name = ''
    
    if request.method == 'POST':
        drug_name = request.POST.get('drug_name', '').strip()
        if drug_name:
            recommendations = recommend_safer_alternatives(drug_name)
            
    return render(request, 'recommender/recommendation.html', {
        'recommendations': recommendations,
        'drug_name': drug_name
    })
