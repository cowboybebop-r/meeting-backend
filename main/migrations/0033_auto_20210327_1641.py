# Generated by Django 3.1.5 on 2021-03-27 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_auto_20210224_1137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='participant_type',
            field=models.CharField(max_length=128, null=True, verbose_name='Ishtirokchilar turi'),
        ),
    ]
