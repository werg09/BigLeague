# Generated by Django 4.2.9 on 2024-03-28 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_customer_customer_address_customer_customer_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='railcar',
            name='released_timestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]