# Generated by Django 2.2.23 on 2021-05-25 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('income', '0005_auto_20210524_0323'),
    ]

    operations = [
        migrations.AddField(
            model_name='savingcalculation',
            name='amount_to_keep_in_bank',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
