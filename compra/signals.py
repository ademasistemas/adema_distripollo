from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Compra
from producto.models import ProductoPrecio

@receiver(post_save, sender=Compra)
def recalculate_prices(sender, instance, **kwargs):

    if instance.estado == True:
        # Obtiene todos los registros de ProductoPrecio y recalcula los precios
        for precio in ProductoPrecio.objects.all():
            precio.precio_manual = precio.precio_unitario_calculado()
            precio.save()
