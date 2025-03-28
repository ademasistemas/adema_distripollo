# Generated by Django 4.0.1 on 2024-12-15 00:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0005_alter_mediodecompra_nombre_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='configuracion',
            name='mostrar_productos_cocina_ldp',
        ),
        migrations.AddField(
            model_name='configuracion',
            name='permitir_venta_negativa',
            field=models.BooleanField(default=True, help_text='Permitir vender con stock negativo'),
        ),
    ]
