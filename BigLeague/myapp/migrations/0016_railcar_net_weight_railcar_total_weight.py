# Generated by Django 4.2.9 on 2024-04-19 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0015_customer_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='railcar',
            name='net_weight',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='railcar',
            name='total_weight',
            field=models.FloatField(blank=True, null=True),
        ),
    ]