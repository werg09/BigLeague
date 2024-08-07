# Generated by Django 4.2.9 on 2024-06-20 19:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0024_invoiceitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tank_number', models.CharField(max_length=255)),
                ('capacity', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='KosherWash',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wash_date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('driver_name', models.CharField(max_length=255)),
                ('wash_type', models.CharField(max_length=255)),
                ('wash_duration', models.DurationField()),
                ('tank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.tank')),
            ],
        ),
    ]
