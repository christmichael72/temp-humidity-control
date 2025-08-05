
from django import forms
from .models import MonitoringData

class MonitoringDataForm(forms.ModelForm):
    class Meta:
        model = MonitoringData
        fields = '__all__'

    def clean_temperature(self):
        temp = self.cleaned_data.get('temperature')
        if temp > -15 or temp < -20:
            raise forms.ValidationError("Temperature must be between -20°C and -15°C.")
        return temp

    def clean_humidity(self):
        hum = self.cleaned_data.get('humidity')
        if hum > 90 or hum < 75:
            raise forms.ValidationError("Humidity must be between 75% and 90%.")
        return hum
