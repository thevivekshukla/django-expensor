# Generated by Django 4.2 on 2023-04-15 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('income', '0029_change_ids_to_big_autofield_dj42'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='source',
            index=models.Index(fields=['user', 'name'], name='income_sour_user_id_9ff498_idx'),
        ),
    ]