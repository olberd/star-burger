# Generated by Django 3.2.19 on 2023-06-05 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0048_alter_productinorder_fixed_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_status',
            field=models.PositiveSmallIntegerField(choices=[('1', 'Необработанный'), ('2', 'Собирается'), ('3', 'Доставка'), ('4', 'Обработан')], default=1),
            preserve_default=False,
        ),
    ]
