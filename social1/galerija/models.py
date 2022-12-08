from django.db import models

KATEGORIJE = [
    ("krace-moderne","Kraće moderne"),

    ("duze-moderne","Duže moderne"),

    ("decije-frizure","Dečije frizure"),

    ("tribali","Tribali"),

    ("internet-frizure", "Internet frizure"),

    ("ostale-usluge", "Ostale usluge")

]

class Slike(models.Model):
    kategorija = models.CharField(max_length=50, choices=KATEGORIJE)
    slika = models.ImageField(upload_to="images/")

    def __str__(self):
        return f"{self.kategorija} - {self.slika}"
