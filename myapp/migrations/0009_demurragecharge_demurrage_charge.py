# Generated by Django 4.2.9 on 2024-03-19 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_customer_contact_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='demurragecharge',
            name='demurrage_charge',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
