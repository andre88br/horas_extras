# Generated by Django 4.1.7 on 2023-05-23 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pos_calculo", "0007_relatoriorubricaslancadas"),
    ]

    operations = [
        migrations.AlterField(
            model_name="relatoriobancosrecalculados",
            name="nome",
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name="relatoriobatidasrejeitadas",
            name="nome",
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name="relatoriorubricaslancadas",
            name="nome",
            field=models.CharField(max_length=200),
        ),
    ]
