
from django.db import models
from django.utils import timezone

class MonitoringData(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    temperature = models.FloatField()
    humidity = models.FloatField()
    container_code = models.CharField(max_length=50)
    pallet_position = models.CharField(max_length=20)
    product_description = models.TextField()

    def is_temp_alert(self):
        return self.temperature > -18

    def is_humidity_alert(self):
        return self.humidity > 85
