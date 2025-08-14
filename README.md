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
https://www.python.org/downloads/
https://git-scm.com/downloads

### 
1️⃣ Clone the Repository

Open your GitBash terminal:
<img width="1133" height="653" alt="Screenshot (90)" src="https://github.com/user-attachments/assets/d6608254-f1a1-4ad6-8a42-52ee3ca9d5e0" />
And run :

git clone https://github.com/christmichael72/temp-humidity-control.git

cd temp-humidity-control

<img width="592" height="383" alt="Screenshot (92)" src="https://github.com/user-attachments/assets/44586dcd-4987-41e7-9046-dc083cf90115" />

2️⃣ Create & Activate a Virtual Environment

For Windows (GitBash)

py -3 -m venv .venv

.venv\Scripts\Activate

<img width="577" height="375" alt="Screenshot (93)" src="https://github.com/user-attachments/assets/74c52e1a-7213-43a9-966f-0066b4273665" />

For macOS / Linux

bash

python3 -m venv .venv

source .venv/bin/activate

3️⃣ Install Dependencies

bash

pip install --upgrade pip

pip install -r requirements.txt

<img width="575" height="367" alt="Screenshot (94)" src="https://github.com/user-attachments/assets/26cd9f2d-88f8-4aeb-86ea-eb9d1d379071" />

5️⃣ Run Database Migrations

bash

python manage.py migrate

<img width="579" height="364" alt="Screenshot (95)" src="https://github.com/user-attachments/assets/cb3c34a6-81c8-443c-9cb5-7117b4ce33c3" />


6️⃣ Create Admin User

bash

python manage.py createsuperuser

<img width="573" height="378" alt="Screenshot (96)" src="https://github.com/user-attachments/assets/ea75e474-7f6a-4f28-a5a6-86a504086613" />

Access admin at: http://127.0.0.1:8000/admin/

7️⃣ Run Development Server

bash

python manage.py runserver

<img width="573" height="368" alt="Screenshot (97)" src="https://github.com/user-attachments/assets/4481c0ab-aa50-4686-97b1-266973e269ad" />

Visit:

Dashboard → http://127.0.0.1:8000/

Admin Panel → http://127.0.0.1:8000/admin/
