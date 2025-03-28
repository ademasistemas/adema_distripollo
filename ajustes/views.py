from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import AjusteVenta

def confirmar_ajuste(request, ajuste_id):
    ajuste = get_object_or_404(AjusteVenta, id=ajuste_id)
    try:
        ajuste.confirmar_ajuste()
        messages.success(request, "El ajuste se ha confirmado y aplicado correctamente.")
    except Exception as e:
        messages.error(request, f"Error al confirmar el ajuste: {str(e)}")
    return redirect(request.META.get('HTTP_REFERER', '/admin/'))
