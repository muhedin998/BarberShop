# Generated by Django 4.1.1 on 2022-11-16 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('galerija', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slike',
            name='kategorija',
            field=models.CharField(choices=[('krace-moderne', 'Kraće moderne'), ('duze-moderne', 'Duže moderne'), ('decije-frizure', 'Dečije frizure'), ('tribali', 'Tribali')], max_length=50),
        ),
    ]
