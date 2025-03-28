from django.utils import timezone
from django.db import models
from producto.models import Producto, UNIDADES_DE_MEDIDA
from agenda.models import medioDeCompra,deposito,Proveedor, medioDePago,Caja
from django.core.exceptions import ValidationError
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from agenda.models import Configuracion

class Compra(models.Model):
    fecha = models.DateField(default=timezone.now)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT,blank=True,null=True,verbose_name='Proveedor')
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, blank=False, null=True)
    total = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0)
    Deposito = models.ForeignKey(deposito, on_delete=models.PROTECT,verbose_name='Deposito ingreso',blank=True,null=True)
    estado = models.BooleanField(default=False)
    compra_inicial = models.BooleanField(default=False)

    def __str__(self):
        return f'Compra # ({self.id}) - {self.total_compra():,.2f}'
     
    def clean(self):
        if self.estado == True:
            raise ValidationError("Este producto ya fué controlado. No se puede modificar.")
        super().clean()
    
    def validar_compra(self):

        diferencia = float(5)
        total = float(self.total_compra())
        pagos = float(self.total_pagos())

        if pagos > total:
            diferencia_real = float(pagos - total)
        else:
            diferencia_real = float(total - pagos)

        if diferencia_real < diferencia and total > 0:
            return True
        else:
            return False

    def save(self, *args, **kwargs):

        
        super(Compra, self).save(*args, **kwargs)
    

    def total_compra(self):
        valor = detalleCompra.objects.filter(Compra=self).aggregate(
            total=Sum(F('Cantidad') * F('Precio'))
        )['total'] or 0

        fletes = FleteCompra.objects.filter(compra=self).aggregate(
            total=Sum('importe')
        )['total'] or 0

        return valor + fletes


    def total_pagos(self):
        detalles = medioDePagoCompra.objects.filter(Compra=self)
        valor = sum(detalle.Total if detalle.Total is not None else 0 for detalle in detalles)
        return valor   
    
    def gastosflete(self):
        fletes = FleteCompra.objects.filter(compra=self)
        valor = sum(flete.importe if flete.importe is not None else 0 for flete in fletes)
        return valor   

    class Meta:
        verbose_name = 'compra'
        verbose_name_plural = 'Ingresos'

class FleteCompra(models.Model):
    compra=models.ForeignKey(Compra,on_delete=models.CASCADE)
    importe =models.DecimalField(max_digits=25,decimal_places=2,default=0)

class medioDePagoCompra(models.Model):
    fecha = models.DateField(auto_now_add=True,blank=True,null=True)
    Compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    Cuenta = models.ForeignKey(medioDeCompra,on_delete=models.PROTECT,blank=False,null=False,verbose_name='medio de pago')
    Total = models.DecimalField(max_digits=25, decimal_places=2, default=0, blank=True, null=True)
    cancelado = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.fecha.day}/{self.fecha.month} $ {self.Total:,.0f}'
    
    class Meta:
        verbose_name = 'pago'
        verbose_name_plural = 'Pagos de compras' 

    def clean(self):
        if self.Total <= 0:
            raise ValidationError("El pago debe ser superior a 0.")

        if not self.Compra.proveedor or self.Compra.proveedor is None:  
            if self.Cuenta.cuenta_corriente:
               raise ValidationError("Para utilizar un medio de pago que genera una cuenta corriente, debe seleccionar un proveedor en la compra.") 

        super().clean()

    def save(self, *args, **kwargs):

        if self.Cuenta.cuenta_corriente and not self.pk:
            self.cancelado = False

        super(medioDePagoCompra, self).save(*args, **kwargs)

    def pagos_pendientes(fecha_inicial, fecha_final):

        pagos_por_dia = medioDePagoCompra.objects.filter(
            fecha__range=(fecha_inicial, fecha_final),
            Cuenta__cuenta_corriente=True,
            cancelado=False,
        ).values('fecha').annotate(total=Sum(ExpressionWrapper(F('Total'), output_field=DecimalField())))

        total = sum(pago['total'] for pago in pagos_por_dia)
        
        return total
    
    def compras_mensual(fecha_inicial, fecha_final):

        pagos_por_dia = medioDePagoCompra.objects.filter(
            fecha__range=(fecha_inicial, fecha_final),
        ).values('fecha').annotate(total=Sum(ExpressionWrapper(F('Total'), output_field=DecimalField())))

        total = sum(pago['total'] for pago in pagos_por_dia)
        
        return total

class detalleCompra(models.Model):

    Fecha = models.DateField(auto_now_add=True)
    Compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    Cantidad = models.DecimalField(max_digits=25, decimal_places=3,default=1)
    unidad_de_medida = models.CharField(max_length=50,choices=UNIDADES_DE_MEDIDA,default='Unidades',blank=False,null=True)
    Precio = models.DecimalField(max_digits=25,decimal_places=3,default=0)
    Descuento = models.DecimalField(verbose_name="Desc (%)",max_digits=5, decimal_places=2,default=0)
    Deposito = models.ForeignKey(deposito, on_delete=models.PROTECT,default="general",verbose_name='Deposito ingreso',blank=True,null=True)
    Total = models.DecimalField(max_digits=25,decimal_places=2,default=0)
    ActualizarCosto = models.BooleanField(default=True)

    unidades_producto = models.DecimalField(max_digits=25, decimal_places=3,default=1)
    costo_unitario_producto = models.DecimalField(max_digits=25, decimal_places=3,default=0)
    unidad_de_medida_producto = models.CharField(max_length=50,choices=UNIDADES_DE_MEDIDA,blank=True,null=True)

    class Meta:
        verbose_name = 'detalle de compra'
        verbose_name_plural = 'Detalles de compras'

    def clean(self):

        if self.unidad_de_medida != self.producto.unidad_de_medida:
            if self.producto == 'Kilos' or self.producto == 'Gramos':
                if self.unidad_de_medida != 'Kilos' or self.unidad_de_medida != 'Gramos':
                    raise ValidationError(f"Solo puedes comprar este producto en Kilos o Gramos")

            elif self.producto == 'Litros' or self.producto == 'Mililitros':
                if self.unidad_de_medida != 'Litros' or self.unidad_de_medida != 'Mililitros':
                    raise ValidationError(f"Solo puedes comprar este producto en Litros o Mililitros")
            else:
                raise ValidationError(f"Solo puedes comprar este producto en {self.producto.unidad_de_medida}") 
             
                
        tipo_descuento = 0

        if tipo_descuento == 0:  # validacion que no se este haciendo modificaciones

            if self.Descuento > 100:
                raise ValidationError("El descuento no puede ser superior a 100%.")
            
            if self.Descuento < 0:
                raise ValidationError("El descuento debe ser superior o igual a 0%.")
        
        super().clean()
    
    def save(self, *args, **kwargs):

        self.unidades_producto = self.producto.cantidad
        self.unidad_de_medida_producto = self.producto.unidad_de_medida
        self.costo_unitario_producto = self.producto.costo_unitario()

        # tipo de descuento 0 es en % y 1 es para que sea por importe.
        tipo_descuento = 0

        if tipo_descuento == 0:
            precio = round(float(self.Precio),2)
            descuento = (precio * float(self.Descuento) / 100)
            self.Total = float(precio - descuento) * float(self.Cantidad)
        else:
            self.Total = round(float((self.Precio * self.Cantidad) - self.Descuento),2)
        
        try:
            self.Deposito = self.Compra.Deposito
        except:
            pass

        super(detalleCompra, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'detalle de comrpa'
        verbose_name_plural = 'Productos comprados' 

    def compras_mensual(fecha_inicial, fecha_final):
        # Obtener las ventas por día
        compras_por_dia = Compra.objects.filter(
            fecha__range=(fecha_inicial, fecha_final),
            estado=True
        ).values('fecha').annotate(total=Sum(ExpressionWrapper(F('total'), output_field=DecimalField())))

        # Sumar los valores de total_venta
        total = sum(venta['total'] for venta in compras_por_dia)
        
        return total
    
    def costo_unitario(self):
        costo_unitario = float(self.Total) / float(self.Cantidad)
        return costo_unitario
    
    def contexto(self):
        moneda = Configuracion.objects.first().Moneda.Abreviacion or '$'
        costo_unitario_anterior = self.producto.costo_unitario()
        costo_unitario_nuevo = float(self.Total) / float(self.Cantidad)

        if self.producto.unidad_de_medida != self.unidad_de_medida:
    
            if self.producto.unidad_de_medida == "Kilos" or self.producto.unidad_de_medida == "Litros":
                costo_unitario_anterior = round(costo_unitario_anterior / 1000,2)
            else:
                costo_unitario_anterior = round(costo_unitario_anterior * 1000,2)

        if costo_unitario_anterior > costo_unitario_nuevo:
            variacion=round(float(1 -float(costo_unitario_nuevo) / float(costo_unitario_anterior)) * 100,2)
            return f'El producto es un %{variacion:,.2f} más barato . Último costo unitario registrado {moneda} {costo_unitario_anterior:,.2f}'
        elif costo_unitario_anterior < costo_unitario_nuevo:
            variacion=round(float(1 -float(costo_unitario_anterior) / float(costo_unitario_nuevo)) * 100,2)
            return f'El producto es un %{variacion:,.2f} más costoso . Último costo unitario registrado {moneda} {costo_unitario_anterior:,.2f}'
        else:
            return f"Sin variación de precios respecto al costo acutal del producto"

class PagosProveedores(models.Model):
    fecha = models.DateField(auto_now_add=True, blank=True, null=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, blank=True, null=True)
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, blank=False, null=True)
    estado = models.BooleanField(default=False)
    pagos_pendientes = models.ManyToManyField(medioDePagoCompra, blank=True, related_name='pagos_proveedores', verbose_name='Pagos adeudados')
    medio_de_pago = models.ForeignKey(medioDePago, on_delete=models.CASCADE, default=1)
    total = models.DecimalField(max_digits=25, decimal_places=2, default=0, null=True)
    
    class Meta:
        verbose_name = 'pago'
        verbose_name_plural ='Pagos a proveedores'

    def __str__(self):
        return f'#{self.fecha} - {self.proveedor.Empresa or self.proveedor.NombreApellido} | Deuda Actual $ {self.total:,.2f} '
    
    def clean(self):
        if self.estado:
            raise ValidationError("Este pago ya está confirmado y no puede ser modificado.")
        
        if self.medio_de_pago.cuenta_corriente:
            raise ValidationError("Este medio de pago no está disponible para cancelar deudas en cuentas corrientes. Por favor seleccione otro medio de pago.")
        
        super().clean()

    def deuda_actual(self):
        total = 0
        pagos_asociados = medioDePagoCompra.objects.filter(Compra__proveedor=self.proveedor, cancelado=False)
        for pago in pagos_asociados:
            total += pago.Total
        return total
           
    def seleccionado(self):
        total = 0
        pagos = self.pagos_pendientes.all()
        for pago in pagos:
            total += pago.Total
        return total
    
    def autorizar_pago(self):
        self.estado = True
        self.save()
        for pago in self.pagos_pendientes.all():
            pago.cancelado = True
            pago.save()








