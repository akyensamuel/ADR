from django.urls import path
from .views import interaction_check, symptom_extraction, unified_analysis

app_name = 'detection'

urlpatterns = [
    path('interaction-check/', interaction_check, name='interaction_check'),
    path('symptom-extraction/', symptom_extraction, name='symptom_extraction'),
    path('analyze/', unified_analysis, name='unified_analysis'),
]
