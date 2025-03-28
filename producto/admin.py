from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from agenda.models import Configuracion
from django.utils import timezone
from producto.models import Producto, Categoria,Merma,ProductoPrecio,RecetaProducto,SubCategoria

def calcular_precios(self, request, queryset):

    productos = Producto.objects.all()
    configuracion = Configuracion.objects.all().first()

    if configuracion:
        tipo_cambio = configuracion.tipo_cambio
    else:
        tipo_cambio = 1

    for producto in productos:
        
        if producto.costo > 0 and producto.rentabilidad > 0 and producto.rentabilidad < 100:

            producto.precio = ((producto.costo * tipo_cambio) / (100 - producto.rentabilidad)) * 100
            producto.precio_usd =( (producto.costo) / (100 - producto.rentabilidad) )* 100
        
        producto.save()

    self.message_user(request, f'Se calcularon los precios en dólares para todos los productos.')

class ProductoPrecioInline(admin.StackedInline):
    model = ProductoPrecio
    extra = 0
    readonly_fields =( 'total','costo_unitario','costo_total','utilidad')

    def utilidad(self, obj):
        """
        Devuelve el margen de utilidad calculado para mostrar en el inline.
        """
        return obj.margen_de_utilidad()      

    def costo_unitario(self, obj):
        """
        Devuelve el margen de utilidad calculado para mostrar en el inline.
        """
        moneda = Configuracion.objects.first().Moneda
        return f'{moneda} {obj.costo_unitario_actual():,.2f}'   

    def costo_total(self, obj):
        """
        Devuelve el margen de utilidad calculado para mostrar en el inline.
        """
        moneda = Configuracion.objects.first().Moneda
        return f'{moneda} {obj.costo_total_actual():,.2f}'   

    def total(self,obj):
        texto = f"$ {obj.precio():,.2f}"
        return texto         
    
    def get_fields(self, request, obj=None):
        """
        Modifica dinámicamente los campos que se muestran en el inline
        según la configuración actual.
        """
        config = Configuracion.objects.first()
        
        if config and config.precio_venta_automatico:
            # Mostrar rentabilidad si está habilitado el precio automático
            return ('cantidad', 'unidad_de_medida', 'costo_unitario','costo_total','rentabilidad', 'total')
        else:
            # Mostrar precio_manual si el precio automático está deshabilitado
            return ('cantidad', 'unidad_de_medida', 'costo_unitario','costo_total', 'precio_manual', 'total','utilidad')

class productoRecetaInline(admin.TabularInline):
    model = RecetaProducto
    extra = 1
    fk_name = 'producto_principal'
    fields = ('producto_usado','cantidad','unidad_de_medida',)#'total',
    readonly_fields = ('total',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('producto_usado')

    def total(self, obj):
        return f"{obj.Costo_calculado():,.2f}"

@admin.register(Categoria)
class CategoriaAdmin(ImportExportModelAdmin):
    list_display = ('nombre',)

@admin.register(SubCategoria)
class SubCategoriaAdmin(ImportExportModelAdmin):
    list_display = ('nombre',)


@admin.register(Merma)
class MermaAdmin(ImportExportModelAdmin):
    list_display = ('fecha','producto','cantidad','motivo',)

@admin.register(ProductoPrecio)
class ProductoPrecioAdmin(ImportExportModelAdmin):
    list_display = ('producto','Cantidad','unidad_de_medida','Rentabilidad',)

    def Cantidad(self,obj):
        texto = "{:,.2f}".format(obj.cantidad)
        return texto

    def Rentabilidad(self,obj):
        texto = f"% {obj.rentabilidad}"
        return texto

@admin.register(Producto)
class ProductoAdmin(ImportExportModelAdmin):
    list_display = ('CODIGO','Descripcion','categoria','costo_unit','Precio_venta','en_inventario')
    list_display_links = ('CODIGO','Descripcion','categoria','costo_unit','Precio_venta','en_inventario')
    list_filter = ('codigo','nombre','descripcion','marca','categoria','sub_categoria',)
    search_fields = ('codigo','nombre','descripcion','marca',)
    exclude = ('precio','precio_usd','Precio_2','en_stock','mostrar','habilitar_stock')
    inlines = [ProductoPrecioInline,]
    ordering = ('codigo',)

    def CODIGO(self, obj):
        return int(obj.codigo)

    # Solo muestra el inline si el producto es "compuesto"
    def get_inlines(self, request, obj=None):
        if obj and obj.tipo == 'Compuesto':
            return [ProductoPrecioInline,productoRecetaInline]
        else:
            return [ProductoPrecioInline]

    def get_readonly_fields(self, request, obj=None):
        # Si el producto es de tipo compuesto, ocultar `costo_ultimo_unitario`
        fields = ['costo_unit', 'Precio_venta', 'stock_actual',]
        if obj and obj.tipo == 'Compuesto':
            fields.append('costo')
        return fields
  
    def tipo(self, obj):
      
        if obj.unidad_de_medida == "Kilos" or obj.unidad_de_medida == "Gramos":
            icono= '⚖️'
        elif obj.unidad_de_medida == "Litros" or obj.unidad_de_medida == "Mililitros":
            icono= '🫗'
        elif obj.unidad_de_medida == "Mts":
            icono= 'Ⓜ️'
        else:
            icono= '📦'
        return icono
    
    def Descripcion(self,obj):
        if obj.nombre:
            name = str(obj.nombre).upper()
        else:
            name = "Sin nombre"
        return name

    def Vencimiento(self, obj):
        if obj.stock_actual() > 0 and obj.vencimiento:
            # Calcular el número de días hasta el vencimiento
            dias_hasta_vencimiento = (obj.vencimiento - timezone.now().date()).days

            if dias_hasta_vencimiento <= 28:
                return "Por Vencer en {} días".format(dias_hasta_vencimiento + 1)
            else:
                return str(obj.vencimiento)
        else:
            return "No Aplica"

    def costo_unit(self, obj):
        return f'{obj.costo_unitario():,.2f}' 

    def Precio_venta(self, obj):

        configuracion = Configuracion.objects.all().first()
        precio = ProductoPrecio.objects.filter(producto=obj).first()
        if precio:
            if configuracion.precio_venta_automatico == False:
                return f'{configuracion.Moneda}{"{:,.2f}".format(precio.precio_manual)} x {precio.cantidad} {precio.unidad_de_medida[:3]}'
            else:
                return f'{configuracion.Moneda}{"{:,.2f}".format(precio.precio())} x {precio.cantidad} {precio.unidad_de_medida[:3]}'
        else:
            return 0
        
    def en_inventario(self, obj):
        stock = f'{"{:,.2f}".format(obj.stock_actual())} {obj.unidad_de_medida}'
        return stock  

