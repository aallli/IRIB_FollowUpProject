# Generated by Django 3.0.8 on 2021-07-05 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IRIB_Auth', '0007_user_personnel_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='national_code',
            field=models.CharField(blank=True, max_length=10, verbose_name='National ID'),
        ),
    ]