from django.urls import path
from .views import safer_alternatives

app_name = 'recommender'

urlpatterns = [
    path('safer-alternatives/', safer_alternatives, name='safer_alternatives'),
]
