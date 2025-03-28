from producto.models import Producto
from venta.models import DetalleVenta
from django.db import models

def extraer_producto(texto):
    # Buscar productos por código o descripción
    if texto.isdigit():
        # Si el texto es solo números, buscar por código
        productos = Producto.objects.filter(codigo=texto)
    else:
        # Si el texto contiene letras, buscar por nombre o descripción
        productos = Producto.objects.filter(nombre__icontains=texto) | Producto.objects.filter(descripcion__icontains=texto)

    return productos  # Devuelve un queryset con los productos encontrados

def obtener_ultimas_ventas_producto(producto):
    ventas = DetalleVenta.objects.filter(producto=producto).order_by('-fecha')[:5]
    return "\n".join([f"Fecha: {venta.fecha}, Cantidad: {venta.cantidad}, Total: ${venta.total}" for venta in ventas])

def obtener_total_vendido(producto):
    total_vendido = DetalleVenta.objects.filter(producto=producto).aggregate(total=models.Sum('cantidad')).get('total')
    return total_vendido or 0

def calcular_rentabilidad_producto(producto):
    # Aquí puedes calcular la rentabilidad, por ejemplo, tomando el costo y el precio de venta
    ingresos = producto.precio_venta()
    costo = producto.costo_unitario()
    rentabilidad = ((ingresos - costo) / costo) * 100 if costo > 0 else 0
    return round(rentabilidad, 2)
