# Generated by Django 5.1.2 on 2025-01-31 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("facebook", "0003_facebookcomment_is_hidden"),
    ]

    operations = [
        migrations.AddField(
            model_name="facebookpost",
            name="last_fetched_time",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
