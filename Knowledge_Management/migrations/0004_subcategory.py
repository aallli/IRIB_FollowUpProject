# Generated by Django 3.0.8 on 2020-09-01 14:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Knowledge_Management', '0003_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=2000, verbose_name='Name')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Knowledge_Management.Category', verbose_name='Category')),
            ],
            options={
                'verbose_name': 'Knowledge Sub-Category',
                'verbose_name_plural': 'Knowledge Sub-Categories',
                'ordering': ['category', 'name'],
                'unique_together': {('name', 'category')},
            },
        ),
    ]