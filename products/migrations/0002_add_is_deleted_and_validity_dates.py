from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='price',
            name='valid_from',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='price',
            name='valid_to',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['rate', 'room', 'is_deleted'], name='products_pr_rate_id_0b420e_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['room', 'is_deleted'], name='products_pr_room_id_d92277_idx'),
        ),
    ]
