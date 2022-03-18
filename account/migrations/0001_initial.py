# Generated by Django 2.2.27 on 2022-03-18 10:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=128)),
                ('type', models.IntegerField(choices=[(0, 'Liability'), (1, 'Asset')])),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='account_names', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('name', 'created_at'),
                'unique_together': {('user', 'name', 'type')},
            },
        ),
        migrations.CreateModel(
            name='NetWorth',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('amount', models.IntegerField()),
                ('date', models.DateField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='net_worth', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-date', '-created_at'),
                'unique_together': {('user', 'date')},
            },
        ),
        migrations.CreateModel(
            name='AccountNameAmount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('amount', models.PositiveIntegerField()),
                ('date', models.DateField()),
                ('account_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='amounts', to='account.AccountName')),
            ],
            options={
                'ordering': ('-date', '-created_at'),
                'unique_together': {('account_name', 'date')},
            },
        ),
    ]
