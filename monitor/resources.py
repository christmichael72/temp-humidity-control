from import_export import resources
from .models import MonitoringData

class MonitoringDataResource(resources.ModelResource):
    class Meta:
        model = MonitoringData
        fields = ('id', 'timestamp', 'temperature', 'humidity', 'container_code', 'pallet_position', 'product_description')