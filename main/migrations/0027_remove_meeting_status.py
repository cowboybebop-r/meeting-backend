# Generated by Django 3.1.5 on 2021-02-23 09:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_auto_20210216_1848'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meeting',
            name='status',
        ),
    ]
