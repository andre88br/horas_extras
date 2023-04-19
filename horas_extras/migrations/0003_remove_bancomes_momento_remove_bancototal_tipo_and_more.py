# Generated by Django 4.1.7 on 2023-04-04 23:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("horas_extras", "0002_remove_bancomes_ano_remove_bancomes_mes_and_more"),
    ]

    operations = [
        migrations.RemoveField(model_name="bancomes", name="momento",),
        migrations.RemoveField(model_name="bancototal", name="tipo",),
        migrations.AddField(
            model_name="frequencia",
            name="data_upload",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 4, 4, 23, 56, 40, 233170)
            ),
        ),
        migrations.AddField(
            model_name="frequencia",
            name="importado_por",
            field=models.CharField(default=0, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="frequencia",
            name="importado_por_id",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]