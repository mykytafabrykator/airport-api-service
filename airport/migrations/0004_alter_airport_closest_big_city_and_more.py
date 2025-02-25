# Generated by Django 5.1.6 on 2025-02-24 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("airport", "0003_airport_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="airport",
            name="closest_big_city",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name="airport",
            unique_together={("name", "closest_big_city")},
        ),
    ]
