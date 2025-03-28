# Generated by Django 4.0.1 on 2024-12-17 13:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('producto', '0002_producto_mostrar_producto_tipo_recetaproducto'),
        ('venta', '0009_alter_venta_estado'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductoCompuestoVendido',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=20)),
                ('producto_compuesto', models.ForeignKey(limit_choices_to={'tipo': 'Compuesto'}, on_delete=django.db.models.deletion.CASCADE, to='producto.producto')),
                ('venta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productos_compuestos_vendidos', to='venta.venta')),
            ],
        ),
        migrations.CreateModel(
            name='ProductosIncluidosVendidos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.DecimalField(decimal_places=2, max_digits=20)),
                ('costo_unitario', models.DecimalField(decimal_places=2, max_digits=20)),
                ('producto_compuesto_vendido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productos_incluidos', to='venta.productocompuestovendido')),
                ('producto_usado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles_vendidos', to='producto.producto')),
            ],
        ),
    ]
