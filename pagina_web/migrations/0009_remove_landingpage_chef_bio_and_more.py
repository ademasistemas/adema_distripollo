# Generated by Django 4.0.1 on 2024-12-15 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagina_web', '0008_rename_featured_dish1_description_landingpage_especialidades_dish1_description_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='landingpage',
            name='chef_bio',
        ),
        migrations.RemoveField(
            model_name='landingpage',
            name='chef_image',
        ),
        migrations.RemoveField(
            model_name='landingpage',
            name='chef_name',
        ),
        migrations.RemoveField(
            model_name='landingpage',
            name='chef_title',
        ),
        migrations.RemoveField(
            model_name='landingpage',
            name='event1_description',
        ),
        migrations.RemoveField(
            model_name='landingpage',
            name='event1_image',
        ),
        migrations.RemoveField(
            model_name='landingpage',
            name='event1_title',
        ),
        migrations.RemoveField(
            model_name='landingpage',
            name='event2_description',
        ),
        migrations.RemoveField(
            model_name='landingpage',
            name='event2_image',
        ),
        migrations.RemoveField(
            model_name='landingpage',
            name='event2_title',
        ),
        migrations.RemoveField(
            model_name='landingpage',
            name='event3_description',
        ),
        migrations.RemoveField(
            model_name='landingpage',
            name='event3_image',
        ),
        migrations.RemoveField(
            model_name='landingpage',
            name='event3_title',
        ),
        migrations.RemoveField(
            model_name='landingpage',
            name='events_title',
        ),
        migrations.RemoveField(
            model_name='landingpage',
            name='gallery_images',
        ),
        migrations.RemoveField(
            model_name='landingpage',
            name='gallery_title',
        ),
        migrations.AddField(
            model_name='landingpage',
            name='testimonials_bg_color',
            field=models.CharField(default='#f0f0f0', help_text='Color de fondo en formato hexadecimal (ejemplo: #f0f0f0)', max_length=7),
        ),
        migrations.AddField(
            model_name='landingpage',
            name='testimonials_font_color',
            field=models.CharField(default='#000000', help_text='Color del texto en formato hexadecimal (ejemplo: #000000)', max_length=7),
        ),
    ]
