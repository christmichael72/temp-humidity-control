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
Open your GitBash terminal:
<img width="1133" height="653" alt="Screenshot (90)" src="https://github.com/user-attachments/assets/d6608254-f1a1-4ad6-8a42-52ee3ca9d5e0" />
And run :

git clone https://github.com/christmichael72/temp-humidity-control.git
cd temp-humidity-control

2️⃣ Create & Activate a Virtual Environment

For Windows (GitBash)

py -3 -m venv .venv
.venv\Scripts\Activate

For macOS / Linux

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

6️⃣ Create Admin User

bash

python manage.py createsuperuser
Access admin at: http://127.0.0.1:8000/admin/

7️⃣ Run Development Server

bash

python manage.py runserver

Visit:

Dashboard → http://127.0.0.1:8000/

Admin Panel → http://127.0.0.1:8000/admin/
