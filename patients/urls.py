from django.urls import path

from . import views

urlpatterns = [
    path('', views.record_list, name='patient-record-list'),
    path('add/', views.record_create, name='patient-record-create'),
    path('<str:patient_id>/', views.record_detail, name='patient-record-detail'),
]