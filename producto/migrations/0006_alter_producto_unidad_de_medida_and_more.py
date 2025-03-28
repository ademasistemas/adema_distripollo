# Generated by Django 5.0.11 on 2025-02-13 00:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('producto', '0005_alter_producto_unidad_de_medida_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='unidad_de_medida',
            field=models.CharField(choices=[('Unidades', 'Unidades'), ('Kilos', 'Kilos'), ('Gramos', 'Gramos'), ('Litros', 'Litros'), ('Mililitros', 'Mililitros'), ('Mt2', 'Mt²')], default='Unidades', max_length=50),
        ),
        migrations.AlterField(
            model_name='productoprecio',
            name='cantidad',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=20),
        ),
        migrations.AlterField(
            model_name='productoprecio',
            name='unidad_de_medida',
            field=models.CharField(choices=[('Unidades', 'Unidades'), ('Kilos', 'Kilos'), ('Gramos', 'Gramos'), ('Litros', 'Litros'), ('Mililitros', 'Mililitros'), ('Mt2', 'Mt²')], default='Unidades', max_length=50),
        ),
        migrations.AlterField(
            model_name='recetaproducto',
            name='unidad_de_medida',
            field=models.CharField(choices=[('Unidades', 'Unidades'), ('Kilos', 'Kilos'), ('Gramos', 'Gramos'), ('Litros', 'Litros'), ('Mililitros', 'Mililitros'), ('Mt2', 'Mt²')], default='Unidades', max_length=50),
        ),
    ]
