from django.contrib import admin
from django import forms
from .models import AjusteVenta, AjusteDetalleVenta, AjustePagosVenta
from venta.models import Venta
from django.urls import reverse
from django.utils.html import format_html

class AjusteDetalleVentaInline(admin.TabularInline):
    model = AjusteDetalleVenta
    extra = 0
    can_delete = True  # Permite eliminar items
    readonly_fields = (
        'producto',
        'cantidad',
        'cantidad_producto',
        'unidad_de_medida',
        'precio',
        'base',
        'altura',
    )
    # Impide agregar o modificar (solo se permite la eliminación)
    def has_add_permission(self, request, obj):
        return False
    def has_change_permission(self, request, obj=None):
        return False

class AjustePagosVentaInline(admin.TabularInline):
    model = AjustePagosVenta
    extra = 0

class AjusteVentaForm(forms.ModelForm):
    class Meta:
        model = AjusteVenta
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(AjusteVentaForm, self).__init__(*args, **kwargs)
        # Permitir seleccionar solo ventas ajustables (no canceladas ni anuladas)
        self.fields['venta'].queryset = Venta.objects.exclude(estado__in=[Venta.ESTADO_CANCELADA, Venta.ESTADO_ANULADA])

@admin.register(AjusteVenta)
class AjusteVentaAdmin(admin.ModelAdmin):
    form = AjusteVentaForm
    inlines = [AjusteDetalleVentaInline, AjustePagosVentaInline]
    list_display = ('id', 'venta', 'nueva_fecha', 'caja', 'nuevo_total', 'total_pagos', 'estado_validacion')
    readonly_fields = ('venta_info', 'estado_validacion', 'nuevo_total')

    fieldsets = (
        ('Venta', {
            'fields': ('venta', 'venta_info', 'nueva_fecha', 'caja', 'nuevo_total')
        }),
    )

    def venta_info(self, obj):
        from agenda.models import Caja  # Importar aquí para evitar problemas de import circular
        if obj.venta:
            # Se intenta obtener el cajero: se prioriza el valor de nombre_factura, sino se usa vendedor.
            cajero = obj.venta.nombre_factura or obj.venta.vendedor or "N/A"
            # Buscar en el modelo Caja un registro cuyo Nombre coincida (ignorando mayúsculas/minúsculas)
            caja_obj = Caja.objects.filter(Nombre__iexact=cajero).first()
            if caja_obj:
                cajero = caja_obj.Nombre
            return format_html(
               "<b>Fecha original:</b> {}<br><b>Cliente:</b> {}<br><b>Cajero:</b> {}<br><b>Total original:</b> {}",
                obj.venta.fecha,
                obj.venta.cliente,
                cajero,
                f'{obj.venta.total:,.2f}'
            )
        return ""

    venta_info.short_description = "Información de la Venta"

    def estado_validacion(self, obj):
        """
        Muestra en rojo 'Verificar pagos' si el total de pagos no coincide con el nuevo_total;
        de lo contrario muestra un botón 'Confirmar' que redirige a la URL para confirmar.
        """ 
        if obj.confirmado == False:
            if obj.nuevo_total != obj.total_pagos():
                return format_html('<span style="color:red;">Verificar pagos</span>')
            else:
                url = reverse('ajustes:confirmar-ajuste-venta', args=[obj.id])
                return format_html('<a class="btn btn-danger" style="border-radius:5px" href="{}">Confirmar</a>', url)
        else:
            return format_html('<span style="color:green;">🌿 Confirmado</span>')
                
        

    estado_validacion.short_description = "Validación de Totales"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Al crear un nuevo ajuste, copiar automáticamente los items y pagos de la venta
        if not change:
            obj.copiar_datos_venta()
