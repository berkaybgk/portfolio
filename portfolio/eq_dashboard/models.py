from django.db import models

class EarthquakeDataUSGS(models.Model):
    time = models.DateTimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    depth = models.FloatField()
    mag = models.FloatField()
    place = models.CharField(max_length=255)
    csv_id = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.place}/{self.time}"

