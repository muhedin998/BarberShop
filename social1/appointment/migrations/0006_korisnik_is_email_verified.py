# Generated by Django 4.1.1 on 2022-12-05 23:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0005_termin_broj_telefona'),
    ]

    operations = [
        migrations.AddField(
            model_name='korisnik',
            name='is_email_verified',
            field=models.BooleanField(default=False),
        ),
    ]
