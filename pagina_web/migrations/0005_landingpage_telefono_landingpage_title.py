# Generated by Django 4.0.1 on 2024-12-15 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagina_web', '0004_remove_landingpage_logo1_landingpage_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='landingpage',
            name='telefono',
            field=models.CharField(default='541112345678', max_length=255),
        ),
        migrations.AddField(
            model_name='landingpage',
            name='title',
            field=models.CharField(default='Excel-ente', max_length=255),
        ),
    ]
