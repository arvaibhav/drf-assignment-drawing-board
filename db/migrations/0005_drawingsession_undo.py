# Generated by Django 4.2.4 on 2023-08-22 05:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0004_drawingboarduserchannel"),
    ]

    operations = [
        migrations.AddField(
            model_name="drawingsession",
            name="undo",
            field=models.BooleanField(default=False),
        ),
    ]
