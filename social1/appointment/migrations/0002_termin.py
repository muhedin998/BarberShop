# Generated by Django 3.0.14 on 2022-09-19 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Termin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datum', models.DateField(blank=True)),
                ('vreme', models.TimeField(blank=True)),
            ],
        ),
    ]
