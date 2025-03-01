# Generated by Django 3.2.15 on 2022-08-18 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0053_auto_20220818_1326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment',
            field=models.CharField(choices=[(0, 'Наличностью'), (1, 'Электронно')], db_index=False, default=0, max_length=1, verbose_name='способ оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[(0, 'Необработанный'), (1, 'Готовится'), (2, 'В доставке'), (3, 'Завершён')], db_index=False, default=0, max_length=1, verbose_name='статус'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment',
            field=models.IntegerField(choices=[(0, 'Наличностью'), (1, 'Электронно')], db_index=True, default=0, verbose_name='способ оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(0, 'Необработанный'), (1, 'Готовится'), (2, 'В доставке'), (3, 'Завершён')], db_index=True, default=0, verbose_name='статус'),
        ),
    ]
