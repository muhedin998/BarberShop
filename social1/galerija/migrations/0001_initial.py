# Generated by Django 4.1.1 on 2022-11-14 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Slike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kategorija', models.CharField(choices=[('fejdovi', 'fejdovi'), ('frizure', 'fejdovi'), ('brade', 'fejdovi'), ('duga_kosa', 'duga kosa')], max_length=50)),
                ('slika', models.ImageField(blank=True, null=True, upload_to='images/')),
            ],
        ),
    ]