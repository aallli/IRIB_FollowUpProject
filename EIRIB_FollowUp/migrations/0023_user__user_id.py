# Generated by Django 3.0.8 on 2020-09-15 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EIRIB_FollowUp', '0022_auto_20200915_1332'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='_user_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='User ID'),
        ),
    ]
