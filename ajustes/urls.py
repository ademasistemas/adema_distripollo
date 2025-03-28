from django.urls import path
from . import views

app_name = 'ajustes'

urlpatterns = [
    path('confirmar-ajuste-venta/<int:ajuste_id>/', views.confirmar_ajuste, name='confirmar-ajuste-venta'),
]
