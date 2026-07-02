from django.urls import path

from . import views

urlpatterns = [
    path('', views.drug_list, name='drug-list'),
    path('<int:pk>/', views.drug_detail, name='drug-detail'),
]