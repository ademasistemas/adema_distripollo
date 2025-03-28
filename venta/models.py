from datetime import timedelta, datetime
from django.db import models
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.forms import ValidationError
from agenda.models import Caja, Cliente,Monedas,Configuracion,Chofer,medioDePago
from producto.models import Producto, RecetaProducto
from repositories.VentaRepository import VentaRepository
from django.utils import timezone

UNIDADES_DE_MEDIDA = [
        ('Unidades', 'Unidades'),
        ('Kilos', 'Kilos'),
        ('Gramos', 'Gramos'),
        ('Litros', 'Litros'),
        ('Mililitros', 'Mililitros'),
        ('Onzas', 'Onzas'),
        ('Libras', 'Libras'),
    ]
    
class Venta(models.Model):
    codigo = models.CharField(max_length=200, null=True, blank=True)
    cliente = models.ForeignKey(Cliente,on_delete=models.CASCADE,blank=True,null=True)
    vendedor = models.CharField(max_length=255,blank=True,null=True)
    fecha = models.DateTimeField(default=timezone.now, null=True, blank=True)
    total = models.DecimalField(max_length=25, decimal_places=2, max_digits=10, null=True)
    nombre_factura = models.CharField(verbose_name='Vendedor',max_length=200, null=True, blank=True)
    nit = models.IntegerField(null=True, blank=True)
    razon_cancelacion = models.CharField(max_length=200, null=True, blank=True)
    entregado = models.BooleanField(default=False)
    cancelado = models.BooleanField(default=False)
    total_entrega = models.DecimalField(decimal_places=2, max_digits=10, default=0)

    def __str__(self):
        return f'#{self.codigo} - {self.cliente.nombre} $ {self.total:,.2f}'
    
    class Meta:
        verbose_name = 'venta'
        verbose_name_plural ='Egresos'

    ESTADO_CREADA = 0
    ESTADO_PAGADA = 1
    ESTADO_FACTURADA = 2
    ESTADO_FINALIZADA = 3
    ESTADO_CANCELADA = 4
    ESTADO_ANULADA = 5

    ESTADOS = (
        (ESTADO_CREADA, 'creada'),
        # (ESTADO_PAGADA, 'pagada'),
        # (ESTADO_FACTURADA, 'facturada'),
        (ESTADO_FINALIZADA, 'finalizada'),
        (ESTADO_CANCELADA, 'cancelada'),
        (ESTADO_ANULADA, 'anulada'),
    )

    estado = models.IntegerField(choices=ESTADOS, default=0)

    def pagar(self):
        if self.estado != self.ESTADO_CREADA:
            raise ValidationError("La venta debe estar en estado 'creada' para ser pagada.")
        
        VentaRepository.pagar(self)
        self.estado = self.ESTADO_PAGADA
        self.save()
        
    def facturar(self, cliente, vendedor):
        if self.estado != self.ESTADO_PAGADA:
            raise ValidationError("La venta debe estar en estado 'pagada' para ser facturada.")
        
        VentaRepository.facturar(self, vendedor, cliente)
        self.estado = self.ESTADO_FACTURADA
        self.save()

    def finalizar(self):
        if self.estado not in [self.ESTADO_PAGADA, self.ESTADO_FACTURADA, self.ESTADO_CREADA]:
            raise ValidationError("La venta debe estar en un estado válido para ser finalizada.")
        
        # Procesar los productos compuestos
        for detalle in self.detalleventa_set.all():
            producto = detalle.producto
            if producto.tipo == 'Compuesto':

                # Crear ProductoCompuestoVendido
                compuesto_vendido = ProductoCompuestoVendido.objects.create(
                    venta=self,
                    producto_compuesto=producto,
                    cantidad=detalle.cantidad
                )

                # Registrar los productos incluidos en el producto compuesto
                for receta in RecetaProducto.objects.filter(producto_principal=producto):

                    # Validar que los valores no sean None
                    receta_cantidad = receta.cantidad or 0
                    detalle_cantidad = detalle.cantidad or 0
                    unidad_origen = receta.unidad_de_medida
                    unidad_destino = receta.producto_usado.unidad_de_medida

                    # Calcular cantidad final ajustada
                    cantidad_total = self.convertir_unidades(
                        receta_cantidad * detalle_cantidad,
                        unidad_origen,
                        unidad_destino
                    )

                    # Validar costo_unitario del producto usado
                    costo_unitario = receta.producto_usado.costo_unitario() or 0

                    # Registrar ProductosIncluidosVendidos
                    ProductosIncluidosVendidos.objects.create(
                        producto_compuesto_vendido=compuesto_vendido,
                        receta_producto=receta,
                        cantidad=cantidad_total,
                        unidad_de_medida=unidad_destino,
                        costo_unitario=costo_unitario
                    )

        # Actualizar estado de la venta
        self.estado = self.ESTADO_FINALIZADA
        self.save()
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




        # Método para cancelar
    def cancelar(self, motivo):
        if self.estado != self.ESTADO_CREADA:
            raise ValidationError("Solo una venta en estado 'creada' puede ser cancelada.")
        
        VentaRepository.cancelar(self, motivo)
        self.estado = self.ESTADO_CANCELADA
        self.save()
    def anular(self, motivo):
        if self.estado not in [self.ESTADO_PAGADA, self.ESTADO_FACTURADA, self.ESTADO_FINALIZADA]:
            raise ValidationError("La venta debe estar en un estado válido para ser anulada.")
        
        VentaRepository.anular(self, motivo)
        self.estado = self.ESTADO_ANULADA
        self.save()

    @staticmethod
    def totales_por_caja(fecha_actual):
        # Obtener los vendedores únicos para ventas en estado 3 en la fecha dada
        cajeros = Venta.objects.filter(
            fecha__date=fecha_actual,
            estado=3
        ).values('nombre_factura').distinct()

        ventas_por_caja = {}

        # Calcular el total de ventas por caja
        for caja in cajeros:
            total_venta = Venta.objects.filter(
                fecha__date=fecha_actual,
                nombre_factura=caja['nombre_factura'],
                estado=3
            ).aggregate(total_venta=Sum(F('detalleventa__cantidad') * F('detalleventa__precio')))

            total = total_venta['total_venta'] or 0

            ventas = Venta.objects.filter(
                fecha__date=fecha_actual,
                nombre_factura=caja['nombre_factura'],
                estado=3
            )

            total_excedente=0

            for venta in ventas:
                pagos = PagosVentas.objects.filter(venta=venta)
                for pago in pagos:
                    if pago.adicional_cc:
                        total_excedente += pago.total

            total = total - total_excedente
            ventas_por_caja[caja['nombre_factura']] = total
    
        return ventas_por_caja
    
    @staticmethod
    def cobroCliente(fecha_actual):

        total_excedente=0

        pagos = PagosVentas.objects.filter(
            fecha__day=datetime.now().day,
            fecha__month=datetime.now().month,
            fecha__year=datetime.now().year
            )
        for pago in pagos:
            if pago.adicional_cc:
                total_excedente += pago.total
            
            if pago.cancelado and pago.medio_de_pago.cuenta_corriente:
                total_excedente += pago.total
        return float(total_excedente)
    
    @property
    def get_cart_total(self):
        config = Configuracion.objects.first()
        detalleventas = self.detalleventa_set.all().filter(moneda=config.Moneda.id)
        total = sum([float(item.get_total) for item in detalleventas]) + float(self.total_entrega)

        return total
    
    @property
    def get_total(self):
        total = float(self.cantidad) * float(self.precio) * float(self.cantidad_producto)
        
        if self.unidad_de_medida == 'Mt2s':
            total *= float(self.base / 1000) * float(self.altura / 1000)
        
        return round(total, 2)
    
    @property
    def get_cart_total_dolares(self):
        config = Configuracion.objects.first()
        detalleventas = self.detalleventa_set.all().filter(moneda=config.Moneda_secundaria.id)
        total = sum([item.get_total for item in detalleventas])
        return total

    @property
    def get_cart_items(self):
        detalleventas = self.detalleventa_set.all()
        total = sum([item.cantidad for item in detalleventas])
        return total

    @property
    def productos(self):
        detalleventas = self.detalleventa_set.all()
        return detalleventas

    @property
    def get_date(self):
        if self.estado == self.ESTADO_CREADA:
            return 'En curso'
        else:
            return self.fecha

    @property
    def pagos_en_cuenta_corriente(self):
        total = PagosVentas.objects.filter(
            venta=self,
            medio_de_pago__cuenta_corriente=True
        ).aggregate(total_general=Sum('total'))['total_general'] or 0
        return total
    
    def __str__(self):
        total = self.total or 0
        if self.cliente:
            return f'{self.codigo} | 👤 {self.cliente}  | $ {round(total,2):,.2f}'
        else:
            return f'{self.codigo} | 👤 Cons. Final  | $ {round(total,2):,.2f}'
        
    @staticmethod
    def total_diario(fecha):
            total = Venta.objects.filter(
                fecha=fecha,
            ).aggregate(total_general=Sum('total'))['total_general'] or 0

            return total
        
class DetalleVenta(models.Model):
    fecha = models.DateField(default=timezone.now,blank=True,null=True)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    moneda = models.ForeignKey(Monedas, on_delete=models.CASCADE,blank=True,null=True)
    cantidad = models.DecimalField(max_digits=25, decimal_places=2,default=1)
    cantidad_producto = models.DecimalField(max_digits=25, decimal_places=2,default=1)
    unidad_de_medida = models.CharField(max_length=50,choices=UNIDADES_DE_MEDIDA,blank=False,null=False,default="Unidades")
    precio = models.DecimalField(max_digits=25, decimal_places=2, blank=True,null=True)
    base = models.DecimalField(max_digits=25, decimal_places=2, blank=True,null=True)
    altura = models.DecimalField(max_digits=25, decimal_places=2, blank=True,null=True)
    costo_unitario = models.DecimalField(max_digits=25, decimal_places=2, blank=True,null=True)
    costo_total = models.DecimalField(max_digits=25, decimal_places=2, blank=True,null=True)
    ganancias_estimadas = models.DecimalField(max_digits=25, decimal_places=2, blank=True,null=True)

    class Meta:
        verbose_name = 'detalle'
        verbose_name_plural ='Productos Simples Vendidos'

    @property
    def get_total_actualizado(self):
        total = float(self.cantidad) * float(self.producto.primer_producto_precio.costo_unitario_actual()) * (float(self.cantidad_producto)) + float(self.ganancias_estimadas)
        
        if self.unidad_de_medida == 'Mt2s':
            total = float(total) * float(self.base/1000) * float(self.altura/1000)

        return round(total,2)
    
    @property
    def get_total(self):
        total = float(self.cantidad) * float(self.precio) #float(self.cantidad_producto) * 

        if self.unidad_de_medida == 'Mt2s':
            total = float(total) * float(self.base/1000) * float(self.altura/1000)

        return round(total,2)

    def __str__(self):
        return self.producto.__str__() + ', cantidad: ' + self.cantidad.__str__() + ' -- ' + self.venta.codigo
    
    def save(self, *args, **kwargs): 
        self.costo_unitario = float(self.producto.costo_unitario())
        self.costo_total = float(self.producto.costo_unitario()) * float(self.cantidad) * float(self.cantidad_producto)
        self.ganancias_estimadas = float(self.get_total) - float(self.costo_total) 
        super(DetalleVenta, self).save(*args, **kwargs)
    

    def ventas_mensual(fecha_inicial, fecha_final):
        # Obtener las ventas por día
        ventas_por_dia = DetalleVenta.objects.filter(
            fecha__range=(fecha_inicial, fecha_final),
            venta__estado=3
        ).values('fecha').annotate(total_venta=Sum(ExpressionWrapper(F('cantidad') * F('precio'), output_field=DecimalField())))

        # Sumar los valores de total_venta
        total = sum(venta['total_venta'] for venta in ventas_por_dia)
        
        return total

    def ganancias_calculadas(fecha_inicial, fecha_final):
        # Obtener las ventas por día
        ventas_por_dia = DetalleVenta.objects.filter(
            fecha__range=(fecha_inicial, fecha_final),
            venta__estado=3
        ).values('fecha').annotate(total_ganancias=Sum(ExpressionWrapper(F('ganancias_estimadas'), output_field=DecimalField())))

        # Sumar los valores de total_venta
        total = sum(venta['total_ganancias'] for venta in ventas_por_dia)
        
        return total
    
    
    def pagos_pendientes(fecha_inicial, fecha_final):
        # Obtener las ventas por día
        pagos_por_dia = PagosVentas.objects.filter(
            fecha__range=(fecha_inicial, fecha_final),
            medio_de_pago__cuenta_corriente=True,
            cancelado=False,
        ).values('fecha').annotate(total=Sum(ExpressionWrapper(F('total'), output_field=DecimalField())))

        # Sumar los valores de total_venta
        total = sum(pago['total'] for pago in pagos_por_dia)
        
        return total

    def pagos_adicionales_pendientes(fecha_inicial, fecha_final):
        # Obtener las ventas por día
        pagos_por_dia = PagosVentas.objects.filter(
            fecha__range=(fecha_inicial, fecha_final),
            adicional_cc=True,
        ).values('fecha').annotate(total=Sum(ExpressionWrapper(F('total'), output_field=DecimalField())))

        # Sumar los valores de total_venta
        total = sum(pago['total'] for pago in pagos_por_dia)
        
        return -total

    @classmethod
    def Total_ventas(cls,fecha_inicial, fecha_final):

        dias = (fecha_final - fecha_inicial).days + 1
        total = []

        # Obtener las ventas por día
        ventas_por_dia = DetalleVenta.objects.filter(
            fecha__range=(fecha_inicial, fecha_final),
            venta__estado=3
        ).values('fecha').annotate(total_venta=Sum(ExpressionWrapper(F('cantidad') * F('precio'), output_field=DecimalField())))

        # Crear un diccionario con fechas y totales
        ventas_dict = {venta['fecha']: venta['total_venta'] for venta in ventas_por_dia}

        # Formatear los resultados en una lista
        for venta in range(dias):
            fecha = fecha_inicial + timedelta(days=venta)
            total_venta = ventas_dict.get(fecha, 0)
            total.append({'fecha': fecha, 'total_venta': total_venta})  # Guardar como objeto date

        # Ordenar la lista en orden descendente según la fecha
        total.sort(key=lambda x: x['fecha'], reverse=True)  # Ordena correctamente como objetos date

        # Opcional: convertir fechas a formato deseado después de la ordenación
        for item in total:
            item['fecha'] = item['fecha'].strftime("%d/%m")  # Ahora convierte a string para visualización
  
        return total
    
    def Total_costos(fecha_inicial, fecha_final):

        ventas = DetalleVenta.objects.filter(
            fecha__range=(fecha_inicial, fecha_final),
            venta__estado=3
        )
        costos=0
        for venta in ventas:
            # if venta.producto.fabricacion_propia:
            #     costos += float(venta.producto.fabricacion_propia.costo_porcion()) * float(venta.cantidad)
            # else:
            costos += float(venta.costo_total)

        return costos
    
    def Total_ventas_calculado(fecha_inicial, fecha_final):

        ventas = DetalleVenta.objects.filter(
            fecha__range=(fecha_inicial, fecha_final),
            venta__estado=3
        )
        total=0
        for venta in ventas:
            total += float(venta.producto.costo_unitario()) * float(venta.cantidad)
            
        return total


class ProductoCompuestoVendido(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='productos_compuestos_vendidos')
    producto_compuesto = models.ForeignKey(Producto, on_delete=models.CASCADE, limit_choices_to={'tipo': 'Compuesto'})
    cantidad = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return f"Producto Compuesto: {self.producto_compuesto.nombre} (x{self.cantidad}) en Venta {self.venta.codigo}"

    class Meta:
        verbose_name = 'detalle'
        verbose_name_plural ='Productos Compuestos Vendidos'


class ProductosIncluidosVendidos(models.Model):
    producto_compuesto_vendido = models.ForeignKey(
        ProductoCompuestoVendido, on_delete=models.CASCADE, related_name='productos_incluidos', null=True
    )
    receta_producto = models.ForeignKey(
        RecetaProducto, on_delete=models.CASCADE, related_name='detalles_vendidos', null=True
    )
    cantidad = models.DecimalField(max_digits=20, decimal_places=2, default=0, null=True)
    unidad_de_medida = models.CharField(max_length=50, choices=UNIDADES_DE_MEDIDA, null=True)
    costo_unitario = models.DecimalField(max_digits=20, decimal_places=2,default=0, null=True)

    def costo_total(self):
        return round(self.cantidad * self.costo_unitario, 2)

    def __str__(self):
        return f"{self.cantidad} {self.unidad_de_medida} de {self.producto_compuesto_vendido.producto_compuesto.nombre} (Costo: {self.costo_unitario:,.2f})"

    class Meta:
        verbose_name = 'detalle incluido'
        verbose_name_plural = 'Productos Incluidos Vendidos'


class EntregaVentas(models.Model):
    fecha_salida = models.DateField(blank=True,null=True)
    fecha_llegada = models.DateField(blank=True,null=True)
    detalles = models.TextField()
    chofer = models.ForeignKey(Chofer,on_delete=models.SET_NULL,blank=True,null=True)

    @property
    def get_costo_total(self):
        ventas_entrega = VentaEntrega.objects.filter(entrega=self)
        costo_total = 0

        for venta_ent in ventas_entrega:
            costo = venta_ent.venta.total if venta_ent.venta.total is not None else 0
            costo_total += costo

        return costo_total
    
    @property
    def get_gasto_total(self):
        gastos_entrega = GastoEntrega.objects.filter(entrega=self)
        costo_total = 0

        for gasto_ent in gastos_entrega:
            costo_total += gasto_ent.total

        return costo_total
    
    def gastos(self):
        return GastoEntrega.objects.filter(entrega=self)
    
    def ventas(self):
        return VentaEntrega.objects.filter(entrega=self)
    
    def cantidad_de_dias(self):
        if self.fecha_salida is not None and self.fecha_llegada is not None:
            diferencia = self.fecha_llegada - self.fecha_salida
            return diferencia.days
        else:
            return "-"
        
    class Meta:
        verbose_name = 'entrega'
        verbose_name_plural ='Entrega de Pedidos'

class VentaEntrega(models.Model):
    entrega = models.ForeignKey(EntregaVentas,on_delete=models.CASCADE)
    venta = models.ForeignKey(Venta,on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'entrega'
        verbose_name_plural ='Ventas a entregar'

class GastoEntrega(models.Model):
    entrega = models.ForeignKey(EntregaVentas,on_delete=models.CASCADE)
    gasto = models.CharField(max_length=255,blank=False,null=False)
    total = models.DecimalField(max_digits=25, decimal_places=2,blank=False,null=False)
   
    class Meta:
        verbose_name = 'gasto'
        verbose_name_plural ='Gastos de entrega'

class PagosVentas(models.Model):
    venta = models.ForeignKey(Venta,on_delete=models.CASCADE,blank=True,null=True)
    cliente = models.ForeignKey(Cliente,on_delete=models.CASCADE,blank=True,null=True)
    medio_de_pago = models.ForeignKey(medioDePago,on_delete=models.CASCADE)
    total = models.DecimalField(max_length=25, decimal_places=2, max_digits=10, null=True)
    fecha = models.DateField(default=timezone.now,blank=True,null=True)
    cancelado = models.BooleanField(default=True)
    adicional_cc = models.BooleanField(default=False)

    
    def __str__(self):
        return f'{self.fecha.day}/{self.fecha.month} $ {self.total:,.0f} $ {self.get_total_actualizado:,.0f}'
    
    class Meta:
        verbose_name = 'pago'
        verbose_name_plural ='Ingresos Ventas'

    def save(self, *args, **kwargs):

        if self.venta:
            if not self.cliente and self.venta.cliente:
                self.cliente = self.venta.cliente

        super(PagosVentas, self).save(*args, **kwargs)

    @property
    def get_total(self):
        pagos = PagosVentas.objects.filter(venta=self.venta)
        total = sum([pago.total for pago in pagos])
        return total
    
    @property
    def get_total_actualizado(self):

        total_actualizado=0
        total=0
        cuenta_corriente=0
        alicuota=0
        pagos =PagosVentas.objects.filter(venta=self.venta)

        for pago in pagos:
            if pago.medio_de_pago.cuenta_corriente:
                cuenta_corriente += pago.total
            total += pago.total
    
        if total > 0:
            alicuota = cuenta_corriente / total
        
        detalles_de_venta = DetalleVenta.objects.filter(venta=self.venta)
        for detalle in detalles_de_venta:
            total_actualizado += float(detalle.get_total_actualizado)

        total_actualizado = float(total_actualizado) * float(alicuota)

        return total_actualizado
    
class PagosClientes(models.Model):
    fecha = models.DateField(auto_now_add=True,blank=True,null=True)
    cliente = models.ForeignKey(Cliente,on_delete=models.CASCADE,blank=False,null=True)
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, blank=False, null=True)
    estado = models.BooleanField(default=False)
    pagos_ventas = models.ManyToManyField(PagosVentas, blank=True, related_name='pagos_clientes',verbose_name='Pagos adeudados')
    medio_de_pago = models.ForeignKey(medioDePago,on_delete=models.CASCADE,default=1)
    total = models.DecimalField(max_length=25, decimal_places=2, max_digits=10, default=0,null=True)
    tomar_actualizado = models.BooleanField(default=True,verbose_name='tomar deuda actualizada')
    
    class Meta:
        verbose_name = 'pago'
        verbose_name_plural ='Pagos de clientes'

    def __str__(self):
        return f'#{self.fecha} - {self.cliente.nombre} | Deuda Actual $ {self.total:,.2f}'
    
    def clean(self):

        if self.estado:
            raise ValidationError("Este pago ya esta confirmado y no puede ser modificado.")
        
        if self.medio_de_pago.cuenta_corriente:
            raise ValidationError("Este medio de pago no esta disponible para cancelar deudas en cuentas corrientes. Por favor seleccione otro medio de pago.")
        
        super().clean()

    def deuda_actual(self):
        total=0
        pagos_asociados = PagosVentas.objects.filter(cliente=self.cliente,cancelado=False)
        for pago in pagos_asociados:
            if pago.medio_de_pago.cuenta_corriente:
                total += pago.total

        return f'$ {" {:,.2f}".format(total)}'
           
    def seleccionado(self):
        total = 0
        pagos = self.pagos_ventas.all()
        for pago in pagos:
            total += pago.total
        return total
    

    def seleccionado_actualizado(self):
        deuda_actualizada=0
        porcentual = 1
        pagos = self.pagos_ventas.all()
        for pago in pagos:
            total=float(pago.venta.get_cart_total)
            if total > 0:
                porcentual = float(pago.venta.pagos_en_cuenta_corriente) /  float(total)
            productos = pago.venta.detalleventa_set.all()
            for producto in productos:
                deuda_actualizada += float(producto.get_total_actualizado) * float(porcentual)

        return deuda_actualizada

    def obtener_pagos(self):
        pagos_info = []
        pagos = self.pagos_ventas.all()
        for pago in pagos:
            pago_real = pago.total
            venta = pago.venta.id
            pago_actualizado = pago.get_total_actualizado
            pagos_info.append((venta,pago_real, pago_actualizado))
        return pagos_info