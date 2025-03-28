import os
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import legal  # O A4, según tu preferencia
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from agenda.models import Configuracion
from venta.models import Venta

def generar_presupuesto_a4(request, venta_id):
    """
    Genera un PDF en formato A4 (o legal) para la venta indicada por venta_id.
    """
    # Obtén la configuración y la venta
    config = Configuracion.objects.first()
    venta = get_object_or_404(Venta, id=venta_id)
    decimales = int(config.mostrar_decimales)
    
    # Determinar la ruta del logo
    current_directory = os.getcwd()
    if config.logo:
        logo_path = config.logo.path
    else:
        logo_path = None

    # Datos de la empresa
    nombre_empresa = config.nombre or ""
    direccion_empresa = config.direccion or ""
    telefono_empresa = config.telefono or ""

    # Crear la respuesta PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="presupuesto_{venta.id}.pdf"'

    # Crear el lienzo (en este ejemplo se usa el tamaño legal)
    p = canvas.Canvas(response, pagesize=legal)
    width, height = legal  # Dimensiones en puntos

    # Posición inicial para el contenido
    y = 940
    x = 50

    # Fondo del reporte
    color_rgb = (220/256, 220/256, 220/256)
    p.setFillColorRGB(*color_rgb)
    p.rect(0, 0, width, height, fill=True)

    # RECTÁNGULO SUPERIOR (cabecera)
    p.setFillColorRGB(1, 1, 1) 
    p.setStrokeColorRGB(1, 1, 1)
    p.setLineWidth(1)
    p.rect(25, height-150, 360, 110, fill=True, stroke=True)
    p.rect(400, height-150, 185, 110, fill=True, stroke=True)

    # Logo
    logo_width = 100
    logo_height = 100
    logo_x = 440
    logo_y = height - 145
    if logo_path:
        logo_image = ImageReader(config.logo)
        p.drawImage(logo_image, logo_x, logo_y, width=logo_width, height=logo_height)
    else:
        # Asegurate de que la ruta 'static/logo_default.png' exista
        logo_image = ImageReader("static/logo_default.png")
        p.drawImage(logo_image, logo_x, logo_y, width=logo_width, height=logo_height)

    # Segundo rectángulo en cabecera
    p.setStrokeColorRGB(1, 1, 1)
    p.setLineWidth(1)
    p.rect(25, height-260, 560, 100, fill=True, stroke=True)

    # Escribir datos de la empresa
    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(x, y, nombre_empresa)
    y -= 25
    p.setFont("Helvetica", 12)
    p.drawString(x, y, direccion_empresa)
    y -= 18
    p.drawString(x, y, telefono_empresa)

    y = height - 175
    # Datos de la venta
    p.setFillColorRGB(0.6, 0.6, 0.6)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(x - 10, y, "DATOS DE LA VENTA")
    y -= 20

    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(x, y, "Número venta:")
    p.setFont("Helvetica", 10)
    codigo_str = str(venta.id)
    p.drawString(122, y, codigo_str.zfill(4))
    y -= 15

    if venta.cliente:
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x, y, "Cliente:")
        p.setFont("Helvetica", 10)
        p.drawString(90, y, str(venta.cliente))
        y -= 15

        # Opcional: teléfono y dirección del cliente
        if hasattr(venta.cliente, 'telefono') and venta.cliente.telefono:
            p.setFont("Helvetica-Bold", 10)
            p.drawString(x, y, "Teléfono:")
            p.setFont("Helvetica", 10)
            p.drawString(100, y, str(venta.cliente.telefono))
            y -= 15
        if hasattr(venta.cliente, 'direccion') and venta.cliente.direccion:
            p.setFont("Helvetica-Bold", 10)
            p.drawString(x, y, "Dirección:")
            p.setFont("Helvetica", 10)
            p.drawString(100, y, str(venta.cliente.direccion))
            y -= 15
    else:
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x, y, "Cliente:")
        p.setFont("Helvetica", 10)
        p.drawString(90, y, "Consumidor Final")
        y -= 15

    
    y = height - 285

    # Listado de productos
    productos = venta.productos  # Asegurate de que 'productos' sea un queryset o lista de items de la venta
    p.setFillColorRGB(1, 1, 1)
    p.setStrokeColorRGB(1, 1, 1)
    p.setLineWidth(1)
    p.rect(25, 140, 560, 600, fill=True, stroke=True)

    if productos:
        p.setFillColorRGB(0.6, 0.6, 0.6)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x - 10, y - 5, "PRODUCTOS INCLUIDOS EN EL PRESUPUESTO")
        y -= 20

        p.setFillColorRGB(0, 0, 0)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x, y, "NOMBRE DE PRODUCTO")
        p.drawString(x + 230, y, "CANTIDAD")
        p.drawString(x + 300, y, " ")
        p.drawString(x + 380, y, "P. UNITARIO")
        p.drawString(x + 470, y, "TOTAL")
        y -= 20

        numero_item = 1
        for producto in productos:
            p.setFillColorRGB(0.6, 0.6, 0.6)
            p.setFont("Helvetica-Bold", 10)
            p.drawString(x - 16, y, str(numero_item))
            p.setFillColorRGB(0, 0, 0)
            p.setFont("Helvetica", 10)
            if producto.producto.descripcion:
                nombre_producto = f"{producto.producto.nombre} | {producto.producto.descripcion}"
            else:
                nombre_producto = producto.producto.nombre
            if len(nombre_producto) > 40:
                nombre_producto = nombre_producto[:40]
            p.drawString(x, y, nombre_producto)
            if producto.unidad_de_medida == "Mt2s":
                p.drawString(x + 230, y, f"{producto.cantidad}x{producto.base/1000}x{producto.altura/1000}")
            else:
                p.drawString(x + 245, y, str(producto.cantidad))
            p.drawString(x + 310, y, producto.unidad_de_medida)
            p.drawString(x + 400, y, f"${producto.precio:,.{decimales}f}")
            p.drawString(x + 470, y, f"${producto.get_total:,.{decimales}f}")
            numero_item += 1
            y -= 15

    # Rectángulo inferior con totales
    p.setFillColorRGB(1, 1, 1)
    p.setStrokeColorRGB(1, 1, 1)
    p.setLineWidth(1)
    p.rect(25, 20, 560, 110, fill=True, stroke=True)
    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 13)
    p.drawString(300, 100, "TOTAL: ")
    p.setFillColorRGB(1, 0, 0)
    p.setFont("Helvetica", 13)
    p.drawString(450, 100, f"${venta.get_cart_total:,.{decimales}f}")
    y -= 15
    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 13)
    p.drawString(300, 80, "Descuentos: ")
    p.setFillColorRGB(1, 0, 0)
    p.setFont("Helvetica", 13)
    p.drawString(450, 80, f"${0:,.{decimales}f}")
    total_bruto = float(venta.get_cart_total)
    descuentos = 0.0
    costo_de_envio = float(venta.total_entrega)
    total_bruto = total_bruto - descuentos - costo_de_envio
    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(300, 35, "TOTAL A PAGAR: ")
    p.setFillColorRGB(1, 0, 0)
    p.setFont("Helvetica", 16)
    p.drawString(450, 35, f"${total_bruto:,.{decimales}f}")
    y -= 15

    p.showPage()
    p.save()
    return response
