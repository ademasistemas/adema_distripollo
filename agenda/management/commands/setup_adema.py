from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from agenda.models import Configuracion, Monedas, deposito, medioDeCompra, medioDePago, Caja, Asignacion

class Command(BaseCommand):
    help = 'Configura el proyecto inicializando la base de datos y creando un superusuario.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Inicializando la base de datos...'))
        call_command('migrate')
        call_command('makemigrations') 
        call_command('migrate')

        # Creación de Superusuario
        self.stdout.write(self.style.SUCCESS('Creando un superusuario...'))
        User = get_user_model()
        if not User.objects.filter(username='EXCEL-ENTE').exists():
            username = 'EXCEL-ENTE'
            email = 'admin@example.com'
            password = 'Adema123.'
            superuser = User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superusuario creado: {username} / {password}'))
        else:
            superuser = User.objects.get(username='EXCEL-ENTE')
            self.stdout.write(self.style.WARNING('El superusuario ya existe.'))

        # Creación de moneda
        self.stdout.write(self.style.SUCCESS('Creando moneda "Pesos"...'))
        pesos_moneda, created = Monedas.objects.get_or_create(
            Nombre='Pesos',
            defaults={'Abreviacion': '$'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Moneda "Pesos" creada.'))
        else:
            self.stdout.write(self.style.WARNING('La moneda "Pesos" ya existe.'))

        # Creación de depósito
        self.stdout.write(self.style.SUCCESS('Creando depósito general...'))
        deposito_general, created1 = deposito.objects.get_or_create(
            Nombre='General',
        )
        if created1:
            self.stdout.write(self.style.SUCCESS('Depósito general creado.'))
        else:
            self.stdout.write(self.style.WARNING('Depósito general ya existe.'))

        # Creación de medio de compra
        self.stdout.write(self.style.SUCCESS('Creando Medio de Compra Efectivo...'))
        medio_compra_efectivo, created = medioDeCompra.objects.get_or_create(
            Nombre='Efectivo',
            cuenta_corriente=False,
            efectivo=True
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Medio de Compra Efectivo creado.'))
        else:
            self.stdout.write(self.style.WARNING('Medio de Compra Efectivo ya existe.'))

        self.stdout.write(self.style.SUCCESS('Creando Medio de Compra Cuenta Corriente...'))
        medio_compra_cc, created = medioDeCompra.objects.get_or_create(
            Nombre='Cuenta Corriente',
            cuenta_corriente=True,
            efectivo=False
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Medio de Compra Cuenta Corriente creado.'))
        else:
            self.stdout.write(self.style.WARNING('Medio de Compra Cuenta Corriente ya existe.'))


        # Creación de medio de pago
        self.stdout.write(self.style.SUCCESS('Creando Medio de Pago de Ventas Efectivo...'))
        medio_pago_efectivo, created = medioDePago.objects.get_or_create(
            Nombre='Efectivo',
            cuenta_corriente=False,
            efectivo=True
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Medio de Pago de Ventas creado.'))
        else:
            self.stdout.write(self.style.WARNING('Medio de Pago de Ventas ya existe.'))

        self.stdout.write(self.style.SUCCESS('Creando Medio de Pago de Ventas Cuenta Corriente...'))
        medio_pago_efectivo, created = medioDePago.objects.get_or_create(
            Nombre='Cuenta Corriente',
            cuenta_corriente=True,
            efectivo=False
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Medio de Pago de Ventas Cuenta Corriente creado.'))
        else:
            self.stdout.write(self.style.WARNING('Medio de Pago de Ventas Cuenta Corriente ya existe.'))

        # Creación de punto de venta
        self.stdout.write(self.style.SUCCESS('Creando Punto de Venta "Administrador"...'))
        caja_admin, created = Caja.objects.get_or_create(
            Nombre='Administrador',
            Deposito=deposito_general,
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Punto de Venta "Administrador" creado.'))
        else:
            self.stdout.write(self.style.WARNING('Punto de Venta "Administrador" ya existe.'))

        # Asignación del superusuario EXCEL-ENTE al Punto de Venta
        self.stdout.write(self.style.SUCCESS('Asignando Punto de Venta al superusuario EXCEL-ENTE...'))
        Asignacion.objects.get_or_create(
            usuario=superuser,
            caja=caja_admin
        )
        self.stdout.write(self.style.SUCCESS('Asignación del Punto de Venta completada.'))

        # Creación de Configuración de Empresa
        self.stdout.write(self.style.SUCCESS('Verificando configuración inicial...'))
        if not Configuracion.objects.filter(id=1).exists():
            Configuracion.objects.create(
                nombre='EXCEL-ENTE',
                direccion='Mi direccion de ejemplo 3216, Buenos aires',
                telefono='123456789',
                Moneda=pesos_moneda,
                Moneda_secundaria=pesos_moneda,
            )
            self.stdout.write(self.style.SUCCESS('Configuración inicial creada.'))
        else:
            self.stdout.write(self.style.WARNING('La configuración inicial ya existe.'))

        self.stdout.write(self.style.SUCCESS('Configuración del proyecto completada.'))
