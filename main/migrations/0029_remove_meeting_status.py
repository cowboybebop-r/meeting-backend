# Generated by Django 3.1.5 on 2021-02-23 09:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_meeting_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meeting',
            name='status',
        ),
    ]
