# Generated by Django 3.1.5 on 2021-02-16 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_baseuser_region'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='baseuser',
            name='regionadmin',
        ),
        migrations.AddField(
            model_name='baseuser',
            name='region_admin',
            field=models.BooleanField(default=False, verbose_name='Viloyat admin'),
        ),
    ]
