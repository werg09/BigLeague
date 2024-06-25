# Generated by Django 4.2.9 on 2024-03-19 19:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_releasedrailcar_railcar_is_released'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='demurrage_free_days',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='customer',
            name='demurrage_rate',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.CreateModel(
            name='DemurrageCharge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('free_days', models.PositiveIntegerField(default=0)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.customer')),
                ('railcar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.railcar')),
            ],
        ),
    ]