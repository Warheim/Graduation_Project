# Generated by Django 4.2.2 on 2023-07-03 11:10

import backend.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', backend.models.UserManager()),
            ],
        ),
    ]
