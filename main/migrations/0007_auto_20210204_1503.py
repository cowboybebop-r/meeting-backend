# Generated by Django 3.1.1 on 2021-02-04 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20210204_1500'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='baseuser',
            name='full_name',
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=128, verbose_name='Ism'),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=128, verbose_name='Ism'),
        ),
    ]
