# Generated by Django 5.0 on 2024-04-18 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keycloak_username', models.CharField(max_length=50, unique=True)),
                ('wallet_address', models.CharField(max_length=50)),
            ],
        ),
    ]
