# Generated by Django 4.2.9 on 2024-04-10 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0013_invoice_invoice_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='email_sent',
            field=models.BooleanField(default=False),
        ),
    ]