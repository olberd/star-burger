# Generated by Django 3.2.19 on 2023-05-18 07:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_auto_20230518_1035'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productinorder',
            name='price',
        ),
    ]
