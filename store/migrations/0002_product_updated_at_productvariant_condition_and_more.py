# Generated by Django 4.2.6 on 2023-11-14 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='productvariant',
            name='condition',
            field=models.CharField(choices=[('New', 'New'), ('Used', 'Used')], default='New', max_length=4),
        ),
        migrations.AddField(
            model_name='productvariant',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]