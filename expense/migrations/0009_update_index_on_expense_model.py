# Generated by Django 4.2 on 2023-04-15 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expense', '0008_add_index_on_expense_table'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='expense',
            name='expense_exp_user_id_9b9c10_idx',
        ),
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['user', '-timestamp', '-created_at'], name='expense_exp_user_id_25c175_idx'),
        ),
    ]
