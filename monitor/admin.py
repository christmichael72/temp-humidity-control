
from django.contrib import admin
from .models import MonitoringData

@admin.register(MonitoringData)
class MonitoringDataAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'temperature', 'humidity', 'container_code', 'pallet_position')
    list_filter = ('container_code', 'pallet_position', 'timestamp')
    search_fields = ('container_code', 'pallet_position', 'product_description')
    ordering = ('-timestamp',)
