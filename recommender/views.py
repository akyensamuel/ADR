from django.shortcuts import render
from detection.services.gemini_analyzer import get_safer_alternatives

def safer_alternatives(request):
    result = None
    drug_name = ''
    
    if request.method == 'POST':
        drug_name = request.POST.get('drug_name', '').strip()
        if drug_name:
            result = get_safer_alternatives(drug_name)
            
    return render(request, 'recommender/recommendation.html', {
        'result': result,
        'drug_name': drug_name
    })
