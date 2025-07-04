# Generated by Django 4.2 on 2025-07-01 18:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('calculadora', '0014_merge_20250630_1827'),
    ]

    operations = [
        migrations.CreateModel(
            name='GranMHistorial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(max_length=10)),
                ('funcion_objetivo', models.TextField()),
                ('restricciones', models.TextField()),
                ('signos', models.TextField()),
                ('resultado_html', models.TextField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
