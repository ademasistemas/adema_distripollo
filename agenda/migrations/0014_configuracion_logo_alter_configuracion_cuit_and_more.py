# Generated by Django 5.0.11 on 2025-02-13 03:17

import agenda.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0013_cliente_correo_electronico_alter_cliente_direccion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracion',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='img/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']), agenda.models.validate_image_size]),
        ),
        migrations.AlterField(
            model_name='configuracion',
            name='cuit',
            field=models.CharField(blank=True, help_text='Esta información aparecerá en el ticket de venta (Dejar vacío si no se requiere)', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='configuracion',
            name='direccion',
            field=models.CharField(blank=True, help_text='Esta información aparecerá en el ticket de venta', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='configuracion',
            name='nombre',
            field=models.CharField(blank=True, help_text='Esta información aparecerá en el ticket de venta', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='configuracion',
            name='telefono',
            field=models.CharField(blank=True, help_text='Esta información aparecerá en el ticket de venta', max_length=255, null=True),
        ),
    ]
