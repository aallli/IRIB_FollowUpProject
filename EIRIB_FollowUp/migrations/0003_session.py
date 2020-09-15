# Generated by Django 3.0.8 on 2020-07-23 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EIRIB_FollowUp', '0002_enactment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=2000, null=True, unique=True, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Session',
                'verbose_name_plural': 'Sessions',
                'ordering': ['name'],
            },
        ),
    ]