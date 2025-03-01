# Generated by Django 3.2.15 on 2022-08-16 08:57

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0037_auto_20210125_1833'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(blank=True, db_index=True, max_length=50, verbose_name='фамилия')),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(db_index=True, max_length=128, region=None, verbose_name='телефон')),
                ('address', models.TextField(blank=True, db_index=True, max_length=200, verbose_name='адрес')),
            ],
            options={
                'verbose_name': 'заказ',
                'verbose_name_plural': 'заказы',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1, verbose_name='количество')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='foodcartapp.order', verbose_name='клиент')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='foodcartapp.product', verbose_name='продукт')),
            ],
            options={
                'verbose_name': 'пункт заказа',
                'verbose_name_plural': 'пункты заказа',
                'unique_together': {('order', 'product')},
            },
        ),
    ]
