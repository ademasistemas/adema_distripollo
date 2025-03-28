# Generated by Django 5.0.11 on 2025-02-13 17:42

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venta', '0016_alter_pagosclientes_options_alter_venta_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detalleventa',
            name='fecha',
            field=models.DateField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='pagosventas',
            name='fecha',
            field=models.DateField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='venta',
            name='fecha',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
    ]
