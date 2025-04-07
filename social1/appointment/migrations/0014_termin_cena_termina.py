from django.db import migrations, models

def populate_cena_termina(apps, schema_editor):
    Termin = apps.get_model('appointment', 'Termin')
    for termin in Termin.objects.filter(cena_termina__isnull=True, usluga__isnull=False):
        termin.cena_termina = termin.usluga.cena
        termin.save()

class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0013_termin_poruka'),
    ]

    operations = [
        migrations.AddField(
            model_name='termin',
            name='cena_termina',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.RunPython(populate_cena_termina),
    ]
