# Generated by Django 2.1.5 on 2019-02-17 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backup', '0002_backup_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backup',
            name='timestamp',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
