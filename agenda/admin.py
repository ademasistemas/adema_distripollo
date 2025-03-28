from django.utils.timezone import localtime
from django.contrib import admin
from .models import *
from django.db.models import Sum
from venta.models import PagosVentas,Venta
from import_export.admin import ImportExportModelAdmin
from django.utils.html import format_html
from django.urls import reverse


class VentaInline(admin.TabularInline):  # O puedes usar admin.StackedInline para un diseño diferente
    model = Venta
    extra = 0  # No agregar filas extra para nuevas ventas, ya que solo queremos mostrar las existentes
    can_delete = False  # Desactivar la opción de eliminar ventas desde aquí
    list_display = ('Fecha_compra', 'codigo', 'total_pago', 'estado', )
    readonly_fields = ('Fecha_compra', 'codigo', 'total_pago', 'estado',)
    exclude = ('total','vendedor','nit','total_entrega','entregado','fecha','razon_cancelacion')
  # Asegúrate de incluir aquí todos los campos que quieres mostrar
    max_num = 0  # Prevenir la adición de nuevas ventas desde este inline
    show_change_link = True  # Opcional: si quieres permitir que el usuario haga clic en una venta para verla/editarla en detalle
    
    def Fecha_compra(self, obj):
        # Asegúrate de que obj.fecha no es None
        if obj.fecha:
            # Si estás utilizando timezone-aware datetimes, convierte a la zona horaria local antes de formatear
            fecha_local = localtime(obj.fecha)
            return fecha_local.strftime("%d/%m - %H:%M")
        else:
            return ""
    
    def total_pago(self, obj):
        if obj.total:
            return f'$ {" {:,.2f}".format(obj.total)}'
        else:
            return 0
    
    def has_add_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de añadir nuevas ventas desde el admin de Cliente

    def has_change_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de editar ventas desde el admin de Cliente

    def has_delete_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de eliminar ventas desde el admin de Cliente

class CuentaCorrienteInline(admin.TabularInline):
    model = PagosVentas
    extra = 0
    can_delete = False
    readonly_fields = ('fecha','medio_de_pago', 'deuda_real','deuda_actualizada',)#'Pagar_neto','Pagar_actualizado'
    exclude = ('venta','total','adicional_cc','cancelado')
    max_num = 0
    show_change_link = True

    verbose_name = "Pago"
    verbose_name_plural = "Pagos adeudados"

    def Pagar_neto(self, obj):
        return format_html('<a class="btn btn-primary" href="{}">Pagar deuda real</a>', reverse('pagar_deuda', args=[obj.id]))
    Pagar_neto.short_description = "Pagar_neto"

    def Pagar_actualizado(self, obj):
        return format_html('<a class="btn btn-primary" href="{}">Pagar deuda actualizada</a>', reverse('pagar_deuda_actualizada', args=[obj.id]))
    Pagar_actualizado.short_description = "Pagar_actualizado"

    def deuda_actualizada(self, obj):
        total=0
        porcentual= float(obj.venta.pagos_en_cuenta_corriente) /  float(obj.venta.get_cart_total)
        productos = obj.venta.detalleventa_set.all()
        for producto in productos:
            total += float(producto.get_total_actualizado) * float(porcentual)
        return f'$ {" {:,.2f}".format(total)}'
     
    def deuda_real(self, obj):
        return f'$ {" {:,.2f}".format(obj.total)}'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(medio_de_pago__cuenta_corriente=True,cancelado=False)#,cancelado=False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
# -----------------------------------------------------------------------------
# Vista proveedor
# 
@admin.register(Proveedor)
class ProveedorAdmin(ImportExportModelAdmin):
    list_display = ('Empresa', 'NombreApellido','Direccion', 'Email','Telefono',)
    list_filter = ('Empresa', 'NombreApellido','Direccion', 'Email','Telefono',)
    search_fields = ('Empresa', 'NombreApellido','Direccion', 'Email','Telefono',)
    ordering = ('Empresa',)



class AsignacionesCajaInline(admin.TabularInline): 
    model = Asignacion
    extra = 0 
    list_display = ('caja',)

@admin.register(Caja)
class CajaAdmin(ImportExportModelAdmin):
    list_display = ('Nombre',)
    inlines = [AsignacionesCajaInline]
    
# @admin.register(PrecioPorKilometro)
# class PrecioPorKilometroAdmin(ImportExportModelAdmin):
#     list_display = ('total',)

@admin.register(Cliente)
class ClienteAdmin(ImportExportModelAdmin):
    list_display = ('nombre','telefono','cuenta_corriente',)
    list_display_links = ('nombre',)
    search_fields = ('nombre',)
    list_filter = ('codigo','nombre',)

    inlines = [VentaInline,CuentaCorrienteInline]# 

    def cuenta_corriente(self, obj):

        total_deuda = 0
        #total_pago = 0

        deudas = PagosVentas.objects.filter(cliente=obj, medio_de_pago__cuenta_corriente=True, cancelado=False)
        #pagos = PagosVentas.objects.filter(cliente=obj, medio_de_pago__cuenta_corriente=False)
        
        for deuda in deudas:
            if deuda.total > 0:
                total_deuda += deuda.total
     
        # for pago in pagos:
        #     if pago.total < 0:
        #         total_pago -= pago.total
                

        cuenta_corriente = total_deuda# - total_pago

        if cuenta_corriente > 0:
            return f'🔴 Debe $ {" {:,.2f}".format(cuenta_corriente)}'
        elif cuenta_corriente == 0:
            return f'🟢 Al dia'
        else:
            return f'🔵 A favor $ {" {:,.2f}".format(cuenta_corriente)}'
        

@admin.register(Configuracion)
class ConfiguracionAdmin(admin.ModelAdmin):
    list_display = ('nombre','vista_clasica','mostrar_foto','entrega',)
    exclude = (
        'mostrar_productos_cocina_ldp',
        'mostrar_productos_cocina_tienda',
        'ventas_mayoristas',
        'Moneda_secundaria',
        'tipo_cambio',
        'mostrar_cocina',
        )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True  

    def has_delete_permission(self, request, obj=None):
        return False 


# @admin.register(Asignacion)
# class AsignacionAdmin(admin.ModelAdmin):
#     list_display = ('usuario','caja',)

@admin.register(Monedas)
class MonedasAdmin(admin.ModelAdmin):
    list_display = ('Nombre','Abreviacion')

# @admin.register(Chofer)
# class ChoferAdmin(ImportExportModelAdmin):
#     list_display = ('nombre','vehiculo','patente')

@admin.register(Gasto)
class GastoAdmin(ImportExportModelAdmin):
    list_display = ('fecha','categoria','descripcion','Gasto_Total')
    list_filter = ('categoria',)

    def Gasto_Total(self, obj):
        config = Configuracion.objects.first()
        moneda = config.Moneda
        texto = f'({moneda.Abreviacion})' + str(" {:,.2f}".format(obj.total))
        return texto


@admin.register(TipoGasto)
class TipoGastoAdmin(ImportExportModelAdmin):
    list_display = ('descripcion',)


# @admin.register(deposito)
# class depositoAdmin(admin.ModelAdmin):
#     list_display = ('Nombre',)

# -----------------------------------------------------------------------------
# Vista Depositos
# 
@admin.register(medioDeCompra)
class medioDeCompraAdmin(admin.ModelAdmin):
    list_display = ('Nombre',)


# -----------------------------------------------------------------------------
# Vista Depositos
# 
@admin.register(medioDePago)
class medioDePagoAdmin(admin.ModelAdmin):
    list_display = ('Nombre',)

# -----------------------------------------------------------------------------
# Vista Depositos
# 
@admin.register(categoria)
class categoriaAdmin(ImportExportModelAdmin):
    list_display = ('Descripcion',)



