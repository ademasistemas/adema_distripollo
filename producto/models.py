from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from agenda.models import Configuracion

UNIDADES_DE_MEDIDA = [
        ('Unidades', 'Unidades'),
        ('Kilos', 'Kilos'),
        ('Gramos', 'Gramos'),
        ('Litros', 'Litros'),
        ('Mililitros', 'Mililitros'),
        ('Mt2','Mt²'),
        # ('Onzas', 'Onzas'),
        # ('Libras', 'Libras'),
    ]

TIPO_CHOICES = [
    ('Simple', 'Simple'),
    ('Compuesto', 'Compuesto')
]

def validate_image_size(value):
    width, height = value.width, value.height
    if width != 500 or height != 500:
        raise ValidationError('La imagen debe ser de 500x500 píxeles.')

class Categoria(models.Model):
    nombre = models.CharField(max_length=100,unique=True)

    def __str__(self):
        return self.nombre

class SubCategoria(models.Model):
    nombre = models.CharField(max_length=100,unique=True)

    def __str__(self):
        return self.nombre
    
class Producto(models.Model):
    codigo = models.DecimalField(max_digits=16, decimal_places=2,default=0,blank=False,null=True,unique=True)
    nombre = models.CharField(max_length=100,blank=False,null=True,default='Nombre')
    descripcion = models.CharField(max_length=200,blank=True,null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    sub_categoria = models.ForeignKey(SubCategoria, on_delete=models.SET_NULL, null=True, blank=True)
    marca = models.CharField(max_length=200,blank=True,null=True)
    imagen = models.ImageField(
        upload_to='img/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']), validate_image_size]
    )
    unidad_de_medida = models.CharField(max_length=50,choices=UNIDADES_DE_MEDIDA,blank=False,null=False,default="Unidades")
    cantidad = models.DecimalField(max_digits=20, decimal_places=2, default=1, blank=False, null=False)
    costo = models.DecimalField(max_digits=25, decimal_places=2,default=0,blank=False,null=False)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='Simple')
    vencimiento = models.DateField(blank=True,null=True)
    habilitar_venta = models.BooleanField(default=True)
    habilitar_stock = models.BooleanField(default=True)
    mostrar = models.BooleanField(default=False,help_text='Mostrar en la carta al publico (Carta QR)')
    ultima_modificacion = models.DateTimeField(auto_now_add=True,blank=True,null=True)

    def __str__(self):
        if self.codigo:
            if self.nombre:
                return f'{self.codigo} {self.nombre.upper()}'
            else:
                return f'{self.codigo} - Sin Nombre'
        return f'Producto sin nombre'

    @property
    def stock_es_negativo(self):
        return self.stock_actual() < 0
        
    def clean(self):

        super().clean()

    def save(self, *args, **kwargs):
        super(Producto, self).save(*args, **kwargs)

    def stock_actual(self):

        from compra.models import detalleCompra  # Importa Compra aquí para evitar el ciclo de importación circular
        from venta.models import DetalleVenta, ProductosIncluidosVendidos  # Importa DetalleVenta aquí para evitar el ciclo de importación circular

        # 1. Mermas del producto
        mermas = Merma.objects.filter(producto=self)
        mermas_totales = mermas.aggregate(total_mermas=models.Sum('cantidad')).get('total_mermas') or 0

    
        # 2. Total de compras confirmadas del producto
        compras = detalleCompra.objects.filter(producto=self, Compra__estado=True)
        compras_totales = compras.aggregate(total_compras=models.Sum('Cantidad')).get('total_compras') or 0

        # 3. Ventas directas del producto
        ventas = DetalleVenta.objects.filter(producto=self, venta__estado=3)
        ventas_totales = 0
      
        for venta in ventas:
            uni_compra = self.unidad_de_medida
            uni_uso = venta.unidad_de_medida

            if uni_uso != uni_compra:
                if uni_compra in ["Gramos", "Mililitros"]:
                    ventas_totales += venta.cantidad * 1000 * venta.cantidad_producto
                else:  # Kilos o Litros
                    ventas_totales += venta.cantidad / 1000 * venta.cantidad_producto
            else:
                ventas_totales += venta.cantidad * venta.cantidad_producto


        # 4. Descontar productos incluidos en ventas de compuestos
        recetas_vendidas = ProductosIncluidosVendidos.objects.filter(
            receta_producto__producto_usado=self
        )
        total_receta_vendida = 0

        for receta in recetas_vendidas:
            total_receta_vendida += receta.cantidad
     
        # 5. Devoluciones del producto
        devoluciones_totales = ventas.filter(venta__estado=5).aggregate(
            total_devoluciones=models.Sum('cantidad')
        ).get('total_devoluciones') or 0

        # Cálculo final del stock
        stock = compras_totales - ventas_totales - total_receta_vendida - mermas_totales - devoluciones_totales
        return stock
    
    def stock_actual_str(self):
        return f'{self.stock_actual():,.2f} {self.unidad_de_medida[:4]}' 

    def precio_venta(self):
        primer_precio=ProductoPrecio.objects.filter(producto=self).first()
        if primer_precio:
            precio = float(primer_precio.precio())
        else:
            precio = 0
        return precio    

    def costo_unitario(self, procesados=None):
        if self.tipo == 'Compuesto':
            total = 0
            cantidad = self.cantidad
            productos = RecetaProducto.objects.filter(producto_principal=self)

            for item in productos:
                total += item.Costo_calculado(procesados)

            total = round(float(total) / float(cantidad),2)
            return round(total, 2)
        return round(float(self.costo) / float(self.cantidad),2)

    def valuacion():
        productos = Producto.objects.all()
        suma = 0
        for producto in productos:
            if producto.stock_actual() > 0:
                suma += round((producto.costo / producto.cantidad) * producto.stock_actual(),2)
        return suma

    @property
    def primer_producto_precio(self):
        return ProductoPrecio.objects.filter(producto=self).first()
    
    @property
    def productos_precio(self):
        return ProductoPrecio.objects.filter(producto=self)

    def convertir_unidades(self, cantidad, unidad_origen, unidad_destino):
        """
        Convierte unidades de medida entre kilos/gramos, litros/mililitros, etc.
        """
        conversiones = {
            ('Kilos', 'Gramos'): lambda x: x * 1000,
            ('Gramos', 'Kilos'): lambda x: x / 1000,
            ('Litros', 'Mililitros'): lambda x: x * 1000,
            ('Mililitros', 'Litros'): lambda x: x / 1000,
        }
        if unidad_origen == unidad_destino:
            return cantidad
        else:
            try:
                return conversiones[(unidad_origen, unidad_destino)](cantidad)
            except KeyError:
                raise ValidationError(
                    f"No se puede convertir de '{unidad_origen}' a '{unidad_destino}'. Verifique las unidades de medida."
                )

class ProductoPrecio(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)
    cantidad =  models.DecimalField(max_digits=20, decimal_places=2, default=1, blank=False, null=False)
    unidad_de_medida = models.CharField(max_length=50,choices=UNIDADES_DE_MEDIDA,blank=False,null=False,default="Unidades")
    rentabilidad = models.DecimalField(max_digits=7, decimal_places=2,default=0 ,blank=False,null=False)
    precio_manual = models.DecimalField(max_digits=15, decimal_places=2,default=0 ,blank=False,null=False)

    def clean(self): 
        
        config = Configuracion.objects.first()

        if config.precio_venta_automatico:
            if self.rentabilidad < 0:
                raise ValidationError("La rentabilidad no puede ser inferior a 0%") 
            
        if self.cantidad == 0:
            raise ValidationError("La cantidad debe ser superior a 1.") 
        
        if self.producto.unidad_de_medida == 'Unidades' and self.unidad_de_medida != 'Unidades':
            raise ValidationError("Debido a la medida de uso de tu producto solo puedes usar 'Unidades'.") 
           
        if self.producto.unidad_de_medida == 'Mt2' and self.unidad_de_medida != 'Mt2':
            raise ValidationError("Debido a la medida de uso de tu producto solo puedes usar 'Mt²'.")     
        
        if self.producto.unidad_de_medida == 'Kilos':
            if self.unidad_de_medida != 'Kilos' and self.unidad_de_medida != 'Gramos':
                raise ValidationError("Debido a la medida de uso de tu producto solo puedes usar 'Kilos' o 'Gramos'.")
            
        if self.producto.unidad_de_medida == 'Gramos':
            if self.unidad_de_medida != 'Kilos' and self.unidad_de_medida != 'Gramos':
                raise ValidationError("Debido a la medida de uso de tu producto solo puedes usar 'Kilos' o 'Gramos'.")   
            
        if self.producto.unidad_de_medida == 'Litros':
            if self.unidad_de_medida != 'Litros' and self.unidad_de_medida != 'Mililitros':
                raise ValidationError("Debido a la medida de uso de tu producto solo puedes usar 'Litros' o 'Mililitros'.")       
               
        if self.producto.unidad_de_medida == 'Mililitros':
            if self.unidad_de_medida != 'Litros' and self.unidad_de_medida != 'Mililitros':
                raise ValidationError("Debido a la medida de uso de tu producto solo puedes usar 'Litros' o 'Mililitros'.")   

        if self.producto.unidad_de_medida == 'Onza':
            if self.unidad_de_medida != 'Litros' and self.unidad_de_medida != 'Mililitros':
                raise ValidationError("Debido a la medida de uso de tu producto solo puedes usar 'Litros' o 'Mililitros'.")   
    

        return super().clean()
    
    def precio(self):

        precio = 0
            
        config = Configuracion.objects.first()

        if self.producto.tipo == "Compuesto":

            costo_unitario_receta = float(self.producto.costo_unitario())
            if config.precio_venta_automatico == True:
                precio = (float(costo_unitario_receta) + (float(self.rentabilidad) * float(costo_unitario_receta) / 100)) * float(self.cantidad)
            else:
                precio = float(self.precio_manual) / float(self.producto.cantidad)

        else:

            if config.precio_venta_automatico == True:

                if self.producto.unidad_de_medida == 'Unidades':
                    # precio = float((self.producto.costo) / (100 - self.rentabilidad) * 100) * float(self.cantidad)
                    precio = float(float(self.producto.costo) + (float(self.rentabilidad) * float(self.producto.costo) / 100)) * float(self.cantidad)
                    precio = float(precio) / float(self.producto.cantidad)
                elif self.producto.unidad_de_medida == 'Kilos':
                    if self.unidad_de_medida == 'Kilos':
                        precio = float((self.producto.costo_unitario()) / float(100 - self.rentabilidad) * 100) * float(self.cantidad)
                    else:
                        precio = float((self.producto.costo_unitario()) / float(100 - self.rentabilidad) * 100) * float(self.cantidad) / 1000
                elif self.producto.unidad_de_medida == 'Litros':
                    if self.unidad_de_medida == 'Litros':
                        precio = float((self.producto.costo_unitario()) / float(100 - self.rentabilidad) * 100) * float(self.cantidad)
                        precio = (float(self.producto.costo_unitario()) + float(float(self.rentabilidad / 100) * float(self.producto.costo_unitario()))) * float(self.cantidad)
                    else:
                        precio = float((self.producto.costo_unitario()) / float(100 - self.rentabilidad) * 100) * float(self.cantidad) / 1000

                elif self.producto.unidad_de_medida == 'Gramos':

                    if self.unidad_de_medida == 'Gramos':
                        precio = float((self.producto.costo_unitario()) / float(100 - self.rentabilidad) * 100) * float(self.cantidad)
                    else:
                        precio = float((self.producto.costo_unitario()) / float(100 - self.rentabilidad) * 100) * float(self.cantidad) * 1000

                elif self.producto.unidad_de_medida == 'Mililitros':
                    if self.unidad_de_medida == 'Mililitros':
                        precio = float((self.producto.costo_unitario()) / float(100 - self.rentabilidad) * 100) * float(self.cantidad)
                    else:
                        precio = float((self.producto.costo_unitario()) / float(100 - self.rentabilidad) * 100) * float(self.cantidad) * 1000
                
                elif self.producto.unidad_de_medida == 'Mt2':
                    precio = float(float(self.producto.costo_unitario()) + (float(self.rentabilidad) * float(self.producto.costo_unitario()) / 100)) * float(self.cantidad)
                    precio = float(precio) / float(self.producto.cantidad)
        
            else:
                precio = float(self.precio_manual) / float(self.producto.cantidad)


        return round(precio, 2)
    
    def costo_unitario_actual(self):
        return round(float(self.producto.costo_unitario()) ,2)

    def costo_total_actual(self):
        return round(float(self.producto.costo_unitario()) * float(self.cantidad) ,2)
    
    def margen_de_utilidad(self):
        # Llama a costo_unitario como método
        costo = float(self.producto.costo_unitario()) * float(self.cantidad) or 0
        precio = float(self.precio()) or 0
        if precio > 0:
            utilidad = round((precio - costo) / precio, 2)
        else:
            utilidad = 0
        return f'% {utilidad * 100:,.2f}'

    def __str__(self):
        return f'x {self.cantidad} {self.unidad_de_medida}'
    
    class Meta:
        verbose_name = 'precio'
        verbose_name_plural ='Precio de Productos' 

class RecetaProducto(models.Model):
    producto_principal = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='recetas')
    producto_usado = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='usado_en_recetas')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2,default=1)
    unidad_de_medida = models.CharField(max_length=50, choices=UNIDADES_DE_MEDIDA,default='Unidades')

    def __str__(self):
        return f'{self.cantidad} {self.unidad_de_medida} de {self.producto_usado.nombre}'
    
    class Meta:
        verbose_name = 'composicion'
        verbose_name_plural = '🛠️ Composicion'

    def Costo_calculado(self, procesados=None):
        if procesados is None:
            procesados = set()

        if self.producto_usado in procesados:
            # Evita ciclos recursivos
            return 0

        procesados.add(self.producto_usado)

        costo_unitario = float(self.producto_usado.costo_unitario(procesados)) * float(self.cantidad) or 0

        if self.unidad_de_medida != self.producto_usado.unidad_de_medida:
            if self.unidad_de_medida == "Kilos" or self.unidad_de_medida == "Litros":
                costo_unitario *= 1000
            elif self.unidad_de_medida == "Gramos" or self.unidad_de_medida == "Mililitros":
                costo_unitario /= 1000

        return costo_unitario

    def clean(self): 
        if self.validad_udm() != True:
            raise ValidationError(f"Validar Unidad de medida.") 
        return super().clean()
    
    def validad_udm(self):
        '''
            Esta validacion es para ver si las unidades de medida corresponden.
            Solo se usa al guardar un precio de producto
        '''
        unidad_compra=self.producto_usado.unidad_de_medida
        unidad_uso=self.unidad_de_medida
        if unidad_compra==unidad_uso:
            return True
        else: 
            if unidad_compra == 'Unidades':
                raise ValidationError(f"El precio tiene que tener la siguiente unidad de medida: Unidades")
            elif unidad_compra == 'Mt2':
                raise ValidationError(f"El precio tiene que tener la siguiente unidad de medida: Mt2s")
            elif unidad_compra == 'Kilos':
                if unidad_uso != 'Gramos':
                    raise ValidationError(f"El precio tiene que tener una de las siguientes unidades de medida: Kilos o Gramos")
            elif unidad_compra == 'Gramos':
                if unidad_uso != 'Kilos':
                    raise ValidationError(f"El precio tiene que tener una de las siguientes unidades de medida: Kilos o Gramos")
            elif unidad_compra == 'Litros':    
                if unidad_uso != 'Mililitros':
                    raise ValidationError(f"El precio tiene que tener una de las siguientes unidades de medida: Litros o Mililitros")
            elif unidad_compra == 'Mililitros':
                if unidad_uso != 'Litros':
                    raise ValidationError(f"El precio tiene que tener una de las siguientes unidades de medida: Litros o Mililitros")
            elif unidad_compra == 'Onzas':    
                if unidad_uso != 'Libras':
                    raise ValidationError(f"El precio tiene que tener una de las siguientes unidades de medida: Libras o Onzas")
            elif unidad_compra == 'Libras':
                if unidad_uso != 'Onzas':
                    raise ValidationError(f"El precio tiene que tener una de las siguientes unidades de medida: Libras o Onzas")
            elif unidad_compra == 'Mt':    
                if unidad_uso != 'Cms':
                    raise ValidationError(f"El precio tiene que tener una de las siguientes unidades de medida: Mt o Cms")
            elif unidad_compra == 'Cms':
                if unidad_uso != 'Mt':
                    raise ValidationError(f"El precio tiene que tener una de las siguientes unidades de medida: Mt o Cms")
            return True

class Merma(models.Model):
    fecha = models.DateField(auto_now=True)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)
    cantidad = models.IntegerField(default=1)
    motivo = models.CharField(max_length=255,blank=False,null=False)

    def __str__(self):
        return f'{self.producto}'
    