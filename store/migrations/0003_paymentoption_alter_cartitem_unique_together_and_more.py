# Generated by Django 4.2.6 on 2023-12-29 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_remove_address_phone_number_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='cartitem',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='cart',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='product',
        ),
        migrations.DeleteModel(
            name='Cart',
        ),
        migrations.DeleteModel(
            name='CartItem',
        ),
    ]
