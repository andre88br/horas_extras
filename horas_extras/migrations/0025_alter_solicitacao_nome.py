# Generated by Django 4.1.7 on 2023-04-28 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("horas_extras", "0024_alter_confirmacao_nome"),
    ]

    operations = [
        migrations.AlterField(
            model_name="solicitacao",
            name="nome",
            field=models.CharField(max_length=150),
        ),
    ]
