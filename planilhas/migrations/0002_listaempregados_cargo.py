# Generated by Django 4.2.2 on 2023-06-15 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planilhas", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="listaempregados",
            name="cargo",
            field=models.CharField(default=0, max_length=30),
            preserve_default=False,
        ),
    ]
