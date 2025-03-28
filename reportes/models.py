import datetime
from django.db import models
from django.forms import ValidationError
from compra.models import PagosProveedores, medioDePagoCompra
from venta.models import DetalleVenta, PagosClientes,PagosVentas
from agenda.models import Caja, Gasto
from dateutil.relativedelta import relativedelta
from django.utils import timezone

MESES = [
    ("ENERO","ENERO"),
    ("FEBRERO","FEBRERO"),
    ("MARZO","MARZO"),
    ("ABRIL","ABRIL"),
    ("MAYO","MAYO"),
    ("JUNIO","JUNIO"),
    ("JULIO","JULIO"),
    ("AGOSTO","AGOSTO"),
    ("SEPTIEMBRE","SEPTIEMBRE"),
    ("OCTUBRE","OCTUBRE"),
    ("NOVIEMBRE","NOVIEMBRE"),
    ("DICIEMBRE","DICIEMBRE"),
]

class ReporteMensual(models.Model):
    fecha = models.DateField(default=timezone.now)

    caja_anterior = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0)
    deuda_clientes_anterior = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0)
    deuda_proveedores_anterior = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0)

    total_ventas_cobradas = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0)
    total_ventas_cc = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0)
    total_ventas = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0)

    total_gastos = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0)

    deuda_clientes = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0)
    deuda_proveedores = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0)

    caja_final = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0)
    deuda_clientes_final = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0)
    deuda_proveedores_final = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0)

    estado = models.BooleanField(default=False)
    cierre_manual = models.BooleanField(default=False)

    def __str__(self):
        return f'Reporte Mensual | {self.fecha.month}/{self.fecha.year}'
     
    def clean(self):
        if self.estado == True:
            raise ValidationError("Este reporte ya se encuentra confirmado, no se puede modificar.")
        super().clean()
    

    def save(self, *args, **kwargs):
        
        
        
        total_ventas_cobradas = 0
        total_ventas_cc = 0
        total_ventas = 0
        total_gastos = 0

        mes_ant = self.fecha - relativedelta(months=1)

        cierre_enterior = ReporteMensual.objects.filter(
            fecha__month=mes_ant.month
        ).first()

        if cierre_enterior:
            self.caja_anterior = cierre_enterior.caja_final
            self.deuda_clientes_anterior = cierre_enterior.deuda_clientes_final
            self.deuda_proveedores_anterior = cierre_enterior.deuda_proveedores_final
        else:
            self.caja_anterior = 0
            self.deuda_clientes_anterior = 0
            self.deuda_proveedores_anterior = 0

        # calculo de pagos 
        pagos = PagosVentas.objects.filter(
            venta__estado=3,
            fecha__month=self.fecha.month,
        )
        for pago in pagos:
            if pago.medio_de_pago.cuenta_corriente:
                total_ventas_cc+=pago.total
            else:
                total_ventas_cobradas+=pago.total
            total_ventas +=pago.total

        if self.cierre_manual == False:
            self.total_ventas_cobradas=total_ventas_cobradas
            self.total_ventas_cc=total_ventas_cc
            self.total_ventas=total_ventas
        else:
            self.total_ventas=self.total_ventas_cc + self.total_ventas_cobradas

        # Calculos de gastos
        gastos = Gasto.objects.filter(
            fecha__month=self.fecha.month,
        )
        for gasto in gastos:
            total_gastos +=gasto.total
        
        if self.cierre_manual == False:
            self.total_gastos=total_gastos

        self.caja_final = self.caja_anterior + self.total_ventas_cobradas - self.total_gastos
        self.deuda_clientes_final = self.deuda_clientes_anterior + self.deuda_clientes
        self.deuda_proveedores_final = self.deuda_proveedores_anterior + self.deuda_proveedores

        super(ReporteMensual, self).save(*args, **kwargs)
    

class ReporteCaja(models.Model):
    fecha = models.DateField(default=timezone.now,
                            help_text='Seleccione la fecha que desea obtener el reporte.')
    
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE,blank=False,null=False,
                            help_text='Seleccione la caja a obtener el reporte.')
    
    efectivo_inicial = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0,
                            help_text='Ingrese el dinero efectivo inicial de la caja.')
    
    efectivo_declarado = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0,
                            help_text='Ingrese el dinero en efectivo que tiene al final del dia.')
    
    total_ventas_efectivo = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0,
                            help_text='Importe total de las ventas cobradas en efectivo.')
    total_ventas_virtuales = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0,
                            help_text='Importe total de las ventas cobradas en cuentas virtuales y otros.')
    total_ventas_cc = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0,
                            help_text='Importe total de vendido en Cuentas Corrientes (Deuda de clientes)')
    total_ventas = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0,
                            help_text='Total de Ventas General del dia.')

    total_compras_efectivo = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0,
                            help_text='Importe comprado en efectivo.')
    total_compras_virtuales = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0,
                            help_text='Importe compradoen cuentas virtuales y otros.')
    total_compras_cc = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0,
                            help_text='Importe comprado en Cuentas Corrientes (Deuda con proveedor)')
    total_compras = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0,
                            help_text='Total de Compras General del dia.')

    cobrado_clientes_efectivo = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0,
                            help_text='Cobros de cuentas corrientes de Clientes con dinero en Efectivo')
    cobrado_clientes_otros = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0,
                            help_text='Cobros de cuentas corrientes de Clientes en Medios de pagos Virtuales/Otros') 

    pagado_proveedores_efectivo = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0,
                            help_text='Pagos de cuentas corrientes a Proveedores con dinero en Efectivo)')
    pagado_proveedores_otros = models.DecimalField(max_digits=25,decimal_places=2,blank=True,null=True,default=0,
                            help_text='Pagos de cuentas corrientes a Proveedores con Medios de pagos Virtuales/Otros')
    
    estado = models.BooleanField(default=False)
    comentarios = models.CharField(max_length=255,blank=True,null=True)

    def __str__(self):
        return f'{self.fecha} | {self.caja}'
     
    def clean(self):
        if self.estado == True:
            raise ValidationError("Este reporte ya se encuentra confirmado, no se puede modificar.")
        super().clean()
    

    def save(self, *args, **kwargs):

        total_ventas_virtuales = 0
        total_ventas_efectivo = 0
        total_ventas_cc = 0
        total_ventas = 0

        total_compras_virtuales = 0
        total_compras_efectivo = 0
        total_compras_cc = 0
        total_compras = 0

        total_cobrado_clientes_efectivo = 0
        total_cobrado_clientes_otros = 0
        total_pagado_proveedores_efectivo = 0
        total_pagado_proveedores_otros = 0


        pagos = PagosVentas.objects.filter(
            venta__estado=3,
            fecha=self.fecha,
            venta__nombre_factura=self.caja.Nombre
        )

        for pago in pagos:
            if pago.medio_de_pago.cuenta_corriente:
                total_ventas_cc+=pago.total
            else:
                if pago.medio_de_pago.efectivo:
                    total_ventas_efectivo +=pago.total
                else:
                    total_ventas_virtuales +=pago.total

            total_ventas +=pago.total


        pagos_compras = medioDePagoCompra.objects.filter(
            Compra__estado=True,
            fecha=self.fecha,
            Compra__caja=self.caja
        )

        for pago in pagos_compras:
            if pago.Cuenta.cuenta_corriente:
                total_compras_cc+=pago.Total
            else:
                if pago.Cuenta.efectivo:
                    total_compras_efectivo +=pago.Total
                else:
                    total_compras_virtuales +=pago.Total

            total_compras +=pago.Total

        pagos = PagosClientes.objects.filter(
            caja=self.caja,
            fecha=self.fecha,
            estado=True
        )
        
        for pago in pagos:
            if pago.medio_de_pago.efectivo == True:
                total_cobrado_clientes_efectivo+=pago.total
            else:
                total_cobrado_clientes_otros+=pago.total


        pagos_a_proveedores = PagosProveedores.objects.filter(
            estado=True,
            fecha=self.fecha,
            caja=self.caja,
        )
        for pagado in pagos_a_proveedores:
            if pagado.medio_de_pago.efectivo:
                total_pagado_proveedores_efectivo += pagado.total
            else:
                total_pagado_proveedores_otros += pagado.total


        self.total_ventas_efectivo=total_ventas_efectivo
        self.total_ventas_virtuales=total_ventas_virtuales
        self.total_ventas_cc=total_ventas_cc
        self.total_ventas=total_ventas

        self.total_compras_efectivo=total_compras_efectivo
        self.total_compras_virtuales=total_compras_virtuales
        self.total_compras_cc=total_compras_cc
        self.total_compras=total_compras
        
        self.cobrado_clientes_efectivo = total_cobrado_clientes_efectivo
        self.cobrado_clientes_otros = total_cobrado_clientes_otros
        self.pagado_proveedores_efectivo = total_pagado_proveedores_efectivo
        self.pagado_proveedores_otros = total_pagado_proveedores_otros

        super(ReporteCaja, self).save(*args, **kwargs)
    
    def resultado(self):

        dinero_inicial = float(self.efectivo_inicial or 0)

        ventas = float(self.total_ventas_efectivo or 0)
        cobro_de_ventas = float(self.cobrado_clientes_efectivo or 0)  

        compras = float(self.total_compras_efectivo or 0)
        pagos_a_proveedores = float(self.pagado_proveedores_efectivo or 0) 

        declarado = float(self.efectivo_declarado or 0)

        resultado = float(dinero_inicial + ventas + cobro_de_ventas - compras - pagos_a_proveedores - declarado)

        return resultado
