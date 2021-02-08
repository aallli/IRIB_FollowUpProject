# Generated by Django 3.0.8 on 2020-12-20 20:16

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EIRIB_FollowUp', '0026_auto_20201125_1159'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='secretary_query',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Secretary Query'), blank=True, null=True, size=100000),
        ),
        migrations.AddField(
            model_name='user',
            name='secretary_query_name',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Secretary Query Name'),
        ),
    ]