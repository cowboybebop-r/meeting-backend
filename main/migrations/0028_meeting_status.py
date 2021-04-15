# Generated by Django 3.1.5 on 2021-02-23 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_remove_meeting_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Reja qilingan'), (2, 'Jarayonda'), (3, 'Yakunlangan'), (4, 'Bekor qilingan')], default=1, verbose_name='Holati'),
        ),
    ]
