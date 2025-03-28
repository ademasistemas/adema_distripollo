
import datetime
import re
from django.db.models.functions import Cast
from django.db.models import IntegerField
import calendar
from django.contrib import messages
from decimal import InvalidOperation
from django.shortcuts import redirect
from django.db.models import Sum, Q,F, ExpressionWrapper, DecimalField
from datetime import date, datetime, time,timedelta
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext as _
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views import View
from .models import *
from django.views.generic import ListView, UpdateView, DetailView
from django.utils.decorators import method_decorator
from venta.forms import VentaForm, VentaFacturaForm
from venta.models import PagosVentas, Venta, DetalleVenta
from django.http import Http404
from agenda.models import *
from agenda.models import medioDeCompra
from compra.models import Compra, medioDePagoCompra
from producto.models import Producto, ProductoPrecio
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from reportlab.lib.pagesizes import letter
from pytz import timezone
from django.db.models.functions import Cast, Lower
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas


UNIDADES_DE_MEDIDA = [
    ('Unidades', 'unidades'),
    ('Kilos', 'kilos'),
    ('Gramos', 'gramos'),
    ('Litros', 'litros'),
    ('Mililitros', 'mililitros'),
    ('Onzas', 'onzas'),
    ('Libras', 'libras'),
]

FACTORES_CONVERSION = {
    ('Unidades', 'Unidades'): 1,
    ('Kilos', 'Kilos'): 1,
    ('Gramos', 'Gramos'): 1,
    ('Litros', 'Litros'): 1,
    ('Mililitros', 'Mililitros'): 1,
    ('Onzas', 'Onzas'): 1,
    ('Libras', 'Libras'): 1,
    ('Kilos', 'Gramos'): 1000,
    ('Gramos', 'Kilos'): 0.001,
    ('Litros', 'Mililitros'): 1000,
    ('Mililitros', 'Litros'): 0.001,
    ('Onzas', 'Libras'): 0.0625,  
    ('Libras', 'Onzas'): 16,
}


from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test

import pandas as pd
from django.http import HttpResponse
from producto.models import Producto

@login_required(login_url='/admin/login/')
def descargar_productos_excel(request):
    """
    Genera y descarga un archivo Excel con toda la lista de productos sin paginación.
    """
    # Obtener todos los productos
    productos = Producto.objects.exclude(habilitar_venta=False).filter(productoprecio__isnull=False).order_by('nombre')

    # Crear una lista con los datos de los productos
    data = []
    for producto in productos:
        data.append([
            producto.id,
            producto.codigo if producto.codigo else "N/A",
            producto.nombre,
            producto.descripcion if producto.descripcion else "Sin descripción",
            producto.categoria.nombre if producto.categoria else "Sin categoría",
            producto.primer_producto_precio.precio if producto.primer_producto_precio else 0,
            producto.stock_actual()
        ])

    # Crear DataFrame con Pandas
    df = pd.DataFrame(data, columns=['ID', 'Código', 'Nombre', 'Descripción', 'Categoría', 'Precio Unitario', 'Stock'])

    # Crear respuesta HTTP con el archivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="productos.xlsx"'

    # Guardar en un buffer y enviarlo como respuesta
    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Productos")

    return response


def custom_logout(request):
    logout(request)
    return redirect('/')


def is_superuser(user):
    return user.is_superuser

    
class PrintTicketPDFView(View):
    
    def get(self, request, venta_id):
        venta = Venta.objects.get(id=venta_id)
        template_path = 'ticket.html'
        configuracion = Configuracion.objects.all().first()
        medios_de_pago = PagosVentas.objects.filter(venta=venta)

        context = {'venta': venta,'configuracion':configuracion,'medios_de_pago':medios_de_pago,}
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename="ticket_venta_{venta_id}.pdf"'
        template = get_template(template_path)
        html = template.render(context)

        pisa_status = pisa.CreatePDF(html, dest=response)

        if pisa_status.err:
            return HttpResponse('Error al generar el PDF', status=500)

        return response

from django.conf import settings
from django.templatetags.static import static
import os
def fetch_resources(uri, rel):
    """
    Función para manejar recursos estáticos y media para xhtml2pdf.
    """
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        path = uri  # Ruta absoluta si no es un recurso estático o media
    return path
 
@login_required
def imprimir_ticket(request, venta_id):
    usuario_actual = request.user
    asignacion_usuario = Asignacion.objects.filter(usuario=usuario_actual).first()
    configuracion = Configuracion.objects.all().first()

    if asignacion_usuario:
        caja_usuario = asignacion_usuario.caja.Nombre
    else:
        caja_usuario = 'Administrador'

    # Obtén la venta actual
    venta = obtener_venta_actual(caja_usuario)

    # Cargar la plantilla HTML del ticket
    template = get_template('ticket.html')

    # Contexto para la plantilla
    context = {
        'venta': venta,
        'configuracion': configuracion,
    }

    # Renderizar la plantilla con el contexto
    rendered_template = template.render(context)

    # Crear un objeto de respuesta HTTP con el tipo MIME adecuado para PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=ticket_venta_{venta_id}.pdf'

    # Convertir la plantilla HTML a PDF y guardar en el objeto de respuesta
    pisa_status = pisa.CreatePDF(
        rendered_template,
        dest=response,
        encoding='utf-8',
        link_callback=fetch_resources,  # Aquí se pasa la función fetch_resources
    )

    # Si la conversión fue exitosa, enviar el PDF como respuesta; de lo contrario, devolver un error
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)

    return response

@method_decorator(login_required, name='dispatch')
class VentaList(ListView):
    model = Venta
    
    def get_queryset(self):
        # Obtener la fecha actual
        fecha_actual = date.today()

        user = self.request.user
        asignacion_caja = Asignacion.objects.filter(usuario=user).first()
        
        # Verificar si el usuario tiene una asignación de caja
        if not asignacion_caja:
            raise Http404("El usuario no tiene asignación de caja.")
        
        if asignacion_caja.caja == "Administrador" and asignacion_caja:
            # Filtrar las ventas del día actual por defecto
            queryset = Venta.objects.filter(fecha__date=fecha_actual).order_by('-fecha')
        elif asignacion_caja:
            # Filtrar las ventas del día actual por defecto y por usuario
            queryset = Venta.objects.filter(fecha__date=fecha_actual,nombre_factura=asignacion_caja.caja).order_by('-fecha')
        else:
            return 404

        desde = self.request.GET.get('desde')
        hasta = self.request.GET.get('hasta')

        filtro_entregado = self.request.GET.get('entregado')

        if filtro_entregado == "Si":
            filtro_entregado = True
        else:
            filtro_entregado = False

        if desde and hasta:
            # Filtrar las ventas dentro del rango de fechas especificado
            queryset = Venta.objects.filter(
                entregado=filtro_entregado,
                nombre_factura=asignacion_caja.caja,
                fecha__date__range=[desde, hasta],  # Utilizar el rango de fechas
                estado__in=[1, 2, 3, 5]  # Filtrar por estados específicos
            ).order_by('-fecha')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        configuracion = Configuracion.objects.all().first()

        desde = self.request.GET.get('desde')
        hasta = self.request.GET.get('hasta')


        user = self.request.user
        asignacion_caja = Asignacion.objects.filter(usuario=user).first()

        # Obtener la fecha actual
        fecha_actual = date.today()

        if asignacion_caja.caja == "Administrador":
            # Filtrar las ventas del día actual por defecto
               # Filtrar las ventas del día actual por defecto
            lista_ventas = DetalleVenta.objects.filter(venta__fecha__date=fecha_actual).order_by('-id')

        else:
            # Filtrar las ventas del día actual por defecto y por usuario
            lista_ventas = DetalleVenta.objects.filter(venta__fecha__date=fecha_actual,venta__nombre_factura=asignacion_caja.caja).order_by('-id')

        

     
        # Resto de tu código de context
        context['lista_ventas'] = lista_ventas

        context['configuracion'] = configuracion

        # Agregar cualquier otro contexto adicional que necesites aquí
        return context

class VentaDetail(DetailView):
    model = Venta

class VentaFactura(UpdateView):
    """
    Facturación de la venta, la venta no puede ser facturada si no se encuentra en estado pagada
    """
    model = Venta
    form_class = VentaFacturaForm
    template_name_suffix = '_facturar_form'
    success_url = reverse_lazy('venta:carrito')

    def dispatch(self, request, *args, **kwargs):
        # La venta no puede entrar a esta vista si se encuentra en estado pagada
        venta = Venta.objects.get(id=self.kwargs['pk'])

        if not venta.estado == venta.ESTADO_PAGADA:
            return HttpResponseBadRequest()

        return super(VentaFactura, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        venta = get_object_or_404(Venta, id=self.kwargs['pk'])
        redirect_url = super(VentaFactura, self).form_valid(form)
        cliente = form.cleaned_data['cliente']
        vendedor = form.cleaned_data['vendedor']
        venta.cliente = cliente
        venta.vendedor = vendedor
        venta.save()
        return redirect_url

class VentaUpdate(UpdateView):
    """
    Actualización de la venta (cambiar de estado a anulada o cancelada), ningún otro cambio puede ser actualizado
    """


    model = Venta
    form_class = VentaForm
    template_name_suffix = '_update_form'
    success_url = reverse_lazy('venta:ventas')

    def dispatch(self, request, *args, **kwargs):
        # La venta no puede entrar a esta vista si se encuentra en estado cancelada o anulada
        venta = Venta.objects.get(id=self.kwargs['pk'])
        if venta.estado == venta.ESTADO_ANULADA or venta.estado == venta.ESTADO_CANCELADA:
            return HttpResponseBadRequest()

        return super(VentaUpdate, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(VentaUpdate, self).get_context_data(**kwargs)
        venta = get_object_or_404(Venta, id=self.kwargs['pk'])
        context['venta'] = venta
        return context

    def form_valid(self, form):
        venta = get_object_or_404(Venta, id=self.kwargs['pk'])
        redirect_url = super(VentaUpdate, self).form_valid(form)
        motivo = form.cleaned_data['razon_cancelacion']

        if venta.estado == venta.ESTADO_CREADA:
            venta.cancelar(motivo)
            obtener_venta_actual(self.caja_usuario)  # Usar la caja del usuario
        else:
            venta.anular(motivo)

        devolver_productos_a_stock(venta.id)
        venta.save()
        return redirect_url

@login_required   
def entregar_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    venta.entregado = True
    venta.save()
    return redirect('venta:ventas')

def login(request):

    context = {'hola': 'hola', }
    return render(request, 'login.html', context)

@login_required(login_url='/admin/login/')
def dashboard(request):

    # Obtener la fecha actual
    fecha_actual = date.today()

    desde = request.GET.get('desde')  # Obtener el valor desde el parámetro GET
    hasta = request.GET.get('hasta')  # Obtener el valor hasta el parámetro GET
    moneda = request.GET.get('moneda')

    configuracion = Configuracion.objects.all().first()
    user = request.user

    caja_user = Asignacion.objects.filter(usuario=user).first()

    if caja_user.caja == "Administrador":      
        # Filtrar las ventas del día actual por defecto
        lista_ventas = DetalleVenta.objects.filter(venta__fecha__date=fecha_actual).order_by('-id')
    else:
        # Filtrar las ventas del día actual por defecto
        lista_ventas = DetalleVenta.objects.filter(venta__fecha__date=fecha_actual,venta__nombre_factura=caja_user.caja).order_by('-id')
 
    if desde and hasta:

        if caja_user.caja == "Administrador": 
            # Filtrar las ventas dentro del rango de fechas especificado
            ventas_filtradas = Venta.objects.filter(
                fecha__date__range=[desde, hasta],  # Utilizar el rango de fechas
                estado__in=[ 2, 3]  # Filtrar por estados específicos
            ).order_by('-fecha')
        else:
            # Filtrar las ventas dentro del rango de fechas especificado
            ventas_filtradas = Venta.objects.filter(
                nombre_factura=caja_user.caja,
                fecha__date__range=[desde, hasta],  # Utilizar el rango de fechas
                estado__in=[ 2, 3]  # Filtrar por estados específicos
            ).order_by('-fecha')  

        lista_ventas = DetalleVenta.objects.filter(venta__in=ventas_filtradas)

    else:
        
        ventas_filtradas = Venta.objects.all().order_by('-fecha')
    
    page_size = 50  # Define la cantidad de elementos por página
    paginator = Paginator(lista_ventas, page_size)
    page_number = request.GET.get('page')  # Obtener el número de página de la solicitud GET
    page = paginator.get_page(page_number)  # Obtener la página actual

    # Calcular el total de ventas filtrado por moneda="Pesos"
    total_ars = sum(item.get_total for item in lista_ventas if item.moneda == configuracion.Moneda)
    # Calcular el total de ventas filtrado por moneda="Dolares"
    total_usd = sum(item.get_total for item in lista_ventas if item.moneda == configuracion.Moneda_secundaria)


    # Obtener la fecha actual en Argentina
    argentina_timezone = timezone('America/Argentina/Buenos_Aires')
    fecha_actual = datetime.now(argentina_timezone)

    # Obtener el mes actual
    mes_actual = fecha_actual.month

    # Obtener el nombre del mes actual
    mes = calendar.month_name[mes_actual]

    context = {
        'lista_ventas': lista_ventas, 
        'page': page,
        'mes':mes,
        'total_ars':total_ars,
        'total_usd':total_usd,
        'configuracion':configuracion
        }
    return render(request, 'home.html', context)

@login_required(login_url='/admin/login/')
def product_list(request):
    """
    Vista de lista de productos, en esta vista se encuentra también la lógica de añadir producto al carrito
    :param request:
    :return:
    """
    data = {}
    usuario_actual = request.user
    asignacion_usuario = Asignacion.objects.filter(usuario=usuario_actual).first()
    configuracion = Configuracion.objects.all().first()
    
    if asignacion_usuario:
        caja_usuario = asignacion_usuario.caja
    else:
        # Maneja el caso en el que el usuario no tenga asignada una caja
        caja_usuario = 'Administrador'  # Puedes definir una caja predeterminada o manejarlo de otra manera

    # Asegúrate de que se utiliza el nombre de la caja y no la instancia de Caja
    nombre_caja = caja_usuario.Nombre if isinstance(caja_usuario, Caja) else str(caja_usuario)
    
    # Obtener todas las ventas en estado "CREADA" para este nombre de caja
    ventas_creadas = Venta.objects.filter(nombre_factura=nombre_caja, estado=Venta.ESTADO_CREADA)

    # Si hay más de una venta creada, eliminar la primera (más antigua)
    if ventas_creadas.count() > 1:
        ventas_creadas.first().delete()

    
    # Ahora, intentar obtener o crear la venta actual
    venta, created = Venta.objects.get_or_create(
        nombre_factura=nombre_caja,
        estado=Venta.ESTADO_CREADA,
        defaults={'cliente': None, 'total': 0}
    )
    productos_queryset = Producto.objects.exclude(habilitar_venta=False).filter(productoprecio__isnull=False).order_by('nombre').distinct()
    if configuracion.stock_negativo_ldp:
        
        lista_productos = [producto for producto in productos_queryset if not producto.stock_es_negativo]
    else:
        lista_productos = Producto.objects.exclude(habilitar_venta=False).filter(productoprecio__isnull=False).order_by('nombre').distinct()

    orden = request.GET.get('ordenar', 'codigo')

    if orden == "codigo":
        def obtener_valor_codigo(p):
            """
            Convierte códigos numéricos a enteros para ordenarlos correctamente.
            Si el código no es numérico, lo deja como string.
            """
            try:
                return int(p.codigo)  # Si es numérico, lo convierte a int
            except (ValueError, TypeError):
                return str(p.codigo)  # Si no, lo deja como string

        lista_productos = sorted(productos_queryset, key=obtener_valor_codigo)

    elif orden == "categoria":
        # Ordenar por categoría (si existe) y luego por nombre
        lista_productos = sorted(lista_productos, key=lambda p: ((p.categoria.nombre if p.categoria else ''), p.nombre))
        
    else:  # Orden por nombre por defecto
        lista_productos = sorted(lista_productos, key=lambda p: p.nombre)

    if request.method == 'POST':
        if 'btnsearch' in request.POST:
            search = request.POST['search']
            if not search == '':
                lista_productos = Producto.objects.filter(
                    Q(codigo__contains=search) |Q(nombre__contains=search) | Q(categoria__nombre__contains=search)).distinct()
            else:
                lista_productos = Producto.objects.order_by('nombre')
            if not lista_productos:
                data['status'] = 'Sin resultados'

        else:

            producto = get_object_or_404(Producto, id=request.POST['id_producto'])
            producto_precio = ProductoPrecio.objects.get(pk=request.POST['venta_caja'])
            cantidad = Decimal(request.POST['cantidad'])
            if producto.unidad_de_medida == "Mt2s":
                base = Decimal(request.POST['base'])
                altura = Decimal(request.POST['altura'])

                data['status'] = agregar_producto_a_carrito(venta, cantidad, base, altura, producto_precio, producto)
            else:
                base = Decimal(1)
                altura = Decimal(1)
                data['status'] = agregar_producto_a_carrito(venta, cantidad, base, altura, producto_precio, producto)


    page_size = 16 #32  # Define la cantidad de elementos por página
    paginator = Paginator(lista_productos, page_size)
    page_number = request.GET.get('page')  # Obtener el número de página de la solicitud GET
    page = paginator.get_page(page_number)  # Obtener la página actual
    
    context = {'producto_list': page, 'data': data, 'venta': venta,'configuracion':configuracion}

    return render(request, 'venta/producto_list.html', context)

@login_required(login_url='/admin/login/')
def carrito(request):
    """
    Vista de carrito, en esta vista se muestran los productos añadidos a la venta actual además de podes cambiar de estado
    a la venta y remover productos del 'carrito'

    :param request:
    :return:
    """

    usuario_actual = request.user
    asignacion_usuario = Asignacion.objects.filter(usuario=usuario_actual).first()
    configuracion = Configuracion.objects.first()
    precio_km = PrecioPorKilometro.objects.all().first()
    medio_pago = medioDePago.objects.all()

    if asignacion_usuario:
        caja_usuario = asignacion_usuario.caja.Nombre
    else:
        # Maneja el caso en el que el usuario no tenga asignada una caja
        caja_usuario = 'Administrador'  # Puedes definir una caja predeterminada o manejarlo de otra manera


    venta = obtener_venta_actual(caja_usuario)  # Pasa la caja del usuario a la función obtener_venta_actual()
    venta_ant = obtener_ultima_venta(caja_usuario)
   
    lista_detalle = DetalleVenta.objects.filter(venta=venta)

    lista_clientes = Cliente.objects.all()
    precio_por_kl = PrecioPorKilometro.objects.first() 
    
    data = {}

    total_mdp_1 = 0
    total_mdp_2 = 0
    medio_de_pago_1=""
    medio_de_pago_2=""

    if request.method == 'POST':
        

        if 'medio_pago_1' in request.POST:
            medio_de_pago_1 = request.POST['medio_pago_1']
            total_mdp_1 = Decimal(request.POST['total_1'])


        if 'medio_pago_2' in request.POST:
            medio_de_pago_2 = request.POST['medio_pago_2']
            total_mdp_2 = Decimal(request.POST['total_2'])

        if 'cantidadKl' in request.POST:
            precio_por_kl = precio_por_kl.total if precio_por_kl is not None else 0
            venta.total_entrega=Decimal(request.POST['cantidadKl']) * precio_por_kl
            venta.save()

        if 'reservar' in request.POST:
            reserva = medio_pago.filter(Nombre="Cuenta Corriente").first()
            pago = PagosVentas.objects.create(
                venta=venta,
                cliente=venta.cliente,
                medio_de_pago=reserva,
                total=venta.get_cart_total,
                cancelado=False
            )
            
            venta.pagar()
            venta.finalizar()
            venta.save()
            new_venta = obtener_venta_actual(caja_usuario)
            return redirect('venta:carrito')
                  
        if 'pagar' in request.POST:

            try:
                
                total_1 = total_mdp_1
                total_2 = total_mdp_2
                total_pagos = round(total_1 + total_2,0)
                total_venta = round(venta.get_cart_total,0)

                if total_venta == total_pagos:
                    medio_pago_1 = medioDePago.objects.get(pk=request.POST['medio_pago_1'])
                    medio_pago_2 = medioDePago.objects.get(pk=request.POST['medio_pago_2'])

                    if medio_pago_1.cuenta_corriente:
                        pago_1 = PagosVentas.objects.create(
                            venta=venta,
                            cliente=venta.cliente,
                            medio_de_pago=medio_pago_1,
                            total=total_1,
                            cancelado=False
                        )
                    else:
                        pago_1 = PagosVentas.objects.create(
                            venta=venta,
                            cliente=venta.cliente,
                            medio_de_pago=medio_pago_1,
                            total=total_1,
                            cancelado=True
                        )

                    if total_2 > 0:
                        if medio_pago_2.cuenta_corriente:
                            pago_2 = PagosVentas.objects.create(
                                venta=venta,
                                cliente=venta.cliente,
                                medio_de_pago=medio_pago_2,
                                total=total_2,
                                cancelado=False
                            )
                        else:
                            pago_2 = PagosVentas.objects.create(
                                venta=venta,
                                cliente=venta.cliente,
                                medio_de_pago=medio_pago_2,
                                total=total_2,
                                cancelado=True
                            )

                    venta.pagar()
                    venta.finalizar()
                    venta.save()
                    new_venta = obtener_venta_actual(caja_usuario)
                    return redirect('venta:carrito')
                    
                else:
                    print(f"Error de pagos")

            except InvalidOperation as e:
                print(f"Error de operación decimal: {e}")

        elif 'facturar' in request.POST:
            pass

        elif 'finalizar' in request.POST:
            venta.finalizar()
            venta.save()
            new_venta = obtener_venta_actual(caja_usuario)
            lista_detalle = DetalleVenta.objects.filter(venta=new_venta)
            
            return redirect('venta:carrito')
    
        elif 'detalle_id' in request.POST: #si
            nueva_cantidad = request.POST['nueva_cantidad']
            nuevo_precio = request.POST['nuevo_precio']
            detalle_id = request.POST['detalle_id']
            detalle_venta = DetalleVenta.objects.get(id=detalle_id)
            detalle_venta.cantidad = nueva_cantidad
            detalle_venta.precio = nuevo_precio
            #detalle_venta.total = nuevo_precio * nueva_cantidad
            detalle_venta.save()

        elif 'id_cliente' in request.POST:
            cliente_id = request.POST.get('id_cliente')
            if cliente_id:
                try:
                    cliente = Cliente.objects.get(id=cliente_id)
                    venta.cliente = cliente
                    venta.save()
                    messages.success(request, f"Cliente '{cliente.nombre}' seleccionado correctamente.")
                except Cliente.DoesNotExist:
                    messages.error(request, "Cliente no válido.")
            else:
                messages.error(request, "Por favor selecciona un cliente válido.")


                
        elif 'detalle_id_delete' in request.POST:
            nombre_producto_eliminado = eliminar_de_carrito(request.POST['detalle_id_delete'])
            data['eliminado'] = 'Se ha eliminado del carrito: ' + nombre_producto_eliminado + ' de manera exitosa'
       
    return render(request, 'venta/carrito.html',
                  {'lista_detalle': lista_detalle, 'venta': venta, 'venta_ant': venta_ant, 'data': data,'lista_clientes':lista_clientes,'configuracion':configuracion, 'venta_por_kl':bool(precio_por_kl is not None),'precio_km':precio_km,'medio_pago':medio_pago,})

@login_required(login_url='/admin/login/')
@user_passes_test(is_superuser, login_url='/')
def reporte_ventas(request):

    configuracion = Configuracion.objects.all().first()
    
    fecha_actual = date.today()
    fecha_actual_formateada = fecha_actual.strftime("%d/%m")

    # 🔹 Obtener mes y año desde la URL, si no, usar valores por defecto
    mes = int(request.GET.get('mes', date.today().month)) or date.today().month
    anio = int(request.GET.get('anio', date.today().year))  or date.today().year

    # 🔹 Calcular primer y último día del mes seleccionado
    primer_dia_mes = datetime(anio, mes, 1)
    ultimo_dia_mes = datetime(anio, mes, calendar.monthrange(anio, mes)[1])

    mes_actual = _(calendar.month_name[primer_dia_mes.month])

    ventas_grafico = DetalleVenta.Total_ventas(primer_dia_mes,ultimo_dia_mes)

    # Filtrar ventas y calcular la suma de la cantidad y el precio
    top_ventas = DetalleVenta.objects.filter(
        venta__fecha__range=[primer_dia_mes, ultimo_dia_mes]
    ).values(
        'producto__descripcion', 'producto__nombre', 'producto__codigo', 'ganancias_estimadas'
    ).annotate(
        can_ventas=Sum(F('cantidad') * F('cantidad_producto')),  # Multiplica la cantidad base por la cantidad del precio
        total_unitario=Sum(F('precio') * F('cantidad') * F('cantidad_producto')),  # Incluye el cálculo correcto
        total=Sum(ExpressionWrapper(F('cantidad') * F('precio') * F('cantidad_producto'), output_field=DecimalField())),
    ).order_by('-can_ventas')[:10]



    top_ventas_recetas = DetalleVenta.objects.all().values(
        'producto').annotate(total_ventas=Sum('cantidad')).order_by('-total_ventas')[:10]
   
    ventas_mes = DetalleVenta.ventas_mensual(primer_dia_mes,ultimo_dia_mes)
    pendientes_mes = DetalleVenta.pagos_pendientes(primer_dia_mes,ultimo_dia_mes)
    adicional_recargo_cc = DetalleVenta.pagos_adicionales_pendientes(primer_dia_mes,ultimo_dia_mes)
    neto_ventas = ventas_mes - pendientes_mes - adicional_recargo_cc
    
    gastos_mes = Gasto.total_calculado(primer_dia_mes,ultimo_dia_mes) or 0
    gastos_fijos = Gasto.total_fijo_calculado(primer_dia_mes,ultimo_dia_mes) or 0
    gastos_variables = gastos_mes - gastos_fijos

    compras_mes =  medioDePagoCompra.compras_mensual(primer_dia_mes,ultimo_dia_mes) or 0
    compras_pendientes_mes = medioDePagoCompra.pagos_pendientes(primer_dia_mes,ultimo_dia_mes) or 0
    neto_compras = compras_mes - compras_pendientes_mes
    
    ventas_hoy = DetalleVenta.objects.filter(fecha=fecha_actual)

    #ventas_hoy = sum(item.get_total for item in ventas_hoy.filter(moneda=configuracion.Moneda,venta__estado=3))
    ventas_hoy = sum(
        item.get_total
        for item in DetalleVenta.objects.filter(
            fecha=fecha_actual,
            venta__estado=3
        )
    )


    ventas_por_caja = Venta.totales_por_caja(fecha_actual)

    valuacion_inventario_positivos = Producto.valuacion()
    valuacion_inventario_negativos = 0
    valuacion_inventario_neta=0
    
    cobrado_a_clientes=0
    cobrado_a_clientes =  Venta.cobroCliente(cobrado_a_clientes)
    
    context = {

        'configuracion':configuracion,
        'fecha_actual_formateada':fecha_actual_formateada,
        'mes_actual':mes_actual,

        'ventas_hoy': ventas_hoy or 0,
        'ventas_mes_actual': ventas_mes or 0, 
        'neto_ventas':neto_ventas or 0,
        'pendientes_mes':pendientes_mes or 0, 

        'compras_mes_actual': compras_mes or 0,
        'compras_pendientes_mes':compras_pendientes_mes or 0,
        'neto_compras':neto_compras or 0,

        'gastos_mes': gastos_mes or 0,
        'gastos_fijos': gastos_fijos or 0,
        'gastos_variables': gastos_variables or 0,

        'top_ventas':top_ventas,
        'top_ventas_recetas':top_ventas_recetas,
        'ventas_por_caja':ventas_por_caja,
        'ventas_grafico':ventas_grafico, 

        'valuacion_inventario_positivos': valuacion_inventario_positivos,
        'valuacion_inventario_negativos': valuacion_inventario_negativos,
        'valuacion_inventario_neta': valuacion_inventario_neta,

        'cobrado_a_clientes':cobrado_a_clientes,
        'mes_seleccionado': mes,  # 🔹 Para preseleccionar el mes en el template
        'anio_seleccionado': anio,  # 🔹 Para preseleccionar el año en el template
    }

    return render(request, 'reporte_ventas.html', context)


@login_required(login_url='/admin/login/')
@user_passes_test(is_superuser, login_url='/')
def reporte_ganancias(request):

    configuracion = Configuracion.objects.all().first()
    

    fecha_actual = date.today()
    fecha_actual_formateada = fecha_actual.strftime("%d/%m")
    
        # Obtener mes y año del formulario o usar valores predeterminados
    selected_date = request.GET.get('month_year')
    if selected_date:
        year, month = map(int, selected_date.split('-'))
    else:
        month = date.today().month
        year = date.today().year

    # primer_dia_mes = fecha_actual.replace(day=1)
    # ultimo_dia_mes = primer_dia_mes.replace(day=28) + timedelta(days=4) - timedelta(days=1)

    # Obtener la fecha inicial y final del mes seleccionado
    primer_dia_mes = datetime(year, month, 1)
    ultimo_dia_mes = (primer_dia_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    ventas_semestral = []
    costos_semestral = []
    gastos_semestral = []
    dias_semestral = []
    ventas_diario = []
    rentablilidad_semestral = []

    rentabilidad_diaria=0
    dias_repo = 30

    #fecha_final = fecha_actual + timedelta(days=1)

    for dia in range(dias_repo - 1, -1, -1):
        fecha_dia = ultimo_dia_mes - timedelta(days=dia)
        fecha_dia_formateada = fecha_dia.strftime("%d/%m")
        dias_semestral.append("")
        dias_semestral.append(fecha_dia_formateada)
        
    dias_semestral.reverse()

    for dia in range(dias_repo, 0, -1):
        fecha_dia = ultimo_dia_mes - timedelta(days=dia)
        total_diario = DetalleVenta.ventas_mensual(fecha_dia,fecha_dia)
        ventas_semestral.append(total_diario)
    ventas_semestral.reverse()

    for dia in range(dias_repo, 0, -1):
        fecha_dia = ultimo_dia_mes - timedelta(days=dia)
        total_diario = DetalleVenta.Total_costos(fecha_dia,fecha_dia)
        costos_semestral.append(total_diario)
    costos_semestral.reverse()

    for dia in range(dias_repo, 0, -1):
        fecha_dia = ultimo_dia_mes - timedelta(days=dia)
        total_diario = Gasto.total_calculado(fecha_dia,fecha_dia)
        gastos_semestral.append(total_diario)
    gastos_semestral.reverse()

    for dia in range(dias_repo, 0, -1):
        fecha_dia = ultimo_dia_mes - timedelta(days=dia)
        rentabilidad_diaria = DetalleVenta.ganancias_calculadas(fecha_dia, fecha_dia)
        rentablilidad_semestral.append(rentabilidad_diaria)
        ventas_diario.append(rentabilidad_diaria)

    ventas_diario.reverse()
    rentablilidad_semestral.reverse()

    ventas_mensual = DetalleVenta.ventas_mensual(ultimo_dia_mes - timedelta(days=30),ultimo_dia_mes) # total vendido
    costos_mensual = DetalleVenta.Total_costos(ultimo_dia_mes - timedelta(days=30),ultimo_dia_mes) # total costos
    gastos_mensual = Gasto.total_calculado(ultimo_dia_mes - timedelta(days=30),ultimo_dia_mes) # total costos
    ganancias = DetalleVenta.ganancias_calculadas(ultimo_dia_mes - timedelta(days=30),ultimo_dia_mes) # total costos
    rentablilidad = float(round(float(ganancias) - float(gastos_mensual),2))

    context = {
        'configuracion':configuracion,
        'fecha_actual_formateada':fecha_actual_formateada,

        'ventas_mensual': ventas_mensual or 0,
        'costos_mensual': costos_mensual or 0,
        'gastos_mensual': gastos_mensual or 0,
        'rentablilidad': rentablilidad or 0,  
        'ventas_diario':ventas_diario or 0,

        'costos_semestral': costos_semestral,
        'gastos_semestral': gastos_semestral,
        'ventas_semestral': ventas_semestral,  

        'dias_semestral':dias_semestral,

    }
    return render(request, 'reporte_costos.html', context)

def agregar_producto_a_carrito(venta, cantidad,  base, altura, producto_precio, producto):

    if venta.estado == venta.ESTADO_CREADA:

        detalle_venta = DetalleVenta()

        detalle_venta.venta = venta
        detalle_venta.producto = producto
        detalle_venta.cantidad = cantidad
        detalle_venta.cantidad_producto = producto_precio.cantidad
        detalle_venta.unidad_de_medida = producto_precio.unidad_de_medida
        detalle_venta.precio = producto_precio.precio()
        detalle_venta.moneda = Configuracion.objects.first().Moneda

        if producto_precio.unidad_de_medida == 'Mt2s':
            detalle_venta.base = base
            detalle_venta.altura = altura

        detalle_venta.save()

        producto.save()

        return producto.nombre.capitalize() + ' se ha agregado al carrito de manera exitosa.'
    else:
        return 'False'

def eliminar_de_carrito(detalle_id):
    """
    En este método se encuentra la lógica de eliminar el DetalleProducto del 'Carrito'

    :param detalle_id:
    :return:
    """
    detalle_venta = DetalleVenta.objects.get(id=detalle_id)
    producto = detalle_venta.producto
    producto.save()
    detalle_venta.delete()
    return detalle_venta.producto.nombre

def vaciar_carrito(venta_id):
    """
    Método para vaciar por completo 'el carrito' de la venta actual, este método elimina todos los detalleventa que existan
    con la venta actual y devolverá a stock de cada producto los productos retirados de la venta

    Uso actual: Sin uso

    :param venta_id:
    :return:
    """
    venta = get_object_or_404(Venta, venta_id)
    for detalleventa in venta.detalleventa_set.all():
        eliminar_de_carrito(detalleventa.id)

def obtener_venta_actual(caja_usuario):
    """
    Método que retorna la venta actual, se pueden seguir realizando acciones en la venta hasta que la venta se encuentre
    en estado cancelada, finalizada o anulada
    :return Venta:
    """
    venta = Venta.objects.filter(estado=Venta.ESTADO_FACTURADA, nombre_factura=caja_usuario).first()
    if not venta:
        venta = Venta.objects.filter(estado=Venta.ESTADO_PAGADA, nombre_factura=caja_usuario).first()
    if not venta:
        # Si no existe una venta en estado creado, la creamos
        venta, create = Venta.objects.get_or_create(estado=Venta.ESTADO_CREADA, nombre_factura=caja_usuario)
        venta.save()

    if not venta.codigo:
        venta.codigo = str(venta.id)
        venta.save()

    return venta

def obtener_ultima_venta(caja_usuario):
    """
    Método que retorna la venta anterior
    :return Venta:
    """
    venta = Venta.objects.filter(estado=Venta.ESTADO_FINALIZADA, nombre_factura=caja_usuario).order_by('-id').first()

    return venta

def devolver_productos_a_stock(id_venta):
    venta = get_object_or_404(Venta, id=id_venta)

def calcular_conversion_cantidad(unidad_original, cantidad, unidad_conversion):
    if (unidad_original, unidad_conversion) not in FACTORES_CONVERSION:
        raise ValueError('Conversión no válida entre {} y {}'.format(unidad_original, unidad_conversion))

    # Calcular la conversión
    factor_conversion = FACTORES_CONVERSION[(unidad_original, unidad_conversion)]
    cantidad_convertida = cantidad * factor_conversion

    return cantidad_convertida

def carta_01_qr(request):

    configuracion = Configuracion.objects.first()

    lista_productos = Producto.objects.exclude(habilitar_venta=False) \
                                    .filter(productoprecio__isnull=False) \
                                    .order_by('nombre')

    context = {
        'configuracion':configuracion,
        'productos': lista_productos,
    }

    return render(request, 'carta_01_qr.html', context)
    
def generar_ticket(request, pago_id):
    from django.utils import timezone

    # Obtén el objeto de PagosClientes
    pago = PagosClientes.objects.get(id=pago_id)

    # Crea un objeto HttpResponse con el tipo de contenido PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{pago_id}.pdf"'

    # Calcula el número de ventas para ajustar el tamaño del lienzo
    pagos_info = pago.obtener_pagos()
    num_ventas = len(pagos_info)
    base_height = 105  # Altura base en mm
    extra_height_per_venta = 16  # Altura extra por cada venta en mm
    total_height = base_height + num_ventas * extra_height_per_venta

    # Crea el PDF con la altura calculada
    p = canvas.Canvas(response, pagesize=(80*mm, total_height*mm))  # 80mm de ancho y altura calculada

    y_position = total_height - 10  # Ajusta la posición inicial en función de la altura total

    # Añade el contenido al PDF
    p.setFont("Helvetica-Bold", 10)
    p.drawString(10, y_position*mm, f'CANCELACION DE C. CORRIENTES')
    p.setFont("Helvetica", 10)
    y_position -= 10
    p.drawString(10, y_position*mm, f'Fecha: {pago.fecha}')
    y_position -= 5
    p.drawString(10, y_position*mm, f'Cliente: {pago.cliente}')
    y_position -= 5
    p.drawString(10, y_position*mm, f'______________________________________')
    y_position -= 7

    for i, (venta, pago_real, pago_actualizado) in enumerate(pagos_info):
        p.setFont("Helvetica-Bold", 10)
        p.drawString(10, y_position*mm, f'Venta {venta}')
        p.setFont("Helvetica", 10)
        y_position -= 5
        p.drawString(10, y_position*mm, f'    Original ${pago_real:,.2f}')
        y_position -= 5
        p.drawString(10, y_position*mm, f'    Actualizado: ${pago_actualizado:,.2f}')
        y_position -= 5

    y_position -= 5
    p.drawString(10, y_position*mm, f'______________________________________')
    y_position -= 8

    p.setFont("Helvetica-Bold", 11)
    p.drawString(10, y_position*mm, f'Total: ${pago.seleccionado_actualizado():,.2f}')
    y_position -= 10
    p.drawString(10, y_position*mm, f'Recibimos los pagos:')
    y_position -= 5 
    p.drawString(10, y_position*mm, f'{pago.medio_de_pago.Nombre} : $ {pago.total:,.2f}')

    y_position -= 5
    p.drawString(10, y_position*mm, f'______________________________________')
    y_position -= 8
    p.setFont("Helvetica-Bold", 11)

    if pago.estado:
        y_position -= 10
        p.drawString(10, y_position*mm, f'Su cuenta corriente actual es:')
        y_position -= 5 
        p.drawString(10, y_position*mm, f' ${pago.cliente.cuenta_corriente():,.2f}')

    y_position -= 10


    p.showPage()
    p.save()

    return response

