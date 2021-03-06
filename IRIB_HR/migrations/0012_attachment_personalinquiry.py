# Generated by Django 3.0.8 on 2021-06-26 14:25

import IRIB_HR.models
import IRIB_Shared_Lib.utils
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('IRIB_HR', '0011_auto_20210614_1215'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonalInquiry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(max_length=150, verbose_name='last name')),
                ('father_name', models.CharField(max_length=30, verbose_name='father name')),
                ('id_number', models.CharField(max_length=30, verbose_name='ID number')),
                ('issue_place', models.CharField(max_length=30, verbose_name='issue place')),
                ('_date', models.DateField(default=IRIB_Shared_Lib.utils.set_now, verbose_name='inquiry date')),
                ('_birthdate', models.DateField(verbose_name='birthdate')),
                ('birth_place', models.CharField(max_length=30, verbose_name='birth place')),
                ('religion', models.CharField(max_length=30, verbose_name='religion')),
                ('personal_no', models.CharField(blank=True, max_length=10, verbose_name='personal number')),
                ('national_code', models.CharField(max_length=10, verbose_name='National ID')),
                ('alias', models.CharField(blank=True, max_length=30, verbose_name='alias')),
                ('marital_status', models.CharField(choices=[('married', 'Married'), ('single', 'Single'), ('divorced', 'Divorced'), ('widowed', 'Widowed')], default='single', max_length=30, verbose_name='marital status')),
                ('cooperation_reason', models.CharField(blank=True, max_length=255, null=True, verbose_name='cooperation reason')),
                ('educational_stage', models.CharField(choices=[('preschool', 'Preschool'), ('primary', 'Primary'), ('lower', 'Lower secondary'), ('upper', 'Upper secondary'), ('bachelor', 'Bachelors or equivalent'), ('master', 'Masters or equivalent'), ('doctoral', 'Doctoral or equivalent')], default='upper', max_length=50, verbose_name='educational stage')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Email address')),
                ('mobile', models.CharField(blank=True, help_text='Valid mobile format is either +989xxxxxxxxx or 09xxxxxxxxx', max_length=13, null=True, validators=[django.core.validators.RegexValidator(message='Valid mobile format is either +989xxxxxxxxx or 09xxxxxxxxx', regex='^(\\+989\\d{9})|^(09\\d{9})$')], verbose_name='Mobile no.')),
                ('tel', models.CharField(blank=True, max_length=13, null=True, verbose_name='Tel')),
                ('sex', models.CharField(choices=[('male', 'Male'), ('female', 'Female')], default='male', max_length=10, verbose_name='Sex')),
                ('postal_code', models.CharField(blank=True, max_length=10, null=True, verbose_name='postal code')),
                ('address', models.TextField(max_length=4000, verbose_name='Address')),
                ('operator_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='operator name')),
                ('description', models.TextField(blank=True, max_length=4000, verbose_name='Description')),
                ('background', models.TextField(blank=True, max_length=4000, verbose_name='job background')),
                ('image', django_resized.forms.ResizedImageField(blank=True, crop=None, force_format='JPEG', keep_meta=True, null=True, quality=75, size=[150, 150], upload_to='uploads/user-images/', verbose_name='Image')),
            ],
            options={
                'verbose_name': 'Personal Inquiry',
                'verbose_name_plural': 'Personal Inquiries',
                'ordering': ['_date', 'last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=2000, null=True, verbose_name='Description')),
                ('file', models.FileField(upload_to=IRIB_HR.models.Attachment.directory_path, verbose_name='File')),
                ('personal_inquiry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='IRIB_HR.PersonalInquiry', verbose_name='Personal Inquiry')),
            ],
            options={
                'verbose_name': 'Attachment',
                'verbose_name_plural': 'Attachments',
                'ordering': ['description'],
            },
        ),
    ]
