# Generated by Django 2.2.23 on 2021-05-23 09:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('expense', '0002_auto_20190805_0309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='remark',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expenses', to='expense.Remark'),
        ),
        migrations.AlterField(
            model_name='expense',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='remark',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='remarks', to=settings.AUTH_USER_MODEL),
        ),
    ]