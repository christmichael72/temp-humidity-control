# Temp & Humidity Control System

A Django-based monitoring dashboard for temperature and humidity data, featuring:
- Real-time dashboard with Chart.js visualizations
- EWMA smoothing and control limits
- Threshold-based alerts
- Data filtering by date, container, pallet, and product
- PDF/chart export (optional)

---

## 🚀 Getting Started
Install Python & Git

### 
1️⃣ Clone the Repository

bash
git clone https://github.com/christmichael72/temp-humidity-control.git
cd temp-humidity-control

2️⃣ Create & Activate a Virtual Environment

Windows (PowerShell)

py -3 -m venv .venv
.venv\Scripts\Activate

macOS / Linux
bash

python3 -m venv .venv
source .venv/bin/activate

3️⃣ Install Dependencies

bash

pip install --upgrade pip
pip install -r requirements.txt

5️⃣ Run Database Migrations

bash

python manage.py migrate

6️⃣ (Optional) Create Admin User

bash

python manage.py createsuperuser
Access admin at: http://127.0.0.1:8000/admin/

7️⃣ Run Development Server

bash

python manage.py runserver

Visit:

Dashboard → http://127.0.0.1:8000/

Admin Panel → http://127.0.0.1:8000/admin/