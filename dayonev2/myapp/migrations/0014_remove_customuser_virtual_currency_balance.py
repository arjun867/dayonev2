# Generated by Django 5.0.1 on 2024-02-07 12:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0013_customuser_virtual_currency_balance'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='virtual_currency_balance',
        ),
    ]
