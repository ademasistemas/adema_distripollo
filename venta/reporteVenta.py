from django.http import HttpResponse
from reportlab.lib.pagesizes import letter,legal
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from django.contrib import admin, messages
from agenda.models import Configuracion
import os
import locale
from django.core.files.storage import default_storage



@admin.action(description="Descargar Reporte")
def generar_reporte(modeladmin, request, queryset):

    #Validacion para que seleccione solo 1 queryset
    if len(queryset) != 1:
        messages.error(request, "Seleccione solo un pedido para generar el informe.")
        return
      
    #Capturo la ruta actual para la ruta del logo
    current_directory = os.getcwd()

    logo_path = os.path.join(current_directory, 'logo.png')

    # Obtener el primer viaje
    entrega_ventas = queryset[0]
    config = Configuracion.objects.first()


    nombre_empresa = config.nombre
    direccion_empresa = config.direccion
    telefono_empresa = config.telefono
    email_empresa = config.contactos
    

    # Obtener el primer pedido seleccionado
    #Crear el objeto
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="presupuesto_{entrega_ventas.fecha_salida}.pdf"'
    # Crear el lienzo PDF
    p = canvas.Canvas(response, pagesize=legal)

    # Agregar contenido al lienzo
    y = 950  # Posición vertical inicial
    x = 50
    
    # Verificar si el archivo de imagen del logo existe
    if logo_path:
        # Tamaño y posición del logo
        logo_width = 150  # Ancho del logo
        logo_height = 150 # Alto del logo
        logo_x = 410  # Posición horizontal del logo
        logo_y = 860  # Posición vertical del logo

        # Agregar el logo al lienzo PDF
        logo_image = ImageReader(logo_path)
        p.drawImage(logo_image, logo_x, logo_y, width=logo_width, height=logo_height)
    
 
    # Titulo del reporte
    p.setFont("Helvetica-Bold", 18)  
    p.drawString(x, y, nombre_empresa)
    y -= 20

    p.setFont("Helvetica", 12)  # Fuente normal
    p.drawString(x, y, direccion_empresa)
    y -= 15

    p.drawString(x, y, telefono_empresa)
    y -= 15

    p.drawString(x, y, email_empresa)
    y -= 15

    # Seccion de cliente - Titulo
    p.setFont("Helvetica-Bold", 12)  # Fuente en negrita y tamaño 14
    p.drawString(x, y, f"")
    y -= 20

    # Bloque entrega
    p.setFillColorRGB(0, 0, 0)  # Color de texto negro
    p.setFont("Helvetica-Bold", 12)  # Fuente en negrita y tamaño 14
    p.drawString(x, y, f"DATOS DE LA ENTREGA")
    y -= 20

    p.setFont("Helvetica-Bold", 10)
    p.drawString(x, y, "Entrega #: ")
    p.setFont("Helvetica", 10)  # Fuente normal
    codigo_str = str(entrega_ventas.id)
    p.drawString(100, y, codigo_str.zfill(4))
    y -= 15

    p.setFont("Helvetica-Bold", 10)
    p.drawString(x, y, "Fecha salida: ")
    p.setFont("Helvetica", 10)  # Fuente normal
    codigo_str = str(entrega_ventas.fecha_salida)
    p.drawString(117, y, codigo_str.zfill(4))
    y -= 15

    p.setFont("Helvetica-Bold", 10)
    p.drawString(x, y, "Fecha llegada: ")
    p.setFont("Helvetica", 10)  # Fuente normal
    codigo_str = str(entrega_ventas.fecha_llegada)
    p.drawString(122, y, codigo_str.zfill(4))
    y -= 15

    p.setFont("Helvetica-Bold", 10)
    p.drawString(x, y, "Cant. dias: ")
    p.setFont("Helvetica", 10)  # Fuente normal
    codigo_str = str(entrega_ventas.cantidad_de_dias())
    p.drawString(102, y, codigo_str)
    y -= 20

    p.setFont("Helvetica-Bold", 10)
    p.drawString(x, y, "Gastos totales: $ ")
    p.setFont("Helvetica", 10)  # Fuente normal
    costo = entrega_ventas.get_gasto_total
    codigo_str = str("{:,.2f}".format(costo))
    p.drawString(135, y, codigo_str)
    y -= 15


    p.setFont("Helvetica-Bold", 10)
    p.drawString(x, y, "Ventas totales: $ ")
    p.setFont("Helvetica", 10)  # Fuente normal
    precio = entrega_ventas.get_costo_total
    codigo_str = str("{:,.2f}".format(precio))
    p.drawString(135, y, codigo_str)
    y -= 15

    p.setFont("Helvetica-Bold", 10)
    p.drawString(x, y, "Ganancia: $ ")
    p.setFont("Helvetica", 10)  # Fuente normal
    calculo = precio - costo
    codigo_str = str("{:,.2f}".format(calculo))
    p.drawString(110, y, codigo_str)    
    y -= 30


    # Obtener los gastos
    gastos = entrega_ventas.gastos()
    cant_gastos = gastos.count()

    if gastos:
        p.setFont("Helvetica-Bold", 10)  # Fuente en negrita y tamaño 14
        p.drawString(x, y, f"GASTOS:")
        y -= 20
        for gasto in gastos:
            p.setFont("Helvetica", 10)  # Fuente en negrita
            p.drawString(x, y, f"{gasto.gasto}: $ {gasto.total:,.2f}")
            y -= 20


    
    y -=  10


    # Obtener los viajes
    ventas = entrega_ventas.ventas()

    if ventas:
        p.setFont("Helvetica-Bold", 10)  # Fuente en negrita y tamaño 14
        p.drawString(x, y, f"VENTAS:")
        y -= 20
        for venta in ventas:
            p.setFont("Helvetica", 10)  # Fuente en negrita
            cliente = str(venta.venta.cliente) if venta.venta.cliente is not None else "#"+str(venta.venta.id)
            total = str(venta.venta.total) if venta.venta.total is not None else "0"
            p.drawString(x, y, cliente + ": $ " + total)
            y -= 20

    p.save()

    return response
