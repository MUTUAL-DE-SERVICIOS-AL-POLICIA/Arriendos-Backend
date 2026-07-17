import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('plans', '0001_initial'),
        ('customers', '0001_initial'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('next_state', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=None)),
            ],
        ),
        migrations.CreateModel(
            name='Event_Type',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Rental',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('initial_total', models.FloatField(null=True)),
                ('contract_number', models.CharField(max_length=10, null=True)),
                ('warranty_return_request', models.DateTimeField(null=True)),
                ('warranty_returned', models.DateTimeField(null=True)),
                ('cancel_reason', models.CharField(max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.customer')),
                ('plan', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='plans.plan')),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leases.state')),
            ],
            options={
                'indexes': [
                    models.Index(fields=['state', 'customer'], name='leases_rent_state_i_acd8ff_idx'),
                    models.Index(fields=['customer', 'state'], name='leases_rent_custome_2c9a42_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='Selected_Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(null=True)),
                ('end_time', models.DateTimeField(null=True)),
                ('detail', models.CharField(max_length=255, null=True)),
                ('product_price', models.FloatField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('event_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leases.event_type')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
                ('rental', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leases.rental')),
            ],
            options={
                'indexes': [
                    models.Index(fields=['rental', 'product'], name='leases_sele_rental__741378_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='Additional_Hour_Applied',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('voucher_number', models.CharField(max_length=255)),
                ('business_name', models.CharField(max_length=255)),
                ('nit', models.CharField(max_length=255)),
                ('total', models.FloatField()),
                ('description', models.CharField(max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('selected_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leases.selected_product')),
            ],
            options={
                'indexes': [
                    models.Index(fields=['selected_product'], name='leases_addi_selecte_4ecb31_idx'),
                ],
            },
        ),
    ]
