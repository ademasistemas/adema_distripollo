# Generated by Django 5.0.11 on 2025-02-13 14:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0015_alter_configuracion_tiket_comandera'),
        ('ajustes', '0002_ajustepagosclientes_detalleajustepago_and_more'),
        ('producto', '0006_alter_producto_unidad_de_medida_and_more'),
        ('venta', '0016_alter_pagosclientes_options_alter_venta_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='detalleajustepago',
            name='ajuste',
        ),
        migrations.RemoveField(
            model_name='detalleajustepago',
            name='medio_de_pago',
        ),
        migrations.CreateModel(
            name='AjusteVenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nueva_fecha', models.DateTimeField(blank=True, help_text='Nueva fecha para la venta (se recalcularán los precios al día de hoy).', null=True)),
                ('confirmado', models.BooleanField(default=False, help_text='Indica si el ajuste ha sido confirmado y aplicado.')),
                ('fecha_confirmacion', models.DateTimeField(blank=True, help_text='Fecha en la que se confirmó el ajuste.', null=True)),
                ('venta', models.ForeignKey(help_text='Seleccione la venta a ajustar.', on_delete=django.db.models.deletion.CASCADE, to='venta.venta')),
            ],
        ),
        migrations.CreateModel(
            name='AjustePagosVenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.DecimalField(decimal_places=2, max_digits=25)),
                ('fecha', models.DateField(blank=True, help_text='Nueva fecha para el pago (usualmente la misma que la venta).', null=True)),
                ('medio_de_pago', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agenda.mediodepago')),
                ('ajuste', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='ajustes.ajusteventa')),
            ],
        ),
        migrations.CreateModel(
            name='AjusteDetalleVenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.DecimalField(decimal_places=2, default=1, max_digits=25)),
                ('cantidad_producto', models.DecimalField(decimal_places=2, default=1, max_digits=25)),
                ('unidad_de_medida', models.CharField(default='Unidades', max_length=50)),
                ('precio', models.DecimalField(blank=True, decimal_places=2, help_text='Nuevo precio del producto (se recalcula al día de hoy).', max_digits=25, null=True)),
                ('base', models.DecimalField(blank=True, decimal_places=2, max_digits=25, null=True)),
                ('altura', models.DecimalField(blank=True, decimal_places=2, max_digits=25, null=True)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='producto.producto')),
                ('ajuste', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='ajustes.ajusteventa')),
            ],
        ),
        migrations.DeleteModel(
            name='AjustePagosClientes',
        ),
        migrations.DeleteModel(
            name='DetalleAjustePago',
        ),
    ]
