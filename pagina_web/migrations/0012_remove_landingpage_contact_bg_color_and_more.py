# Generated by Django 4.0.1 on 2024-12-15 15:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pagina_web', '0011_landingpage_contact_bg_color_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='landingpage',
            name='contact_bg_color',
        ),
        migrations.RemoveField(
            model_name='landingpage',
            name='contact_font_color',
        ),
        migrations.RemoveField(
            model_name='landingpage',
            name='location_bg_color',
        ),
        migrations.RemoveField(
            model_name='landingpage',
            name='location_font_color',
        ),
        migrations.RemoveField(
            model_name='landingpage',
            name='map_image',
        ),
    ]
