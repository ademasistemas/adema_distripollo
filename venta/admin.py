from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from agenda.models import Configuracion
from .forms import PagosClientesForm
from venta.models import Venta, DetalleVenta,VentaEntrega,GastoEntrega,PagosVentas,PagosClientes, ProductoCompuestoVendido, ProductosIncluidosVendidos
from import_export.admin import ImportExportModelAdmin
from django.utils.translation import gettext_lazy as _
from .presupuesto import generar_presupuesto_a4

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ('producto', 'cantidad','unidad_de_medida','precio_unitario','subtotal')
    fields = ('producto', 'cantidad','unidad_de_medida','precio_unitario','subtotal')

    def precio_unitario(self, obj):
        moneda=Configuracion.objects.first().Moneda
        return f'{moneda} {obj.precio:,.2f}'

    def subtotal(self, obj):
        moneda=Configuracion.objects.first().Moneda
        return f'{moneda} {obj.get_total:,.2f}'
    
    def has_add_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de añadir nuevas ventas desde el admin de Cliente

    def has_change_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de editar ventas desde el admin de Cliente

    def has_delete_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de eliminar ventas desde el admin de Cliente

class PagosVentaInline(admin.TabularInline):
    model = PagosVentas
    extra = 0
    readonly_fields = ('fecha','medio_de_pago', 'total_pago',)
    fields = ('fecha','medio_de_pago', 'total_pago',)
    
    def total_pago(self, obj):
        moneda=Configuracion.objects.first().Moneda
        return f'{moneda} {obj.total:,.2f}'
    
    def has_add_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de añadir nuevas ventas desde el admin de Cliente

    def has_change_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de editar ventas desde el admin de Cliente

    # def has_delete_permission(self, request, obj=None):
    #     return False  # Desactivar la capacidad de eliminar ventas desde el admin de Cliente

def Entregar(modeladmin, request, queryset):

    for venta in queryset:
        if venta.entregado == False:
            venta.entregado = True
            venta.save()
        else:
            messages.warning(request, f"La venta ya se encuentra entregada.")

@admin.register(DetalleVenta)
class DetalleVentaAdmin(ImportExportModelAdmin):
    list_display = ('fecha','venta','producto','Cantidad','precio_unitario','total','ganancias_estimadas','costo_total')
    list_filter = ('fecha','venta','producto',)
    exclude =('precio','base','altuyra',)
    readonly_fields =  ('fecha','venta','producto','cantidad','moneda','precio_unitario','total', 'unidad_de_medida', 'cantidad_producto')
    list_per_page = 20
    
    def Cantidad(self,obj):
        txt = f'{round(obj.cantidad,0)} Unid'
        return txt
    
    def precio_unitario(self, obj):
        return "💲{:,.2f}".format(obj.precio)

    def total(self, obj):
        return "💲{:,.2f}".format(obj.get_total)

    def has_add_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de añadir nuevas ventas desde el admin de Cliente

    def has_change_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de editar ventas desde el admin de Cliente

    # def has_delete_permission(self, request, obj=None):
    #     return False  # Desactivar la capacidad de eliminar ventas desde el admin de Cliente

@admin.register(Venta)
class VentaAdmin(ImportExportModelAdmin):
    list_display = ('codigo','fecha','cajero','cliente_','total_factura','entregado','ESTADO')
    readonly_fields = ('codigo','fecha','cajero','cliente_','total_factura','entregado','ESTADO')
    list_filter = ('estado','cliente',)
    date_hierarchy = 'fecha'
    exclude = ('nit','nombre_factura','total','vendedor','razon_cancelacion','ESTADO','total_entrega','estado')
    actions = [Entregar]
    inlines = [DetalleVentaInline,PagosVentaInline,]
    list_per_page = 15

    def cliente_(self,obj):
        if not obj.cliente:
            return f'Sin Cliente'
        else:
            return f'{obj.cliente}'
    
    def get_queryset(self, request):
        """
        Modifica el queryset predeterminado para excluir las ventas con estado 'creada' (estado=0),
        excepto cuando se aplica un filtro específico.
        """
        qs = super().get_queryset(request)
        
        # Si no hay filtros aplicados, excluir los movimientos con estado 'creada'
        if not request.GET:  
            return qs.exclude(estado=self.model.ESTADO_CREADA)
        return qs

    def ESTADO(self,obj):

        if obj.estado == 0:
            msj = f'🟡creada'
        elif obj.estado == 1:
            msj = f'💲pagada'
        elif obj.estado == 2:
            msj = f'💳pagada'
        elif obj.estado == 3:
            msj = f'🟢finalizada'
        elif obj.estado == 4:
            msj = f'🔴cancelada'
        else:
            msj = f'🔴anulada'

        return msj
    
    def cajero(self, obj):

        return obj.nombre_factura

    def total_factura(self, obj):
        moneda=Configuracion.objects.first().Moneda
        if obj.total is not None:
            return f'{moneda} {obj.total:,.2f}'
        else:
            return "N/A"

    def has_add_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de añadir nuevas ventas desde el admin de Cliente

    def has_change_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de editar ventas desde el admin de Cliente

    # def has_delete_permission(self, request, obj=None):
    #     return False  # Desactivar la capacidad de eliminar ventas desde el admin de Cliente

class GastoEntregaInline(admin.TabularInline):
    model = GastoEntrega
    extra = 1
    fields = ('gasto', 'total')

class VentaEntregaInline(admin.StackedInline):
    model = VentaEntrega
    extra = 1
    fields = ('venta',)
    readonly_fields = ('cliente', 'total',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'venta':
            kwargs['queryset'] = Venta.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        fields += ['cliente', 'total']
        return fields

    def cliente(self, obj):
        return obj.venta.cliente.nombre if obj.venta.cliente else 'N/A'

    def total(self, obj):
        return "💲{:,.2f}".format(obj.venta.total) if obj.venta.total is not None else 'N/A'

class CobradoFilter(admin.SimpleListFilter):
    title = _('estado de cobro')  # or use 'Cobrado'
    parameter_name = 'cobrado'
    
    def lookups(self, request, model_admin):
        # Define las opciones que se mostrarán en el filtro.
        return (
            ('Cobrado', _('Cobrado')),
            ('Pendiente de Cobro', _('Pendiente de Cobro')),
        )

    def queryset(self, request, queryset):
        # Modifica el queryset basado en el valor seleccionado por el usuario.
        if self.value() == 'Cobrado':
            return queryset.filter(cancelado=True)#.exclude(medio_de_pago__cuenta_corriente=True)
        if self.value() == 'Pendiente de Cobro':
            return queryset.filter(cancelado=False,medio_de_pago__cuenta_corriente=True)

class ProductosIncluidosVendidosInline(admin.TabularInline):
    model = ProductosIncluidosVendidos
    extra = 0
    readonly_fields = ('cantidad_receta','cantidad_vendida','Costo_unitario' , 'Costo_total')
    exclude = ('receta_producto','costo_unitario','unidad_de_medida','cantidad')

    def cantidad_vendida(self, obj):
        cantidad = obj.cantidad
        return f'{cantidad:,.2f} {obj.unidad_de_medida}'
    
    def cantidad_receta(self, obj):
        if obj.receta_producto is not None:
            return f'{obj.receta_producto}'
        else:
            return "N/A"
        
    def Costo_unitario(self, obj):
        if obj.costo_unitario is not None:
            moneda = Configuracion.objects.first().Moneda
            return f'{moneda} {obj.costo_unitario:,.2f}'
        else:
            return "N/A"

    def Costo_total(self, obj):
        if obj.costo_total() is not None:
            moneda = Configuracion.objects.first().Moneda
            return f'{moneda} {obj.costo_total():,.2f}'
        else:
            return "N/A"

class ProductoCompuestoVendidoAdmin(admin.ModelAdmin):
    inlines = [ProductosIncluidosVendidosInline]
    list_display = ('venta', 'producto_compuesto', 'cantidad')

    def has_add_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de añadir nuevas ventas desde el admin de Cliente

    def has_change_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de editar ventas desde el admin de Cliente


admin.site.register(ProductoCompuestoVendido, ProductoCompuestoVendidoAdmin)


@admin.register(PagosVentas)
class PagosVentasAdmin(ImportExportModelAdmin):
    list_display = ('venta','total_venta','Cliente','medio_de_pago','Total','Cobrado')
    readonly_fields = ('venta','total_venta','Cliente','medio_de_pago','Total','Cobrado')
    list_filter = ('venta__cliente', 'medio_de_pago', CobradoFilter)
    exclude = ('cliente','total','cancelado','adicional_cc')
    list_per_page = 20

    def total_venta(self,obj):
        total = float(obj.get_total)
        moneda=Configuracion.objects.first().Moneda
        return f'{moneda} {total:,.2f}'
    #total_venta.admin_order_field = 'get_total'

    def Cobrado(self,obj):
        if obj.medio_de_pago.cuenta_corriente:

            if obj.cancelado:
                return f'Cobrado'
            else:
                return f'Pendiente de Cobro'
        else:
            return f'Cobrado'
        
    def Cliente(self,obj):
        cliente = obj.cliente
        if cliente:
            return f'{cliente}'
        else:
            return 'Cons. Final'
    Cliente.admin_order_field = 'venta__cliente'

    def Total(self, obj):
        moneda=Configuracion.objects.first().Moneda
        return f'{moneda} {obj.total:,.2f}'
    Total.admin_order_field = 'total'

    def has_add_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de añadir nuevas ventas desde el admin de Cliente

    def has_change_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de editar ventas desde el admin de Cliente

    # def has_delete_permission(self, request, obj=None):
    #     return False  # Desactivar la capacidad de eliminar ventas desde el admin de Cliente

@admin.register(PagosClientes)
class PagosClientesAdmin(ImportExportModelAdmin):
    form = PagosClientesForm
    list_display = ('fecha','cliente','Deuda_real','seleccionado','Total_pago','estado','descargar')
    readonly_fields = ('seleccionado','descargar')
    exclude = ('estado',)
    list_filter = ('cliente',)
    list_per_page = 20
      
    def seleccionado(self, obj):
        moneda=Configuracion.objects.first().Moneda
        if obj.tomar_actualizado:
            return f'{moneda} {obj.seleccionado_actualizado():,.2f}'
        else:
            return f'{moneda} {obj.seleccionado():,.2f}'

    def Deuda_real(self, obj):
        valor=obj.deuda_actual() or 0
        return valor

    def Total_pago(self, obj):
        moneda=Configuracion.objects.first().Moneda
        valor=obj.total or 0
        return f'{moneda} {valor:,.2f}'
    
    def descargar(self,obj):
        return format_html(
            '<a class="btn btn-primary" href="/generar_ticket/{}/">Descargar</a>', 
            obj.id
        )
    
    def confirmar(modeladmin, request, queryset):
        # Validación para que seleccione solo 1 queryset
        if len(queryset) != 1:
            messages.error(request, "Seleccione 1 pago a la vez.")
            return
        
        pago_cliente = queryset[0]
        total = round(float(pago_cliente.total),2)
        real = float(pago_cliente.seleccionado())
        actualizado = float(pago_cliente.seleccionado_actualizado())
        diferencia = actualizado - real

        if pago_cliente.tomar_actualizado:
            seleccionado = round(actualizado,2)
        else:
            seleccionado = round(real,2)

        if total != seleccionado:
            messages.error(request, "El total seleccionado no coincide con el total pagado.")
            return

        if not pago_cliente.estado:
            pagos_ventas = pago_cliente.pagos_ventas.all()
            for pago in pagos_ventas:
                pago.cancelado = True
                pago.save()

            if diferencia != 0:
                diferencia_por_actualizacion = PagosVentas.objects.create(
                    cliente=pago_cliente.cliente,
                    medio_de_pago=pago_cliente.medio_de_pago,
                    total=diferencia,
                    cancelado=True,
                    adicional_cc=True,
                )
                diferencia_por_actualizacion.save()

            pago_cliente.estado = True
            pago_cliente.save()
            messages.success(request, "El pago se confirmó correctamente y las ventas seleccionadas se han marcado como canceladas.")
        else:
            messages.warning(request, "Este pago ya ha sido confirmado.")

    confirmar.short_description = "Confirmar Pago y Cancelar Ventas Seleccionadas"
    actions = [confirmar,]


