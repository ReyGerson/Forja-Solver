# Generated by Django 4.2 on 2025-06-23 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculadora', '0008_splinehistory_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='puntofijohistorial',
            name='despeje_latex',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='puntofijohistorial',
            name='funcion_latex',
            field=models.TextField(blank=True, null=True),
        ),
    ]
