# Generated by Django 3.0.8 on 2021-04-13 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EIRIB_FollowUp', '0027_auto_20201220_2016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enactment',
            name='result',
            field=models.TextField(blank=True, help_text='Please insert your name and entry date before your result.', max_length=4000, null=True, verbose_name='Result'),
        ),
    ]