# Generated by Django 3.1.5 on 2021-02-16 13:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_auto_20210216_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='region',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.region', verbose_name='Region'),
        ),
    ]
