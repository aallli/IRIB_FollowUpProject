# Generated by Django 3.0.8 on 2020-08-31 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IRIB_FollowUp', '0008_groupfollowup'),
    ]

    operations = [
        migrations.AddField(
            model_name='enactment',
            name='_type',
            field=models.CharField(choices=[('AGENDA', 'Agenda'), ('ENACTMENT', 'Enactment')], default='ENACTMENT', max_length=30, verbose_name='Type'),
        ),
    ]
