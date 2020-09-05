# Generated by Django 3.0.8 on 2020-09-04 17:22

import IRIB_FollowUpProject.utils
import Knowledge_Management.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Knowledge_Management', '0006_activityindicator_indicator'),
    ]

    operations = [
        migrations.CreateModel(
            name='CardtableBase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=IRIB_FollowUpProject.utils.set_now, verbose_name='Creation Date')),
                ('description', models.TextField(blank=True, max_length=4000, null=True, verbose_name='Description')),
                ('_status', models.CharField(choices=[('NEW', 'New'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected'), ('CONDITIONAL', 'Conditional'), ('APPROVED', 'Approved')], default='NEW', max_length=30, verbose_name='Status')),
                ('activity', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Knowledge_Management.Activity', verbose_name='Activity')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Knowledge User')),
            ],
            options={
                'verbose_name': 'Cardtable Base',
                'verbose_name_plural': 'Cardtable Bases',
                'ordering': ['activity'],
            },
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=2000, null=True, verbose_name='Description')),
                ('file', models.FileField(upload_to=Knowledge_Management.models.Attachment.directory_path, verbose_name='File')),
                ('cardtable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Knowledge_Management.CardtableBase', verbose_name='Personal Cardtable')),
            ],
            options={
                'verbose_name': 'Attachment',
                'verbose_name_plural': 'Attachments',
                'ordering': ['description'],
            },
        ),
        migrations.CreateModel(
            name='ActivityAssessment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, null=True, verbose_name='Assessment Date')),
                ('score', models.IntegerField(blank=True, null=True, verbose_name='Score')),
                ('description', models.TextField(blank=True, max_length=2000, null=True, verbose_name='Description')),
                ('cardtable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Knowledge_Management.CardtableBase', verbose_name='Personal Cardtable')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Knowledge_Management.CommitteeMember', verbose_name='Committee Member')),
            ],
            options={
                'verbose_name': 'Activity Assessment',
                'verbose_name_plural': 'Activity Assessments',
                'ordering': ['cardtable', 'member'],
                'unique_together': {('cardtable', 'member')},
            },
        ),
    ]
