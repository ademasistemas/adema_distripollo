from django.urls import path
from . import views

academia_patterns = [
    path('academia/', views.academia_list, name='academia'),
]
