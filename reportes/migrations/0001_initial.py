# Generated by Django 5.0.7 on 2024-09-02 23:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('agenda', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReporteMensual',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('caja_anterior', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('deuda_clientes_anterior', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('deuda_proveedores_anterior', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('total_ventas_cobradas', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('total_ventas_cc', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('total_ventas', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('total_gastos', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('deuda_clientes', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('deuda_proveedores', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('caja_final', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('deuda_clientes_final', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('deuda_proveedores_final', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('estado', models.BooleanField(default=False)),
                ('cierre_manual', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ReporteCaja',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('efectivo_inicial', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('efectivo_declarado', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('total_ventas_efectivo', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('total_ventas_virtuales', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('total_ventas_cc', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('total_ventas', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('cobrado_clientes', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('pagado_a_proveedores', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=25, null=True)),
                ('estado', models.BooleanField(default=False)),
                ('comentarios', models.CharField(blank=True, max_length=255, null=True)),
                ('caja', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agenda.caja')),
            ],
        ),
    ]
