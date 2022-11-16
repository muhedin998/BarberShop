from django.db import models

KATEGORIJE = [
    ("fejdovi","Fejdovi"),

    ("frizure","Frizure"),

    ("brade","Brade"),

    ("duga_kosa","Duga kosa"),

]

class Slike(models.Model):
    kategorija = models.CharField(max_length=50, choices=KATEGORIJE)
    slika = models.ImageField(null=True, blank=True, upload_to="images/")
