# Generated by Django 3.2.19 on 2023-05-31 19:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_auto_20230531_1844'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='contact_phone',
            new_name='phonenumber',
        ),
    ]
