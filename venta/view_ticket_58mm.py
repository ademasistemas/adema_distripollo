# views_ticket_58mm.py

import re
from django.http import HttpResponse
from django.views import View
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from django.shortcuts import get_object_or_404
from .models import Venta, Configuracion, PagosVentas

class ImprimirTicket58mmView(View):
    def get(self, request, venta_id):
        # Obtener venta, configuración y medios de pago
        venta = get_object_or_404(Venta, id=venta_id)
        configuracion = Configuracion.objects.first()
        medios_de_pago = PagosVentas.objects.filter(venta=venta)
        decimales = int(configuracion.mostrar_decimales)
        
        # Cálculo dinámico de la altura en mm:
        # Valores base: header, footer y espacio entre ítems
        header_height = 40    # mm (datos principales)
        footer_height = 20    # mm (totales y mensaje final)
        detalle_height = 10   # altura base para los detalles

        # Por cada detalle, asignamos espacio según la cantidad de líneas a mostrar
        for detalle in venta.detalleventa_set.all():
            lineas = 2  # nombre y cantidad
            if detalle.unidad_de_medida == "Mt2s":
                lineas += 1  # línea extra para dimensiones
            lineas += 1  # línea para precio y subtotal
            detalle_height += lineas * 3.5  # 3.5 mm por línea (valor ajustable)
        
        total_height_mm = header_height + detalle_height + footer_height + 15

        # Configurar el canvas con 58 mm de ancho y la altura calculada
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ticket_venta_{venta_id}_58mm.pdf"'
        c = canvas.Canvas(response, pagesize=(58 * mm, total_height_mm * mm))
        
        # Posición vertical inicial (desde la parte superior)
        y = total_height_mm - 10  # margen superior

        # Si la venta está anulada, mostrar aviso
        if venta.estado == 5:
            c.setFont("Helvetica-Bold", 10)
            c.setFillColorRGB(1, 0, 0)  # rojo
            c.drawCentredString((58/2)*mm, y * mm, "FACTURA ANULADA")
            c.setFillColorRGB(0, 0, 0)
            y -= 7

        # Título/Nombre del local
        c.setFont("Helvetica-Bold", 12)
        nombre_local = configuracion.nombre if configuracion and configuracion.nombre else "Tienda"
        c.drawCentredString((58/2)*mm, y * mm, nombre_local)
        y -= 4

        # Datos de la configuración (dirección, teléfono, CUIT)
        c.setFont("Helvetica", 8)
        if configuracion:
            if configuracion.direccion:
                c.drawCentredString((58/2)*mm, y * mm, configuracion.direccion)
                y -= 4
            if configuracion.telefono:
                c.drawCentredString((58/2)*mm, y * mm, configuracion.telefono)
            if configuracion.cuit:
                y -= 4
                c.drawCentredString((58/2)*mm, y * mm, configuracion.cuit)
        y -= 10

        # Datos de la venta
        c.setFont("Helvetica", 8)
        c.drawString(2 * mm, y * mm, f"Nº Venta: {venta.id}")
        y -= 4
        c.drawString(2 * mm, y * mm, f"Cliente: {venta.cliente}")
        y -= 4
        c.drawString(2 * mm, y * mm, f"Cajero: {venta.nombre_factura}")
        y -= 4
        fecha_str = venta.fecha.strftime('%d/%m/%Y %H:%M') if venta.fecha else ""
        c.drawString(2 * mm, y * mm, f"Fecha: {fecha_str}")
        y -= 6

        # Línea separadora
        c.line(2 * mm, y * mm, (58 - 2) * mm, y * mm)
        y -= 4

        # Encabezado del detalle de la venta
        c.setFont("Helvetica-Bold", 8)
        c.drawString(2 * mm, y * mm, "Detalle de Venta:")
        y -= 8
        c.setFont("Helvetica", 8)

        # Recorre cada detalle y muestra la información
        for detalle in venta.detalleventa_set.all():
            producto_line = detalle.producto.nombre
            if detalle.producto.descripcion:
                producto_line += f" {detalle.producto.descripcion}"
            producto_line += f" x {detalle.cantidad_producto}"
            c.drawString(2 * mm, y * mm, producto_line)
            y -= 4

            # Si es Mt2s, mostrar detalles de dimensiones
            if detalle.unidad_de_medida == "Mt2s":
                c.drawString(2 * mm, y * mm, f"Cant: {detalle.cantidad} x {detalle.base} x {detalle.altura} {detalle.unidad_de_medida}")
                y -= 4

            # Mostrar precio unitario y subtotal
            precio_line = f"P. Unit: {detalle.moneda} {detalle.precio:,.{decimales}f} - Subtotal: {detalle.moneda} {detalle.get_total:,.{decimales}f}"
            c.drawString(2 * mm, y * mm, precio_line)
            y -= 6  # Espacio entre detalles

        # Línea separadora antes del total
        c.line(2 * mm, y * mm, (58 - 2) * mm, y * mm)
        y -= 7

        # Muestra el total de la venta
        c.setFont("Helvetica-Bold", 10)
        total_line = f"Total {configuracion.Moneda if configuracion and configuracion.Moneda else ''}: {venta.get_cart_total:,.{decimales}f}"
        c.drawRightString((58 - 2) * mm, y * mm, total_line)

        # Mostrar medios de pago
        c.setFont("Helvetica", 8)
        c.drawString(2 * mm, y * mm, "Medios de pago:")
        y -= 4
        for pago in medios_de_pago:
            if pago.total > 0:
                pago_line = f"{pago.medio_de_pago.Nombre}: {configuracion.Moneda if configuracion and configuracion.Moneda else ''} {pago.total:,.{decimales}f}"
                c.drawString(2 * mm, y * mm, pago_line)
                y -= 4

        y -= 6
        # Mensaje final
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString((58/2)*mm, y * mm, "¡Gracias por su compra!")
        
        c.showPage()
        c.save()
        return response
