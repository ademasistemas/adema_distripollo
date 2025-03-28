from django.contrib import admin
from .models import ReporteCaja,ReporteMensual
from agenda.models import Configuracion
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin, messages

@admin.action(description="Actualizar")
def Actualizar(modeladmin, request, queryset):

    if len(queryset) != 1:
        messages.error(request, "Se puede actualizar de a 1 balance a la vez")
        return
    
    for query in queryset:
        query.save()

    messages.success(request, f"{query} Actualizado")


@admin.register(ReporteCaja)
class ReporteCajaAdmin(ImportExportModelAdmin):
    list_display = ('fecha', 'caja','ventas_cobradas_efectivo','ventas_cobradas_virtuales','ventas_en_cuenta_corriente','cierre')
    readonly_fields = (
        'ventas_cobradas_efectivo',
        'ventas_cobradas_virtuales',
        'ventas_en_cuenta_corriente',
        'total_general_ventas',

        'compras_en_efectivo',
        'compras_en_virtuales',
        'compras_en_cuenta_corriente',
        'total_general_compras',

        'Pagado_a_proveedores_efectivo',
        'Pagado_a_proveedores_otros',
        'cobrado_a_clientes_efectivo',
        'cobrado_a_clientes_otros',
        'cierre'
        )
    list_filter = ('caja',)

    exclude = (
        'estado',
        'total_ventas_efectivo',
        'total_ventas_virtuales',
        'total_ventas_cc',
        'total_ventas',

        'total_compras_efectivo',
        'total_compras_virtuales',
        'total_compras_cc',
        'total_compras',

        'cobrado_clientes_efectivo',
        'cobrado_clientes_otros',
        'pagado_proveedores_efectivo',
        'pagado_proveedores_otros',
        'total_ventas_cobradas',
        )

    def Pagado_a_proveedores_efectivo(self,obj):
        config = Configuracion.objects.first()
        moneda = config.Moneda.Abreviacion
        return f'{moneda} {obj.pagado_proveedores_efectivo:,.2f}'
    
    def Pagado_a_proveedores_otros(self,obj):
        config = Configuracion.objects.first()
        moneda = config.Moneda.Abreviacion
        return f'{moneda} {obj.pagado_proveedores_otros:,.2f}'

    def cobrado_a_clientes_efectivo(self,obj):
        config = Configuracion.objects.first()
        moneda = config.Moneda.Abreviacion
        return f'{moneda} {obj.cobrado_clientes_efectivo:,.2f}'
    
    def cobrado_a_clientes_otros(self,obj):
        config = Configuracion.objects.first()
        moneda = config.Moneda.Abreviacion
        return f'{moneda} {obj.cobrado_clientes_otros:,.2f}'
    
    def ventas_cobradas_efectivo(self,obj):
        config = Configuracion.objects.first()
        moneda = config.Moneda.Abreviacion
        return f'{moneda} {obj.total_ventas_efectivo:,.2f}'

    def ventas_cobradas_virtuales(self,obj):
        config = Configuracion.objects.first()
        moneda = config.Moneda.Abreviacion
        return f'{moneda} {obj.total_ventas_virtuales:,.2f}'
    
    def ventas_en_cuenta_corriente(self,obj):
        config = Configuracion.objects.first()
        moneda = config.Moneda.Abreviacion
        return f'{moneda} {obj.total_ventas_cc:,.2f}'
    
    def total_general_ventas(self,obj):
        config = Configuracion.objects.first()
        moneda = config.Moneda.Abreviacion
        return f'{moneda} {obj.total_ventas:,.2f}'


    def compras_en_efectivo(self,obj):
        config = Configuracion.objects.first()
        moneda = config.Moneda.Abreviacion
        return f'{moneda} {obj.total_compras_efectivo:,.2f}'

    def compras_en_virtuales(self,obj):
        config = Configuracion.objects.first()
        moneda = config.Moneda.Abreviacion
        return f'{moneda} {obj.total_compras_virtuales:,.2f}'
    
    def compras_en_cuenta_corriente(self,obj):
        config = Configuracion.objects.first()
        moneda = config.Moneda.Abreviacion
        return f'{moneda} {obj.total_compras_cc:,.2f}'
    
    def total_general_compras(self,obj):
        config = Configuracion.objects.first()
        moneda = config.Moneda.Abreviacion
        return f'{moneda} {obj.total_compras:,.2f}'
    

    def cierre(self,obj):
        importe=round(float(obj.resultado()) or 0, 2)
        if importe < 0:
            return f'Sobrante de caja por: {float(-1) * float(importe):,.2f}'
        elif importe == 0:
            return f'Cierre sin diferencias.'
        else:
             return f'Faltante de caja por: {float(importe):,.2f}'
        
@admin.register(ReporteMensual)
class ReporteMensualAdmin(ImportExportModelAdmin):
    list_display = ('fecha','caja_final','deuda_clientes_final','deuda_proveedores_final')
    exclude = ('estado',)
    actions = [Actualizar,]
    readonly_fields = (
        'caja_anterior',
        'deuda_clientes_anterior',
        'deuda_proveedores_anterior',
        'total_ventas',
        'caja_final',
        'deuda_clientes_final',
        'deuda_proveedores_final',
    )

