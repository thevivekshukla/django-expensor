# Generated by Django 2.2.24 on 2021-08-21 20:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('income', '0018_auto_20210822_0106'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='savingcalculation',
            name='debt_percentage',
        ),
        migrations.RemoveField(
            model_name='savingcalculation',
            name='equity_percentage',
        ),
    ]