# Generated by Django 3.1.1 on 2021-02-05 14:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20210204_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=128, verbose_name='Familiyasi'),
        ),
        migrations.AlterField(
            model_name='compliance',
            name='meeting',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.meeting'),
        ),
        migrations.AlterField(
            model_name='compliance',
            name='option',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.complianceoption'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.organization', verbose_name='Tashkilot'),
        ),
        migrations.AlterField(
            model_name='meetingtopic',
            name='meeting',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.meeting', verbose_name='Majlis'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='region',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.region', verbose_name='Region'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Masul'),
        ),
    ]
