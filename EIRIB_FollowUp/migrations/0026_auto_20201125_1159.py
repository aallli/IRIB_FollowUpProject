# Generated by Django 3.0.8 on 2020-11-25 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EIRIB_FollowUp', '0025_auto_20201122_1313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enactment',
            name='result',
            field=models.TextField(blank=True, max_length=4000, null=True, verbose_name='Result'),
        ),
    ]
