# Generated by Django 3.0.8 on 2020-10-03 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IRIB_HR', '0005_auto_20200928_1425'),
    ]

    operations = [
        migrations.AddField(
            model_name='payslip',
            name='contract_type',
            field=models.CharField(blank=True, max_length=200, verbose_name='Contract Type'),
        ),
        migrations.AddField(
            model_name='payslip',
            name='etc',
            field=models.IntegerField(default=0, verbose_name='etc'),
        ),
    ]
