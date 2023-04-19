# Generated by Django 4.1.7 on 2023-04-04 21:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Importacoes",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("data_upload", models.DateTimeField()),
                ("importado_por_id", models.IntegerField()),
                ("importado_por", models.CharField(max_length=100)),
                ("mes", models.CharField(max_length=15)),
                ("ano", models.IntegerField()),
                ("tipo", models.CharField(max_length=20)),
            ],
            options={"unique_together": {("tipo", "mes", "ano")},},
        ),
        migrations.CreateModel(
            name="Empregado",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("matricula", models.IntegerField()),
                ("nome", models.CharField(max_length=100)),
                ("salario", models.FloatField()),
                ("insalubridade", models.FloatField()),
                ("data_atualizacao", models.DateTimeField()),
                ("mes", models.CharField(max_length=15)),
                ("ano", models.IntegerField()),
                (
                    "importacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="empregados.importacoes",
                    ),
                ),
            ],
            options={"unique_together": {("matricula", "mes", "ano")},},
        ),
        migrations.CreateModel(
            name="CargaHoraria",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nome", models.CharField(max_length=100)),
                ("carga_horaria", models.FloatField()),
                ("importado_por", models.CharField(max_length=100)),
                ("importado_por_id", models.IntegerField()),
                ("mes", models.CharField(max_length=15)),
                ("ano", models.IntegerField()),
                (
                    "empregado",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="empregados.empregado",
                    ),
                ),
                (
                    "importacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="empregados.importacoes",
                    ),
                ),
            ],
        ),
    ]
