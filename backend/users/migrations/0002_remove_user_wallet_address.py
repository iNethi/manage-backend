# Generated by Django 5.0 on 2024-06-21 13:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='wallet_address',
        ),
    ]