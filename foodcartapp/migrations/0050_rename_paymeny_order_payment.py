# Generated by Django 3.2.15 on 2022-08-18 06:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0049_order_paymeny'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='paymeny',
            new_name='payment',
        ),
    ]
