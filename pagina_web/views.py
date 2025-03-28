from datetime import datetime
from django.shortcuts import render

from agenda.models import Configuracion
from producto.models import Producto
from .models import LandingPage

def landing(request):
    landing_data = LandingPage.objects.first()
    return render(request, "pagina_web/landing.html", {"landing": landing_data})

def productos(request):
    anio_actual = datetime.today().year
    landing_data = Producto.objects.filter(habilitar_venta=True)
    config = Configuracion.objects.first()
    return render(request, "pagina_web/carta.html", {"landing": landing_data, "configuracion": config, 'anio_actual':anio_actual,})