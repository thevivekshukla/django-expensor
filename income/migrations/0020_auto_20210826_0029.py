# Generated by Django 2.2.24 on 2021-08-25 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('income', '0019_auto_20210822_0153'),
    ]

    operations = [
        migrations.AddField(
            model_name='savingcalculation',
            name='auto_fill_amount_to_keep_in_bank',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='savingcalculation',
            name='auto_fill_savings_min_amount',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]