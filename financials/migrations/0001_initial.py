# Generated by Django 4.2.4 on 2023-10-23 19:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('leases', '0003_rental_initial_total_rental_plan_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Warranty_Movement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('income', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('returned', models.DecimalField(decimal_places=2, max_digits=10)),
                ('balance', models.DecimalField(decimal_places=2, max_digits=10)),
                ('detail', models.CharField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('rental', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leases.rental')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voucher_number', models.IntegerField()),
                ('detail', models.CharField(null=True)),
                ('payable_mount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('rental', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leases.rental')),
            ],
        ),
        migrations.CreateModel(
            name='Event_Damage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('selected_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leases.selected_product')),
                ('warranty_movement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='financials.warranty_movement')),
            ],
        ),
    ]
