# Generated by Django 5.0.11 on 2025-02-13 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compra', '0009_detallecompra_unidad_de_medida'),
    ]

    operations = [
        migrations.AddField(
            model_name='detallecompra',
            name='costo_unitario_producto',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=25),
        ),
    ]
