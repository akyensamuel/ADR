from django.urls import path

from . import views

urlpatterns = [
    path('', views.term_search, name='meddra-term-search'),
    path('<int:pk>/', views.term_detail, name='meddra-term-detail'),
]