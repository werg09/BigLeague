# Generated by Django 4.2.9 on 2024-05-30 19:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0023_alter_invoice_railcar_alter_invoice_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
                ('quantity', models.IntegerField()),
                ('price_per_unit', models.DecimalField(decimal_places=2, max_digits=5)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.invoice')),
            ],
        ),
    ]