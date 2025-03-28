# Generated by Django 5.0.7 on 2024-09-02 23:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Caja',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nombre', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'punto',
                'verbose_name_plural': 'Puntos de venta',
            },
        ),
        migrations.CreateModel(
            name='categoria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Descripcion', models.CharField(max_length=120, unique=True)),
            ],
            options={
                'verbose_name': 'categoria',
                'verbose_name_plural': 'Categorias',
            },
        ),
        migrations.CreateModel(
            name='Chofer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(blank=True, max_length=255, null=True)),
                ('vehiculo', models.CharField(blank=True, max_length=255, null=True)),
                ('patente', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'chofer',
                'verbose_name_plural': 'Lista de Choferes',
            },
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(blank=True, max_length=200, null=True, unique=True, verbose_name='documento')),
                ('nombre', models.CharField(blank=True, max_length=200, null=True)),
                ('telefono', models.CharField(blank=True, default=1, max_length=20, null=True)),
                ('direccion', models.EmailField(blank=True, max_length=200, null=True, verbose_name='Correo')),
                ('cbu', models.CharField(blank=True, max_length=200, null=True)),
                ('habilitar_cc', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='deposito',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nombre', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'deposito',
                'verbose_name_plural': 'Depositos',
            },
        ),
        migrations.CreateModel(
            name='medioDeCompra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nombre', models.CharField(blank=True, max_length=200, null=True)),
                ('cuenta_corriente', models.BooleanField(default=False)),
                ('efectivo', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'medio de compra',
                'verbose_name_plural': 'Medios de compra',
            },
        ),
        migrations.CreateModel(
            name='medioDePago',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nombre', models.CharField(blank=True, max_length=200, null=True)),
                ('cuenta_corriente', models.BooleanField(default=False)),
                ('efectivo', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'medio de pago',
                'verbose_name_plural': 'Medios de pago',
            },
        ),
        migrations.CreateModel(
            name='Monedas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nombre', models.CharField(default='Pesos', max_length=255, unique=True)),
                ('Abreviacion', models.CharField(default='$', max_length=3, unique=True, verbose_name='Signo')),
            ],
        ),
        migrations.CreateModel(
            name='PrecioPorKilometro',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.DecimalField(decimal_places=2, max_digits=20)),
            ],
        ),
        migrations.CreateModel(
            name='Proveedor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Empresa', models.CharField(blank=True, max_length=120, null=True)),
                ('NombreApellido', models.CharField(blank=True, max_length=120, null=True)),
                ('Direccion', models.CharField(blank=True, max_length=120, null=True)),
                ('Email', models.EmailField(blank=True, max_length=254, null=True)),
                ('Telefono', models.CharField(blank=True, max_length=120, null=True)),
            ],
            options={
                'verbose_name': 'proveedor',
                'verbose_name_plural': 'Proveedores',
            },
        ),
        migrations.CreateModel(
            name='TipoGasto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=255, unique=True)),
                ('gasto_fijo', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Asignacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('caja', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='agenda.caja', verbose_name='Punto de venta')),
            ],
            options={
                'verbose_name': 'asignacion',
                'verbose_name_plural': 'asignacion',
            },
        ),
        migrations.AddField(
            model_name='caja',
            name='Deposito',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='agenda.deposito'),
        ),
        migrations.CreateModel(
            name='Configuracion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(blank=True, max_length=255, null=True)),
                ('direccion', models.CharField(blank=True, max_length=255, null=True)),
                ('telefono', models.CharField(blank=True, max_length=255, null=True)),
                ('nombre_cuenta', models.CharField(blank=True, max_length=255, null=True)),
                ('alias', models.CharField(blank=True, max_length=255, null=True)),
                ('contactos', models.CharField(blank=True, max_length=255, null=True, verbose_name='Campo libre')),
                ('cuit', models.CharField(blank=True, max_length=255, null=True)),
                ('tiket_comandera', models.BooleanField(default=True)),
                ('vista_clasica', models.BooleanField(default=True)),
                ('mostrar_foto', models.BooleanField(default=True)),
                ('entrega', models.BooleanField(default=False)),
                ('stock_negativo_ldp', models.BooleanField(default=False)),
                ('mostrar_productos_cocina_ldp', models.BooleanField(default=True)),
                ('mostrar_productos_cocina_tienda', models.BooleanField(default=True)),
                ('tipo_cambio', models.DecimalField(decimal_places=10, default=1, max_digits=25)),
                ('ventas_mayoristas', models.BooleanField(default=False)),
                ('mostrar_cocina', models.BooleanField(default=True)),
                ('entrega_ventas', models.BooleanField(default=False)),
                ('precio_venta_automatico', models.BooleanField(default=True)),
                ('Moneda', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='moneda_principal', to='agenda.monedas')),
                ('Moneda_secundaria', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='moneda_secundaria', to='agenda.monedas')),
            ],
            options={
                'verbose_name': 'configuracion',
                'verbose_name_plural': 'Confirguracion',
            },
        ),
        migrations.CreateModel(
            name='Gasto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(null=True)),
                ('descripcion', models.CharField(max_length=255)),
                ('total', models.DecimalField(decimal_places=2, max_digits=20)),
                ('categoria', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='agenda.tipogasto')),
            ],
        ),
    ]
