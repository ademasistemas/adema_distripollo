from django.http import HttpResponse
from .models import Configuracion
from .presupuesto import generar_presupuesto_a4  # Ahora existe esta función
from .view_ticket_comandera import ImprimirTicketCommanderaView
from .view_ticket_58mm import ImprimirTicket58mmView

def imprimir_ticket(request, venta_id):
    """
    Despacha la generación del ticket según el check de configuración.
    Si el campo 'ticket_a4' es True en la configuración, utiliza el formato A4,
    de lo contrario, utiliza el formato comandera (80mm).
    """
    configuracion = Configuracion.objects.first()
    if configuracion and configuracion.tiket_comandera == "A4":
        return generar_presupuesto_a4(request, venta_id)
    elif configuracion and configuracion.tiket_comandera == "80mm":
        return ImprimirTicketCommanderaView.as_view()(request, venta_id=venta_id)
    else:
        return ImprimirTicket58mmView.as_view()(request, venta_id=venta_id)
