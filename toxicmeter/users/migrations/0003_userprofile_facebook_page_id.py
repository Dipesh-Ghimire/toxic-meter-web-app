# Generated by Django 5.1.2 on 2024-12-23 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_userprofile_assigned_by_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="facebook_page_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
