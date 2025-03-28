from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


DECIMALES = [
    ('0', '0'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3')
]

meses = {
    1: "ENERO",
    2: "FEBRERO",
    3: "MARZO",
    4: "ABRIL",
    5: "MAYO",
    6: "JUNIO",
    7: "JULIO",
    8: "AGOSTO",
    9: "SEPTIEMBRE",
    10: "OCTUBRE",
    11: "NOVIEMBRE",
    12: "DICIEMBRE",
}

class Chofer(models.Model):
    nombre = models.CharField(max_length=255,blank=True,null=True)
    vehiculo = models.CharField(max_length=255,blank=True,null=True)
    patente =models.CharField(max_length=255,blank=True,null=True)

    def __str__(self):
        return self.nombre
    
    class Meta: # Metodo para nombrar el modelo
        verbose_name = 'chofer'  # Como se va a nombrar el objeto de la instancia
        verbose_name_plural ='Lista de Choferes' # Como se nombra el modelo

class Monedas(models.Model):
    Nombre = models.CharField(max_length=255,unique=True,blank=False,null=False,default="Pesos")
    Abreviacion = models.CharField(max_length=3,unique=True,blank=False,null=False,default="$",verbose_name="Signo")

    def __str__(self):
        return f'{self.Abreviacion}'

def validate_image_size(value):
        width, height = value.width, value.height
        if width != 500 or height != 500:
            raise ValidationError('El logo debe ser de 500x500 píxeles.')
        
TICKET_CHOICES = (
    ('A4', 'Ticket A4'),
    ('80mm', 'Ticket Comandera (80mm)'),
    ('58mm', 'Ticket 58mm'),
)
class Configuracion(models.Model):

    logo = models.ImageField(
        upload_to='img/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']), validate_image_size]
    )
    nombre = models.CharField(max_length=255,blank=True,null=True,help_text="Esta información aparecerá en el ticket de venta")
    direccion = models.CharField(max_length=255,blank=True,null=True,help_text="Esta información aparecerá en el ticket de venta")
    telefono = models.CharField(max_length=255,blank=True,null=True,help_text="Esta información aparecerá en el ticket de venta")
    cuit = models.CharField(max_length=255,blank=True,null=True,help_text="Esta información aparecerá en el ticket de venta (Dejar vacío si no se requiere)")
    nombre_cuenta = models.CharField(max_length=255, blank=True,verbose_name="Campo libre (Primera linea)",help_text="Si requiere agregar una linea de texto en el ticket de venta puede usar este campo (Dejar vacío si no se requiere)")
    alias = models.CharField(max_length=255,blank=True,null=True,verbose_name="Campo libre (Segunda linea)",help_text="Si requiere agregar una linea de texto en el ticket de venta puede usar este campo (Dejar vacío si no se requiere)")
    
    Moneda = models.ForeignKey(Monedas,verbose_name="💵 Moneda", on_delete=models.CASCADE, blank=False, null=False,default=1, related_name='moneda_principal',help_text="Seleccione la moneda que desea manejar en el sistema (Puede crear una nueva)")   
    Moneda_secundaria = models.ForeignKey(Monedas, on_delete=models.CASCADE, blank=False,default=1, null=False, related_name='moneda_secundaria')
    tipo_cambio = models.DecimalField(max_digits=25, decimal_places=10, default=1, blank=False, null=False)
    tiket_comandera = models.CharField(
        verbose_name="🖨️ Ticket A4", 
        choices=TICKET_CHOICES,
        max_length=255,
        default='80mm',
        help_text="Seleccione el formato del ticket para impresión: Ticket A4, Ticket Comandera (80mm) o Ticket 58mm."
        )
    
    vista_clasica = models.BooleanField(default=True,verbose_name="🖼️ Vista como Tarjetas",help_text="Si quiere que su tienda muestre los productos en forma de tarjeta, deje en Verdadero esta casilla.")
    mostrar_foto = models.BooleanField(default=True,verbose_name="📷 Mostrar Foto",help_text="Si quiere que se muestren las fotos de los productos en su tienda deje esta casilla en Veradero.")
    entrega = models.BooleanField(default=False,verbose_name="🚴🏻‍♂️ Gestionar Entrega",help_text="Esta opción agrega la acción de 'Entregar' cada venta, por lo que todas las ventas serán NO ENTREGADAS por defecto.")
    stock_negativo_ldp = models.BooleanField(default=True,verbose_name="📄 Ocultar productos sin Stock de la Lista de precios",help_text='Esta opción permite ocultar los productos con stock negativo desde la tienda')
    permitir_venta_negativa = models.BooleanField(default=True,verbose_name="🏪 Ocultar productos sin Stock de la tienda",help_text='Esta opción permite ocultar los productos con stock negativo desde la tienda')
    mostrar_productos_cocina_tienda = models.BooleanField(default=True)
    ventas_mayoristas = models.BooleanField(default=False)
    mostrar_cocina = models.BooleanField(default=True)
    mostrar_decimales = models.CharField(max_length=10, choices=DECIMALES, default=2, verbose_name="🖨️ Decimales en ticket",help_text="Ingrese la cantidad de decimales que desea mostrar en ticket.")
    precio_venta_automatico = models.BooleanField(default=True,verbose_name="🧮 Cálculo de precios",help_text="Si quiere que los precios de venta de tus productos se ingresen manualmente, deja esta casilla en True. (En Falso, los precios se calcularán en base a una % Rentabilidad)")


    def __str__(self):
        return self.nombre
    
    def clean(self):
        Configs = Configuracion.objects.count() or 0
        if Configs:
            config = Configuracion.objects.first()
            if self.id != config.pk:
                raise ValidationError("Ya existe la configuracion de la empresa.")

        super().clean()

    class Meta:
        verbose_name = 'configuracion' 
        verbose_name_plural ='Confirguracion' #

    
        
def formatear_fecha(fecha):
    dia = fecha.day
    mes_numero = fecha.month
    mes_nombre = meses[mes_numero]
    return f"{dia} De {mes_nombre}"

class Cliente(models.Model):
    codigo = models.CharField(verbose_name="documento",unique=True,max_length=200, null=True, blank=True)
    nombre = models.CharField(max_length=200, null=True, blank=True)
    telefono = models.CharField(max_length=30,default="1111-1111",blank=True,null=True)
    direccion = models.CharField(max_length=255,blank=True,null=True)
    correo_electronico = models.EmailField(max_length=200,blank=True,null=True)
    cbu = models.CharField(max_length=200, null=True, blank=True)
    habilitar_cc = models.BooleanField(default=False,verbose_name="Habilitar cuenta corriente" , help_text="Este check habilita al cliente todos los medios de pago que sean de tipo 'Cuenta Corriente'")
    
    def __str__(self):
        return self.nombre or "Sin nombre"
    
    def cuenta_corriente(self):
        from venta.models import PagosVentas
        total_deuda = 0
        deudas = PagosVentas.objects.filter(cliente=self, medio_de_pago__cuenta_corriente=True, cancelado=False)
        for deuda in deudas:
            if deuda.total > 0:
                total_deuda += deuda.total
        return total_deuda
    
class TipoGasto(models.Model):
    descripcion = models.CharField(max_length=255,unique=True,blank=False,null=False)
    gasto_fijo = models.BooleanField(default=False)

    def __str__(self):
        return self.descripcion
    
class Gasto(models.Model):
    fecha = models.DateField(blank=False,null=True)
    categoria = models.ForeignKey(TipoGasto,on_delete=models.SET_NULL,blank=False,null=True)
    descripcion = models.CharField(max_length=255, null=False, blank=False)
    total = models.DecimalField(max_digits=20,decimal_places=2,blank=False,null=False)

    def __str__(self):
        msg = f'{self.categoria} | {self.descripcion} | ${self.total}'
        return msg
       

    def total_calculado(fecha_inicial,fecha_final):

        total = 0
        gastos = Gasto.objects.filter(
            fecha__range=(fecha_inicial, fecha_final),
        )

        for gasto in gastos:
            total += gasto.total
            
        return total
    
    def total_fijo_calculado(fecha_inicial,fecha_final):

        total = 0
        gastos = Gasto.objects.filter(
            fecha__range=(fecha_inicial, fecha_final),
            categoria__gasto_fijo=True,
        )

        for gasto in gastos:
            total += gasto.total
            
        return total
    
class PrecioPorKilometro(models.Model):
    total = models.DecimalField(max_digits=20,decimal_places=2)
    def __str__(self):
        return f'PrecioxKm ${self.total}'

class deposito(models.Model):
    Nombre = models.CharField(max_length=100,unique=True,blank=False,null=False)

    def clean(self): # Metodo para verificar algun  campo antes de guardar.
        super().clean()

    def __str__(self): # Como se muestra el objeto en una relacion foranea
        return self.Nombre
    
    class Meta: # Metodo para nombrar el modelo
        verbose_name = 'deposito'  # Como se va a nombrar el objeto de la instancia
        verbose_name_plural ='Depositos' # Como se nombra el modelo

class medioDeCompra(models.Model):
    Nombre = models.CharField(max_length=200, null=True, blank=True,help_text='Nombre descriptivo para el método de pago que usarás para pagar las compras a proveedores.')
    cuenta_corriente = models.BooleanField(default=False,help_text='Esta casilla permite agrupar el medio de pago como DEUDA CON EL PROVEEDOR (Cuentas Corrientes)')
    efectivo = models.BooleanField(default=False,help_text='Si usted quiere tomar el metodo de pago como efectivo (Para el cierre de caja)')

    def clean(self):
        if self.cuenta_corriente == True and self.efectivo  == True:
            raise ValidationError('No puede seleccionar "cuenta corriente" y "efectivo" a la vez.')
        super().clean()

    def __str__(self): # Como se muestra el objeto en una relacion foranea
        return self.Nombre
    
    class Meta: # Metodo para nombrar el modelo
        verbose_name = 'medio de compra'  # Como se va a nombrar el objeto de la instancia
        verbose_name_plural ='Medios de compra' # Como se nombra el modelo

class medioDePago(models.Model):
    Nombre = models.CharField(max_length=200, null=True, blank=True,help_text='Nombre descriptivo para el método de pago que usarán los clientes para pagarte.')
    cuenta_corriente = models.BooleanField(default=False,help_text='Esta casilla permite agrupar el medio de pago como DEUDA DE CLIENTES (Cuentas Corrientes)')
    efectivo = models.BooleanField(default=False,help_text='Si usted quiere tomar el metodo de pago como efectivo (Para el cierre de caja)')

    def clean(self):
        if self.cuenta_corriente == True and self.efectivo  == True:
            raise ValidationError('No puede seleccionar "cuenta corriente" y "efectivo" a la vez.')
        super().clean()

    def __str__(self): 
        return self.Nombre
    
    class Meta: 
        verbose_name = 'medio de pago'
        verbose_name_plural ='Medios de pago' 

# -----------------------------------------------------------------------------
# Metodos para acceder a los valores de forma dinamica
class categoria(models.Model):
    Descripcion = models.CharField(max_length=120, null=False, blank=False,unique=True)

    def __str__(self):
        return self.Descripcion
    
    class Meta:
        verbose_name = 'categoria'  # Como se va a nombrar el objeto de la instancia
        verbose_name_plural ='Categorias' # Como se nombra el modelo

# -----------------------------------------------------------------------------
# Metodos para acceder a los valores de forma dinamica
# proveedor.pedidos()    ---> Devuelve la cantidad de compras confirmadas
# proveedor.cuenta_corriente()   ---> Devuelve el monto de la suma de los pagos a proveedores en c.c. menos los pagos en c.c.
class Proveedor(models.Model):
    Empresa=models.CharField(max_length=120,null=True,blank=True) 
    NombreApellido=models.CharField(max_length=120,null=True,blank=True) 
    Direccion=models.CharField(max_length=120,null=True,blank=True)
    Email=models.EmailField(null=True,blank=True)
    Telefono=models.CharField(max_length=120,null=True,blank=True)

    def __str__(self):
        return self.Empresa
    
    class Meta:
        verbose_name = 'proveedor' # Como se va a nombrar el objeto de la instancia
        verbose_name_plural ='Proveedores' # Como se nombra el modelo

    def pedidos():
        # Falta armar funcion
        pass

    def cuenta_corriente():
        # Falta armar funcion
        pass

class Caja(models.Model):
    Nombre = models.CharField(max_length=255,unique=True,blank=False,null=False)
    Deposito = models.ForeignKey(deposito,on_delete=models.CASCADE,blank=False,null=False,default=1)

    def __str__(self):
        return self.Nombre
    
    class Meta: # Metodo para nombrar el modelo
        verbose_name = 'caja'  # Como se va a nombrar el objeto de la instancia
        verbose_name_plural ='Caja' # Como se nombra el modelo

class Asignacion(models.Model):
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)
    caja = models.ForeignKey(Caja,on_delete=models.DO_NOTHING,blank=True,null=True,verbose_name="Punto de venta")
    
    def __str__(self):
        return self.usuario.first_name
    
    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuario'
        constraints = [
            models.UniqueConstraint(fields=['usuario'], name='unique_user_assignment')
        ]