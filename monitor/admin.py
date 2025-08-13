
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import MonitoringData
from .resources import MonitoringDataResource

@admin.register(MonitoringData)
class MonitoringDataAdmin(ImportExportModelAdmin):
    resource_class = MonitoringDataResource
    list_display = ('timestamp', 'temperature', 'humidity', 'container_code', 'pallet_position', 'product_description')
    list_filter = ('container_code', 'pallet_position', 'timestamp')
    search_fields = ('container_code', 'pallet_position', 'product_description')
    ordering = ('-timestamp',)
