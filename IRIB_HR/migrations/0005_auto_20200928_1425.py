# Generated by Django 3.0.8 on 2020-09-28 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IRIB_HR', '0004_auto_20200928_1126'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payslip',
            options={'ordering': ['year', 'month'], 'verbose_name': 'Pay Slip', 'verbose_name_plural': 'Pay Slips'},
        ),
        migrations.AddField(
            model_name='payslip',
            name='overtime',
            field=models.IntegerField(default=0, verbose_name='Overtime'),
        ),
    ]
