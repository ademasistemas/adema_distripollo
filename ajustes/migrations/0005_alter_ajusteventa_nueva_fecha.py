# Generated by Django 5.0.11 on 2025-02-13 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ajustes', '0004_ajusteventa_caja_alter_ajustedetalleventa_precio_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ajusteventa',
            name='nueva_fecha',
            field=models.DateTimeField(blank=True, help_text='(Opcional) Nueva fecha para la venta.', null=True),
        ),
    ]
