# Generated by Django 4.1.7 on 2023-05-23 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("relatorios", "0012_alter_relatorioconfirmacao_nome_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="relatorioconfirmacao",
            name="nome",
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name="relatorioentradasaida",
            name="nome",
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name="relatorioerros",
            name="nome",
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name="relatorionegativos",
            name="nome",
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name="relatoriopagas",
            name="nome",
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name="relatoriorejeitarbatidas",
            name="nome",
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name="relatoriosolicitacao",
            name="nome",
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name="voltarnegativos",
            name="nome",
            field=models.CharField(max_length=200),
        ),
    ]
