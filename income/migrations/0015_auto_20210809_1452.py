# Generated by Django 2.2.24 on 2021-08-09 09:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('income', '0014_remove_savingcalculation_savings_max_amount'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='income',
            options={'ordering': ('-timestamp', '-created_at')},
        ),
    ]
