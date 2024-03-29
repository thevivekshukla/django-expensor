# Generated by Django 2.2.23 on 2021-05-23 19:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('income', '0003_auto_20210523_1432'),
    ]

    operations = [
        migrations.CreateModel(
            name='SavingCalculation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('savings_percentage', models.PositiveIntegerField(help_text='in percentage')),
                ('savings_min_amount', models.PositiveIntegerField(help_text='min amount that must be saved. 0 to ignore')),
                ('savings_max_amount', models.PositiveIntegerField(help_text='max amount that can be saved. 0 to ignore')),
                ('gold_percentage', models.PositiveIntegerField(help_text='in percentage')),
                ('debt_percentage', models.PositiveIntegerField(help_text='in percentage')),
                ('equity_percentage', models.PositiveIntegerField(help_text='in percentage')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='savings_calculation', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
