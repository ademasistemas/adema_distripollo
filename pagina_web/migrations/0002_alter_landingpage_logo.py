# Generated by Django 4.0.1 on 2024-12-15 03:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagina_web', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='landingpage',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
