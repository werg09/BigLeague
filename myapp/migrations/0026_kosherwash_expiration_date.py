# Generated by Django 4.2.9 on 2024-06-24 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0025_tank_kosherwash'),
    ]

    operations = [
        migrations.AddField(
            model_name='kosherwash',
            name='expiration_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
