from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

# Importamos modelos originales
from venta.models import Venta, DetalleVenta, PagosVentas
from producto.models import Producto
from agenda.models import Caja, medioDePago

class AjusteVenta(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        help_text="Seleccione la venta a ajustar."
    )
    nueva_fecha = models.DateTimeField(
        null=True, blank=True,
        help_text="(Opcional) Nueva fecha para la venta."
    )
    caja = models.ForeignKey(
        Caja,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="Seleccione la caja que se asignará como vendedor (se asigna a 'nombre_factura')."
    )
    confirmado = models.BooleanField(
        default=False,
        help_text="Indica si el ajuste ha sido confirmado y aplicado."
    )
    fecha_confirmacion = models.DateTimeField(
        null=True, blank=True,
        help_text="Fecha en la que se confirmó el ajuste."
    )

    def total_productos(self):
        """Suma el total de cada item (detalle) presente en el ajuste."""
        return sum([d.total() for d in self.detalles.all()])

    @property
    def nuevo_total(self):
        """Alias para total_productos, usado para mostrar el total actualizado."""
        return self.total_productos()

    def total_pagos(self):
        """Suma el total de cada pago ingresado en el ajuste."""
        return sum([p.total for p in self.pagos.all()])

    def clean(self):
        if self.venta.estado in [Venta.ESTADO_CANCELADA, Venta.ESTADO_ANULADA]:
            raise ValidationError("No se puede ajustar una venta cancelada o anulada.")
        super().clean()

    def copiar_datos_venta(self):
        """
        Copia los items (DetalleVenta) y pagos (PagosVentas) de la venta original
        al ajuste (solo si aún no se han copiado).
        """
        if not self.detalles.exists():
            for dv in self.venta.detalleventa_set.all():
                AjusteDetalleVenta.objects.create(
                    ajuste=self,
                    producto=dv.producto,
                    cantidad=dv.cantidad,
                    cantidad_producto=dv.cantidad_producto,
                    unidad_de_medida=dv.unidad_de_medida,
                    precio=dv.precio,  # En este caso se copia el precio actual.
                    base=dv.base,
                    altura=dv.altura
                )
        if not self.pagos.exists():
            for pv in PagosVentas.objects.filter(venta=self.venta):
                AjustePagosVenta.objects.create(
                    ajuste=self,
                    medio_de_pago=pv.medio_de_pago,
                    total=pv.total,
                    fecha=pv.fecha
                )

    def confirmar_ajuste(self):
        """
        Aplica el ajuste a la venta:
          1. Valida que el total de pagos coincida con el total (nuevo_total).
          2. Actualiza la fecha (si se modificó) y el total de la venta.
          3. Actualiza 'nombre_factura' asignándolo al valor de la Caja (como string).
          4. Reemplaza los items y pagos de la venta por los definidos en el ajuste.
        """
        if self.nuevo_total != self.total_pagos():
            raise ValidationError("El total de pagos no concuerda con el total de productos.")

        # Actualizar datos de la venta
        if self.nueva_fecha:
            self.venta.fecha = self.nueva_fecha
        if self.caja:
            self.venta.nombre_factura = str(self.caja)
        self.venta.total = self.nuevo_total
        self.venta.save()

        # Reemplazar los detalles (items)
        self.venta.detalleventa_set.all().delete()
        for detalle in self.detalles.all():
            dv = DetalleVenta.objects.create(
                venta=self.venta,
                producto=detalle.producto,
                cantidad=detalle.cantidad,
                cantidad_producto=detalle.cantidad_producto,
                unidad_de_medida=detalle.unidad_de_medida,
                precio=detalle.precio,
                base=detalle.base,
                altura=detalle.altura,
                # Intenta asignar la fecha, pero si auto_now_add está activo, no se usará
                fecha=self.nueva_fecha.date() if self.nueva_fecha else self.venta.fecha.date()
            )
            # Actualizar la fecha si es necesario (si no se asignó en la creación)
            if self.nueva_fecha:
                DetalleVenta.objects.filter(id=dv.id).update(fecha=self.nueva_fecha.date())

        # Reemplazar los pagos
        PagosVentas.objects.filter(venta=self.venta).delete()
        for pago in self.pagos.all():
            PagosVentas.objects.create(
                venta=self.venta,
                cliente=self.venta.cliente,
                medio_de_pago=pago.medio_de_pago,
                total=pago.total,
                fecha=self.nueva_fecha.date() if self.nueva_fecha else self.venta.fecha.date(),
                cancelado=False,
                adicional_cc=False,
            )
        self.confirmado = True
        self.fecha_confirmacion = timezone.now()
        self.save()

    def __str__(self):
        return f"Ajuste para Venta {self.venta.codigo} - Confirmado: {self.confirmado}"


class AjusteDetalleVenta(models.Model):
    """
    Representa un item de la venta dentro del ajuste.
    Se copian los datos originales y se muestran como readonly.
    Se permite eliminarlos para reducir el total.
    """
    ajuste = models.ForeignKey(AjusteVenta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=25, decimal_places=2, default=1)
    cantidad_producto = models.DecimalField(max_digits=25, decimal_places=2, default=1)
    unidad_de_medida = models.CharField(max_length=50, default="Unidades")
    precio = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    base = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)
    altura = models.DecimalField(max_digits=25, decimal_places=2, null=True, blank=True)

    def total(self):
        return self.cantidad * self.precio

    def __str__(self):
        return f"{self.producto} - Cant: {self.cantidad} - Precio: {self.precio}"


class AjustePagosVenta(models.Model):
    """
    Representa un pago asociado al ajuste.
    Permite modificar el medio de pago y el monto (y la fecha).
    """
    ajuste = models.ForeignKey(AjusteVenta, on_delete=models.CASCADE, related_name='pagos')
    medio_de_pago = models.ForeignKey(medioDePago, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=25, decimal_places=2)
    fecha = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.medio_de_pago} - Pago: {self.total}"
