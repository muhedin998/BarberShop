# Generated by Django 4.1.1 on 2022-09-27 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0007_termin_usluga'),
    ]

    operations = [
        migrations.CreateModel(
            name='Frizer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/')),
            ],
        ),
    ]