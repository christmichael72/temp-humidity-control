
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator
from io import BytesIO
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import MonitoringData
from .forms import MonitoringDataForm
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Avg, Max
from xhtml2pdf import pisa
from datetime import datetime, timedelta
import base64

def dashboard(request):
    data = MonitoringData.objects.all().order_by('timestamp')

    # Filters
    date = request.GET.get('date')
    start_hour = request.GET.get('start_hour')
    end_hour = request.GET.get('end_hour')

    # ✅ If no date filter is given, default to most recent day
    if not date:
        latest_entry = MonitoringData.objects.aggregate(Max('timestamp'))['timestamp__max']
        if latest_entry:
            date = latest_entry.date().strftime('%Y-%m-%d')

    # Apply date filter
    if date:
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            data = data.filter(timestamp__date=date_obj)

            # ✅ Apply hour filter if provided
            if start_hour and end_hour:
                try:
                    start_h = int(start_hour)
                    end_h = int(end_hour)
                    data = data.filter(timestamp__hour__gte=start_h, timestamp__hour__lte=end_h)
                except ValueError:
                    pass

        except ValueError:
            pass

    temp_alerts = data.filter(temperature__gt=-18).order_by('-timestamp')
    humidity_alerts = data.filter(humidity__gt=85).order_by('-timestamp')

    labels = [d.timestamp.strftime('%H:%M') for d in data]
    temps = [d.temperature for d in data]
    hums = [d.humidity for d in data]

    ewma_temps, ewma_hums = [], []
    temp_forecast, hum_forecast = [], []

    # Calculate EWMA for temps
    if len(temps) > 0:
        df_temp = pd.Series(temps)
        ewma_temps = df_temp.ewm(alpha=0.3).mean().round(2).tolist()

        if len(ewma_temps) > 1:
            slope = ewma_temps[-1] - ewma_temps[-2]
        else:
            slope = 0
        last_val = ewma_temps[-1]

        # Predict next 6 intervals
        horizon = 6
        temp_forecast = [round(last_val + (i + 1) * slope, 2) for i in range(horizon)]

        last_time = data.last().timestamp
        forecast_labels = [(last_time + timedelta(minutes=60 * (i + 1))).strftime('%H:%M') for i in range(horizon)]

        # Control Limits
        mean_temp = df_temp.mean()
        std_temp = df_temp.std()
        cl_temp = round(mean_temp, 2)
        ucl_temp = round(mean_temp + 3 * std_temp, 2)
        lcl_temp = round(mean_temp - 3 * std_temp, 2)
    else:
        ewma_temps = []
        temp_forecast = []
        forecast_labels = []
        cl_temp = ucl_temp = lcl_temp = None

    # Calculate EWMA for hums
    if len(hums) > 0:
        df_hum = pd.Series(hums)
        ewma_hums = df_hum.ewm(alpha=0.3).mean().round(2).tolist()

        if len(ewma_hums) > 1:
            slope = ewma_hums[-1] - ewma_hums[-2]
        else:
            slope = 0
        last_val = ewma_hums[-1]

        # Predict next 6 intervals
        horizon = 6
        hum_forecast = [round(last_val + (i + 1) * slope, 2) for i in range(horizon)]

        last_time = data.last().timestamp
        forecast_labels = [(last_time + timedelta(minutes=60 * (i + 1))).strftime('%H:%M') for i in range(horizon)]

        # Control Limits
        mean_hum = df_hum.mean()
        std_hum = df_hum.std()
        cl_hum = round(mean_hum, 2)
        ucl_hum = round(mean_hum + 3 * std_hum, 2)
        lcl_hum = round(mean_hum - 3 * std_hum, 2)
    else:
        ewma_hums = []
        hum_forecast = []
        forecast_labels = []
        cl_hum = ucl_hum = lcl_hum = None

    forecast_temp_alerts, forecast_hum_alerts = [], []

    # Forecast temperature alerts
    if temp_forecast and ucl_temp is not None and lcl_temp is not None:
        for i, val in enumerate(temp_forecast):
            if val >= ucl_temp or val <= lcl_temp:
                forecast_temp_alerts.append({
                    "time": forecast_labels[i],
                    "value": val,
                    "type": "upper" if val >= ucl_temp else "lower"
                })

    # Forecast humidity alerts
    if hum_forecast and ucl_hum is not None and lcl_hum is not None:
        for i, val in enumerate(hum_forecast):
            if val >= ucl_hum or val <= lcl_hum:
                forecast_hum_alerts.append({
                    "time": forecast_labels[i],
                    "value": val,
                    "type": "upper" if val >= ucl_hum else "lower"
                })

    # Extract metadata from first matching entry (if exists)
    metadata = data.first()

    context = {
        'data': data,
        'labels': labels,
        'temps': temps,
        'ewma_temps': ewma_temps,
        'cl_temp': cl_temp,
        'ucl_temp': ucl_temp,
        'lcl_temp': lcl_temp,
        'hums': hums,
        'ewma_hums': ewma_hums,
        'cl_hum': cl_hum,
        'ucl_hum': ucl_hum,
        'lcl_hum': lcl_hum,
        'metadata': metadata,
        'date' : date,
        'temp_alerts': temp_alerts,
        'humidity_alerts': humidity_alerts,
        'forecast_labels': forecast_labels,
        'temp_forecast': temp_forecast,
        'hum_forecast': hum_forecast,
        "forecast_temp_alerts": forecast_temp_alerts,
        "forecast_hum_alerts": forecast_hum_alerts,
        'request': request
    }
    return render(request, 'monitor/dashboard.html', context)

def range_chart(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    start_hour = request.GET.get('start_hour')
    end_hour = request.GET.get('end_hour')

    data = MonitoringData.objects.all()

    # Apply date range
    if start_date and end_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            data = data.filter(timestamp__date__gte=start_dt, timestamp__date__lte=end_dt)
        except ValueError:
            pass


    # ✅ Apply hour filter
    if start_hour and end_hour:
        try:
            start_h = int(start_hour)
            end_h = int(end_hour)
            data = data.filter(timestamp__hour__gte=start_h, timestamp__hour__lte=end_h)
        except ValueError:
            pass

    daily_data = (
        data
        .values('timestamp__date')
        .annotate(avg_temp=Avg('temperature'), avg_hum=Avg('humidity'))
        .order_by('timestamp__date')
    )

    labels = [d['timestamp__date'].strftime('%Y-%m-%d') for d in daily_data]
    avg_temps = [round(d['avg_temp'], 2) for d in daily_data]
    avg_hums = [round(d['avg_hum'], 2) for d in daily_data]

    # ✅ EWMA
    ewma_temps = pd.Series(avg_temps).ewm(alpha=0.3).mean().round(2).tolist() if avg_temps else []
    ewma_hums = pd.Series(avg_hums).ewm(alpha=0.3).mean().round(2).tolist() if avg_hums else []

    # ✅ Control Limits
    def get_cl_limits(values):
        if not values:
            return None, None, None
        s = pd.Series(values)
        cl = round(s.mean(), 2)
        ucl = round(cl + 3 * s.std(), 2)
        lcl = round(cl - 3 * s.std(), 2)
        return cl, ucl, lcl

    cl_temp, ucl_temp, lcl_temp = get_cl_limits(avg_temps)
    cl_hum, ucl_hum, lcl_hum = get_cl_limits(avg_hums)

    return render(request, 'monitor/range_chart.html', {
        'labels': labels,
        'avg_temps': avg_temps,
        'avg_hums': avg_hums,
        'ewma_temps': ewma_temps,
        'ewma_hums': ewma_hums,
        'cl_temp': cl_temp,
        'ucl_temp': ucl_temp,
        'lcl_temp': lcl_temp,
        'cl_hum': cl_hum,
        'ucl_hum': ucl_hum,
        'lcl_hum': lcl_hum,
        'start_date': start_date or '',
        'end_date': end_date or ''
    })

def manual_input(request):
    form = MonitoringDataForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request, 'monitor/manual_input.html', {'form': form})

def generate_chart_pdf(request):
    date = request.GET.get("date")
    container = request.GET.get("container")
    pallet = request.GET.get("pallet")
    product = request.GET.get("product")

    data = MonitoringData.objects.all()

    if date:
        data = data.filter(timestamp__date=date)
    if container:
        data = data.filter(container_code__icontains=container)
    if pallet:
        data = data.filter(pallet_position__icontains=pallet)
    if product:
        data = data.filter(product_description__icontains=product)

    data = data.order_by("timestamp")

    # Generate labels and chart data
    labels = [d.timestamp.strftime('%I:%M %p') for d in data]
    temps = [d.temperature for d in data]
    hums = [d.humidity for d in data]

    # Thresholds
    temp_threshold = -18
    humidity_threshold = 85

    # Color logic
    temp_colors = ['red' if t > temp_threshold else '#FFA500' for t in temps]
    humidity_colors = ['red' if h > humidity_threshold else '#007BFF' for h in hums]

    # Chart generation
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(labels, temps, color='#FFA500', linewidth=2, label='Temperature (°C)')
    ax1.scatter(labels, temps, color=temp_colors, s=50, zorder=5)
    ax1.set_ylabel('Temperature (°C)', color='#FFA500')
    ax1.tick_params(axis='y', labelcolor='#FFA500')
    ax1.set_ylim(-22, -12)
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax1.axhline(temp_threshold, color='red', linestyle='--', linewidth=1, alpha=0.5)

    ax2 = ax1.twinx()
    ax2.bar(labels, hums, color=humidity_colors, alpha=0.7)
    ax2.set_ylabel('Humidity (%)', color='#007BFF')
    ax2.tick_params(axis='y', labelcolor='#007BFF')
    ax2.set_ylim(55, 90)
    ax2.axhline(humidity_threshold, color='red', linestyle='--', linewidth=1, alpha=0.5)

    ax1.set_xticks(range(len(labels)))
    ax1.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    plt.title(f"Temperature & Humidity Monitoring - {date}", fontsize=12, weight='bold')
    fig.tight_layout()

    # Save chart to image buffer
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()

    # Use first entry for metadata
    metadata = data.first()

    # Render PDF content
    html = render_to_string("monitor/chart_pdf_embed.html", {
        "chart": image_base64,
        "date": date,
        "container_code": metadata.container_code,
        "pallet_position": metadata.pallet_position,
        "product_description": metadata.product_description,
    })

    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="chart_report_{date}.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response
