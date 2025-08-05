
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from io import BytesIO
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import MonitoringData
from .forms import MonitoringDataForm
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
from datetime import datetime
import base64

def dashboard(request):
    data = MonitoringData.objects.all().order_by('timestamp')

    # Filters
    date = request.GET.get('date')
    container = request.GET.get('container')
    pallet = request.GET.get('pallet')
    product = request.GET.get('product')

    if date:
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            data = data.filter(timestamp__date=date_obj)
        except ValueError:
            pass

    if container:
        data = data.filter(container_code__icontains=container)

    if pallet:
        data = data.filter(pallet_position__icontains=pallet)

    if product:
        data = data.filter(product_description__icontains=product)

    alerts = data.filter(temperature__gt=-15) | data.filter(humidity__gt=85).order_by('-timestamp')
    labels = [d.timestamp.strftime('%H:%M') for d in data]
    temps = [d.temperature for d in data]
    hums = [d.humidity for d in data]

    # Extract metadata from first matching entry (if exists)
    metadata = data.first()

    context = {
        'data': data,
        'labels': labels,
        'temps': temps,
        'hums': hums,
        'metadata': metadata,
        'date' : date,
        'alerts': alerts,
        'request': request
    }
    return render(request, 'monitor/dashboard.html', context)

def latest_data_api(request):
    time_slots = ["%s:%02d %s" % ((h-1)%12+1, m, "AM" if h < 12 else "PM")
                  for h in range(7, 18) for m in (0, 30)]
    slot_data = {label: {'temp': None, 'hum': None} for label in time_slots}
    entries = MonitoringData.objects.filter(timestamp__hour__gte=7, timestamp__hour__lte=17)
    for e in entries:
        slot = e.timestamp.strftime("%I:%M %p").lstrip("0")
        if slot in slot_data:
            slot_data[slot] = {'temp': e.temperature, 'hum': e.humidity}
    labels = list(slot_data.keys())
    temps = [slot_data[k]['temp'] for k in labels]
    hums = [slot_data[k]['hum'] for k in labels]
    return JsonResponse({
        "labels": labels,
        "temperatures": temps,
        "humidities": hums,
        "temp_alert": any(t and t > -18 for t in temps),
        "humidity_alert": any(h and h > 85 for h in hums)
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
    ax1.set_ylim(-21, -14)
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax1.axhline(temp_threshold, color='red', linestyle='--', linewidth=1, alpha=0.5)

    ax2 = ax1.twinx()
    ax2.bar(labels, hums, color=humidity_colors, alpha=0.7)
    ax2.set_ylabel('Humidity (%)', color='#007BFF')
    ax2.tick_params(axis='y', labelcolor='#007BFF')
    ax2.set_ylim(70, 100)
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
