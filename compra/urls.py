from django.urls import path
from .views import pagar_deuda_proveedores

urlpatterns = [
    path('pagar_deuda_proveedores/<int:id_pago>/', pagar_deuda_proveedores, name='pagar_deuda_proveedores'),
]