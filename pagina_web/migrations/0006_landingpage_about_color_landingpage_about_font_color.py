# Generated by Django 4.0.1 on 2024-12-15 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagina_web', '0005_landingpage_telefono_landingpage_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='landingpage',
            name='about_color',
            field=models.CharField(default='#f0f0f0', help_text='Color de fondo en formato hexadecimal (ejemplo: #f0f0f0)', max_length=7),
        ),
        migrations.AddField(
            model_name='landingpage',
            name='about_font_color',
            field=models.CharField(default='#000000', help_text='Color del texto en formato hexadecimal (ejemplo: #000000)', max_length=7),
        ),
    ]
