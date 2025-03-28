# Generated by Django 5.0.7 on 2024-09-02 23:42

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('agenda', '0001_initial'),
        ('producto', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Compra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(default=django.utils.timezone.now)),
                ('total', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('estado', models.BooleanField(default=False)),
                ('compra_inicial', models.BooleanField(default=False)),
                ('Deposito', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='agenda.deposito', verbose_name='Deposito ingreso')),
                ('proveedor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='agenda.proveedor', verbose_name='Proveedor')),
            ],
        ),
        migrations.CreateModel(
            name='detalleCompra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Fecha', models.DateField(auto_now_add=True)),
                ('Cantidad', models.DecimalField(decimal_places=3, default=1, max_digits=25)),
                ('Precio', models.DecimalField(decimal_places=3, default=0, max_digits=25)),
                ('Descuento', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Desc (%)')),
                ('Total', models.DecimalField(decimal_places=2, default=0, max_digits=25)),
                ('ActualizarCosto', models.BooleanField(default=True)),
                ('Compra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compra.compra')),
                ('Deposito', models.ForeignKey(blank=True, default='general', null=True, on_delete=django.db.models.deletion.PROTECT, to='agenda.deposito', verbose_name='Deposito ingreso')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='producto.producto')),
            ],
            options={
                'verbose_name': 'detalle de comrpa',
                'verbose_name_plural': 'Productos comprados',
            },
        ),
        migrations.CreateModel(
            name='FleteCompra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('importe', models.DecimalField(decimal_places=2, default=0, max_digits=25)),
                ('compra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compra.compra')),
            ],
        ),
        migrations.CreateModel(
            name='medioDePagoCompra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(auto_now_add=True, null=True)),
                ('Total', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('cancelado', models.BooleanField(default=True)),
                ('Compra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compra.compra')),
                ('Cuenta', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='agenda.mediodecompra', verbose_name='medio de pago')),
            ],
            options={
                'verbose_name': 'pago',
                'verbose_name_plural': 'Pagos de compras',
            },
        ),
        migrations.CreateModel(
            name='PagosProveedores',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(auto_now_add=True, null=True)),
                ('estado', models.BooleanField(default=False)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=25, null=True)),
                ('medio_de_pago', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='agenda.mediodepago')),
                ('pagos_pendientes', models.ManyToManyField(blank=True, related_name='pagos_proveedores', to='compra.mediodepagocompra', verbose_name='Pagos adeudados')),
                ('proveedor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='agenda.proveedor')),
            ],
            options={
                'verbose_name': 'pago',
                'verbose_name_plural': 'Pago a proveedores',
            },
        ),
    ]
