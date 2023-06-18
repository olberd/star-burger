# Generated by Django 3.2.19 on 2023-06-09 06:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0058_auto_20230607_2323'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cooking_restaurant',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='foodcartapp.restaurant', verbose_name='Ресторан для приготовления заказа'),
        ),
    ]
