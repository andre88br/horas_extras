# Generated by Django 4.1.7 on 2023-04-05 12:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("horas_extras", "0006_alter_frequencia_data_upload"),
    ]

    operations = [
        migrations.AlterField(
            model_name="frequencia",
            name="data_upload",
            field=models.DateTimeField(
                default=datetime.datetime(2023, 4, 5, 12, 50, 53, 914696)
            ),
        ),
    ]