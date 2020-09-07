# Generated by Django 3.0.8 on 2020-09-07 12:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Knowledge_Management', '0014_auto_20200907_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardtablebase',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Knowledge User'),
        ),
    ]
