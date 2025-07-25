# Generated by Django 4.2.17 on 2025-07-20 09:40

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("trials", "0001_initial"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="trial",
            name="trials_status_30b7af_idx",
        ),
        migrations.AlterUniqueTogether(
            name="favoritetrial",
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name="userindustry",
            unique_together=set(),
        ),
        migrations.AlterModelTable(
            name="favoritetrial",
            table=None,
        ),
        migrations.AlterModelTable(
            name="industry",
            table=None,
        ),
        migrations.AlterModelTable(
            name="trial",
            table=None,
        ),
        migrations.AlterModelTable(
            name="userindustry",
            table=None,
        ),
    ]
