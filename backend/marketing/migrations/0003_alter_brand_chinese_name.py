# Generated by Django 3.2.25 on 2024-05-24 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0002_auto_20240522_1352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='chinese_name',
            field=models.CharField(max_length=255),
        ),
    ]
