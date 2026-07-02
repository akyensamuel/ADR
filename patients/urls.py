from django.urls import path

from . import views

urlpatterns = [
    path('', views.record_list, name='patient-record-list'),
    path('<str:patient_id>/', views.record_detail, name='patient-record-detail'),
]