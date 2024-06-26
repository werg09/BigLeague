# Generated by Django 4.2.9 on 2024-01-16 03:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('entrance_fee', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Railcar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('railcar_number', models.CharField(max_length=11)),
                ('received_date', models.DateField()),
                ('released_date', models.DateField(blank=True, null=True)),
                ('left_yard_date', models.DateField(blank=True, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('days_in_yard', models.PositiveIntegerField()),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('railcar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.railcar')),
            ],
        ),
    ]
