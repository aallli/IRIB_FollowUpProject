# Generated by Django 3.0.8 on 2021-04-13 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IRIB_HR', '0006_auto_20201003_1058'),
    ]

    operations = [
        migrations.AddField(
            model_name='payslip',
            name='difference',
            field=models.IntegerField(default=0, verbose_name='difference'),
        ),
    ]