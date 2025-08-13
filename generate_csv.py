import pandas as pd
import numpy as np
from datetime import datetime

# Load original CSV to get categories and actual daily patterns
original_df = pd.read_csv("monitoring_data.csv")
original_df['timestamp'] = pd.to_datetime(original_df['timestamp'])

# Average daily pattern by hour
avg_temp_by_hour = original_df.groupby(original_df['timestamp'].dt.hour)['temperature'].mean()
avg_hum_by_hour = original_df.groupby(original_df['timestamp'].dt.hour)['humidity'].mean()

# New date range
start = datetime(2025, 6, 15, 1, 0)
end = datetime(2025, 7, 8, 0, 0)
timestamps = pd.date_range(start=start, end=end, freq='60min')

temperature_values = []
humidity_values = []

i = 0
while i < len(timestamps):
    hour = timestamps[i].hour

    # Base values from daily pattern + noise
    base_temp = avg_temp_by_hour.get(hour, avg_temp_by_hour.mean()) + np.random.uniform(-0.5, 0.5)
    base_hum = avg_hum_by_hour.get(hour, avg_hum_by_hour.mean()) + np.random.uniform(-1, 1)

    # Check if starting an incident
    if np.random.rand() < 0.03:  # ~3% chance to start incident
        duration = np.random.randint(2, 5)  # 1–2 hours
        # Gradually ramp up from last value (or base_temp if start of data)
        last_temp = temperature_values[-1] if temperature_values else base_temp
        last_hum = humidity_values[-1] if humidity_values else base_hum

        target_temp = np.random.uniform(-15, -14)
        target_hum = np.random.uniform(88, 90)

        temp_step = (target_temp - last_temp) / duration
        hum_step = (target_hum - last_hum) / duration

        for j in range(duration):
            temperature_values.append(round(last_temp + temp_step * (j + 1) + np.random.uniform(-0.2, 0.2), 1))
            humidity_values.append(round(last_hum + hum_step * (j + 1) + np.random.uniform(-0.5, 0.5), 1))
            i += 1
            if i >= len(timestamps):
                break
        continue  # skip to next loop
    else:
        temperature_values.append(round(base_temp, 1))
        humidity_values.append(round(base_hum, 1))
        i += 1

# Build DataFrame
new_df = pd.DataFrame({
    "timestamp": timestamps,
    "temperature": temperature_values[:len(timestamps)],
    "humidity": humidity_values[:len(timestamps)],
    "container_code": np.random.choice(original_df['container_code'].unique(), len(timestamps)),
    "pallet_position": np.random.choice(original_df['pallet_position'].unique(), len(timestamps)),
    "product_description": np.random.choice(original_df['product_description'].unique(), len(timestamps)),
})

# Save CSV
new_df.to_csv("monitoring_data_generated_smooth_alerts.csv", index=False)
print("✅ Generated CSV with smooth, gradual spikes")
