from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('leases', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Warranty_Movement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voucher_number', models.CharField(max_length=255)),
                ('income', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('returned', models.DecimalField(decimal_places=2, max_digits=10)),
                ('balance', models.DecimalField(decimal_places=2, max_digits=10)),
                ('detail', models.CharField(max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('rental', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leases.rental')),
            ],
            options={
                'indexes': [
                    models.Index(fields=['rental'], name='financials__rental__64ad0b_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voucher_number', models.CharField(max_length=255)),
                ('business_name', models.CharField(max_length=255)),
                ('nit', models.CharField(max_length=255)),
                ('detail', models.CharField(max_length=255, null=True)),
                ('payable_mount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('rental', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leases.rental')),
            ],
            options={
                'indexes': [
                    models.Index(fields=['rental'], name='financials__rental__671c00_idx'),
                ],
            },
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
