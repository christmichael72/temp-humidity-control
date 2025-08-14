
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('range-chart/', views.range_chart, name='range_chart'),
    path('manual-input/', views.manual_input, name='manual_input'),
    path('generate-chart-pdf/', views.generate_chart_pdf, name='generate_chart_pdf'),
]
