from django.contrib import admin
from compra.models import Compra,detalleCompra,medioDePagoCompra,FleteCompra,PagosProveedores
from compra.views import pagar_deuda_proveedores
from producto.models import Producto
from django.db.models import Sum
from agenda.models import Configuracion
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import ValidationError
from import_export.admin import ImportExportModelAdmin
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.urls import path
from .models import PagosProveedores
from .forms import PagosProveedoresForm


@admin.register(medioDePagoCompra)
class medioDePagoAdmin(ImportExportModelAdmin):
    list_display = ('id', 'Fecha', 'Proveedor', 'Cuenta', 'total', 'Estado_de_pago', )#'Pagar'
    list_filter = ('id','Compra__proveedor', 'Cuenta', 'cancelado' )
    readonly_fields = ('Compra', 'Cuenta', 'total', 'Estado_de_pago')
    exclude = ('Total', 'cancelado')

    def Estado_de_pago(self, obj):
        estado = obj.Cuenta.cuenta_corriente
        if estado == True:
            if obj.cancelado:
                return "🟢 Pago Realizado"
            else:
                return "🔴 Pago Pendiente"
        else:
            return "🟢 Pago Realizado"

    def Fecha(self, obj):
        return obj.Compra.fecha

    def Proveedor(self, obj):
        return obj.Compra.proveedor

    def total(self, obj):
        moneda = Configuracion.objects.first()
        if obj.Total:
            return str(moneda.Moneda) + str(" {:,.2f}".format(obj.Total))
        else:
            return str(moneda.Moneda) + str(" {:,.2f}".format(0))

    def Pagar(self, obj):
        if obj.cancelado == True:
            return "🟢 Pago Realizado"
        else:
            return format_html('<a class="btn btn-danger" href="{}">Pagar deuda</a>', reverse('admin:pagar_deuda_proveedores', args=[obj.id]))
    Pagar.short_description = "Pagar"

    def has_add_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de añadir nuevas ventas desde el admin de Cliente

    def has_change_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de editar ventas desde el admin de Cliente

    # def has_delete_permission(self, request, obj=None):
    #     return False  # Desactivar la capacidad de eliminar ventas desde el admin de Cliente

class articulosCompraInline(admin.StackedInline):
    model = detalleCompra
    extra = 1
    list_per_page = 15
    fields = ('producto', 'Cantidad','unidad_de_medida', 'Precio','Descuento','subtotal','ActualizarCosto','Cantidad_comprada','ultimo_costo_unitario','contexto')
    readonly_fields = ('subtotal','Cantidad_comprada','ultimo_costo_unitario','contexto')

    def Cantidad_comprada(self, obj):
        return f'{obj.Cantidad:,.2f} {obj.unidad_de_medida}'

    def ultimo_costo_unitario(self, obj):
        config = Configuracion.objects.first()
        moneda = config.Moneda
        if obj.unidad_de_medida_producto == obj.unidad_de_medida:
            precio = round(obj.producto.costo_unitario(),2)
        else:
            if obj.unidad_de_medida_producto == "Kilos" or obj.unidad_de_medida_producto == "Litros":
                precio = round(obj.producto.costo_unitario() / 1000,2)
            else:
                precio = round(obj.producto.costo_unitario() * 1000,2)

        return f'{moneda.Abreviacion} {precio:,.2f} x {obj.unidades_producto:,.2f} {obj.unidad_de_medida_producto}'


    def subtotal(self, obj):
        config = Configuracion.objects.first()
        moneda = config.Moneda
        precio = obj.Total
        return str(moneda.Abreviacion) + str(" {:,.2f}".format(precio))
    
    def contexto(self,obj):
        return f'{obj.contexto()}'


class MedioDePagoInline(admin.TabularInline):
    model = medioDePagoCompra
    extra = 1
    fields = ('Cuenta','Total')

# class FleteCompraInline(admin.TabularInline):
#     model = FleteCompra
#     extra = 1
#     fields = ('importe',)

@admin.register(Compra)
class CompraAdmin(ImportExportModelAdmin):
    list_display = ('id','Status','fecha','proveedor', 'total_compra',)#'medio_de_pago',
    exclude = ('total', 'estado','compra_inicial','Deposito')
    inlines = [articulosCompraInline,MedioDePagoInline,]#FleteCompraInline
    list_filter = ('id','proveedor',)
    search_fields = ('proveedor__NombreApellido','proveedor__Empresa',)
    readonly_fields = ('total_compra',)
    list_per_page = 20

    def total_compra(self, obj):
        config = Configuracion.objects.first()
        moneda = config.Moneda
        precio = detalleCompra.objects.filter(Compra=obj).aggregate(Sum('Total'))
        flete = FleteCompra.objects.filter(compra=obj).aggregate(Sum('importe'))

        # Usamos 'or 0' para asegurar que el valor no sea None
        total_sum = float(precio['Total__sum'] or 0)
        total_flete = float(flete['importe__sum'] or 0)

        total_sum += total_flete

        if total_sum is not None:
            return str(moneda.Abreviacion) + str(" {:,.2f}".format(total_sum))
        else:
            return "N/A"  # O cualquier otro valor predeterminado que desees mostrar si el total es None
    
    
    def Status(self, obj):
        check_pagos = obj.validar_compra()

        if obj.estado == False:
            if check_pagos == True:
                msg = "🟠 Pendiente Ingreso"
            else:
                msg = "🔴 Verificar pagos"
        else:
            msg = "🟢 Compra Aprobada"

        return msg

    def clean(self):
        if self.estado == True:
            raise ValidationError("Este producto ya fue controlado. No se puede modificar.")
        super().clean()

    def save(self, *args, **kwargs):
        super(Compra, self).save(*args, **kwargs)

    def ingresar_compra(self, request, queryset):
        
        for compra in queryset:
            if  compra.estado == False:
                if compra.validar_compra() == False: #validar los pagos coincidentes
                    if compra.compra_inicial == False:
                        error_message = f"Debe verificar los pagos de la compra #{compra.pk}"
                        messages.error(request, error_message)
                        return HttpResponseRedirect(
                            reverse("admin:%s_%s_change" % (compra._meta.app_label,  compra._meta.model_name),
                                    args=[compra.pk])
                        )
                    else:
                        # productos = detalleCompra.objects.filter(Compra=compra)
                        # for producto in productos:
                        #     producto.Precio = 0

                        compra.estado = True
                        compra.save()
                        message = f"Ingreso de mercaderias incial correcto."
                        messages.success(request, message)
                else:
             
                    productos = detalleCompra.objects.filter(Compra=compra)

                    for producto in productos:
                        if producto.ActualizarCosto:
                            costo =  producto.costo_unitario()
                            item = Producto.objects.filter(id=producto.producto.pk).first()
                            item.costo = float(costo) * float(item.cantidad)
                            item.save()


                    compra.estado = True
                    compra.save()
                    message = f"La compra se ingresó correctamente. Numero de compra: #{compra.pk}"
                    messages.success(request, message)
        

    ingresar_compra.short_description = "Confirmar compra"
    actions = [ingresar_compra] 

@admin.register(detalleCompra)
class DetalleCompraAdmin(ImportExportModelAdmin):
    list_display = ('Fecha','Compra','producto','Cantidad','precio_unitario','subtotal','cotizacion_actual',)
    readonly_fields = ('Fecha','Compra','producto','Cantidad','Precio','Descuento','Total')
    list_filter = ('Fecha','Compra','producto',)
    list_per_page = 30
    exclude=('precio','Deposito',)

    def precio_unitario(self, obj):
        config = Configuracion.objects.first()
        moneda = config.Moneda
        precio = obj.Precio
        return str(moneda.Abreviacion) + str(" {:,.2f}".format(precio))

    def cotizacion_actual(self, obj):
        config = Configuracion.objects.first()
        moneda = config.Moneda_secundaria
        precio = obj.Precio / config.tipo_cambio
        return str(moneda.Abreviacion) + str(" {:,.2f}".format(precio))

    def subtotal(self, obj):
        config = Configuracion.objects.first()
        moneda = config.Moneda
        precio = obj.Precio * obj.Cantidad
        return str(moneda.Abreviacion) + str(" {:,.2f}".format(precio))

    def has_add_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de añadir nuevas ventas desde el admin de Cliente

    def has_change_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de editar ventas desde el admin de Cliente

    # def has_delete_permission(self, request, obj=None):
    #     return False  # Desactivar la capacidad de eliminar ventas desde el admin de Cliente

@admin.register(PagosProveedores)
class PagosProveedoresAdmin(admin.ModelAdmin):
    form = PagosProveedoresForm
    list_display = ('id','fecha', 'proveedor', 'medio_de_pago', 'total_','total_seleccionado')
    list_filter = ('id','proveedor', 'medio_de_pago',)
    readonly_fields = ('total_seleccionado',)
    actions = ['autorizar_pagos',]
    exclude = ('estado',)

    def autorizar_pagos(self, request, queryset):
        for pago in queryset:
            if not pago.estado:
                total_seleccionado = pago.seleccionado()
                if total_seleccionado != pago.total:
                    messages.error(request, f'El total seleccionado (${total_seleccionado:,.2f}) no coincide con el total pagado (${pago.total:,.2f}) para el pago #{pago.id}.')
                else:
                    pago.autorizar_pago()
                    messages.success(request, f'El pago #{pago.id} ha sido autorizado y los pagos pendientes han sido cancelados.')
            else:
                messages.warning(request, f'El pago #{pago.id} ya estaba autorizado.')
    autorizar_pagos.short_description = "Autorizar pagos seleccionados"

    def total_(self,obj):

        return f'$ {obj.total:,.2f}'
    
    def total_seleccionado(self,obj):

        return f'$ {obj.seleccionado():,.2f}'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('pagar_deuda_proveedores/<int:id_pago>/', self.admin_site.admin_view(self.pagar_deuda_proveedores_view), name='pagar_deuda_proveedores')
        ]
        return custom_urls + urls

    def pagar_deuda_proveedores_view(self, request, id_pago):
        return pagar_deuda_proveedores(request, id_pago)



