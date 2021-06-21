# Generated by Django 3.0.8 on 2021-06-21 10:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('IRIB_FollowUp', '0023_auto_20201220_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionbase',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.Group', verbose_name='Allowed Group'),
        ),
    ]
