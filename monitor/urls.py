
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/latest-data/', views.latest_data_api),
    path('manual-input/', views.manual_input, name='manual_input'),
    path('generate-chart-pdf/', views.generate_chart_pdf, name='generate_chart_pdf'),
]
