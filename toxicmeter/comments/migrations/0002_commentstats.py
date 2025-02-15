# Generated by Django 5.1.2 on 2025-01-15 12:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("comments", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CommentStats",
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
                ("comments_analyzed", models.PositiveIntegerField(default=0)),
                ("comments_fetched", models.PositiveIntegerField(default=0)),
                ("comments_deleted", models.PositiveIntegerField(default=0)),
                ("comments_hidden", models.PositiveIntegerField(default=0)),
                ("comments_unhidden", models.PositiveIntegerField(default=0)),
                ("comments_manually_tagged", models.PositiveIntegerField(default=0)),
                ("posts_fetched", models.PositiveIntegerField(default=0)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "moderator",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="moderator_stats",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
