# Generated by Django 3.0.8 on 2020-07-23 11:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('EIRIB_FollowUp', '0003_session'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='enactment',
            name='user',
        ),
    ]
