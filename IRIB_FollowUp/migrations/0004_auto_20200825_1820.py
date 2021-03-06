# Generated by Django 3.0.8 on 2020-08-25 18:20

import IRIB_FollowUp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IRIB_FollowUp', '0003_auto_20200825_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enactment',
            name='date',
            field=models.DateTimeField(default=IRIB_FollowUp.models.set_now, verbose_name='Assignment Date'),
        ),
        migrations.AlterField(
            model_name='enactment',
            name='review_date',
            field=models.DateTimeField(default=IRIB_FollowUp.models.set_now, verbose_name='Review Date'),
        ),
    ]
