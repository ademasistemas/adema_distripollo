# Generated by Django 5.0 on 2024-09-21 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venta', '0003_detalleventa_ganancias_estimadas'),
    ]

    operations = [
        migrations.AddField(
            model_name='detalleventa',
            name='total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=25, null=True),
        ),
    ]
