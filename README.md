# 🏥 Pharmacy Management System

A full-stack **Pharmacy Management System** designed to manage **billing tokens, counters, pharmacy staff, and medicine preparation workflow** efficiently.  
This system supports **manual and automatic billing**, **FIFO token assignment**, and **automated prescription preparation** using smart logic and ML-based time estimation.

---

## 🚀 Features

### 🔹 Token & Billing Management
- Generate tokens for patients
- FIFO-based token queue
- Support for **multiple counters**
- **Manual billing completion**
- **Automatic billing completion** based on time
- Dynamic reassignment of waiting tokens to free counters

### 🔹 Pharmacy (Medicine Preparation)
- Automatic creation of prescriptions after billing
- Assignment of prescriptions to pharmacy staff
- Support for **manual & automatic medicine preparation completion**
- Staff busy/free state handling

### 🔹 Smart Automation
- Automatic handling when counters or staff become free
- Background auto-completion logic
- Ensures no duplicate prescriptions
- Edge cases handled (counter added later, staff added later)

### 🔹 Machine Learning Integration
- Predicts medicine preparation time based on medicine count
- Improves estimation accuracy for pharmacy operations

---

## 🛠 Tech Stack

- **Backend**: Django, Django REST Framework
- **Database**: SQLite (can be upgraded to PostgreSQL/MySQL)
- **ML**: Scikit-learn (Linear Regression)
- **Task Handling**: Celery (optional for background tasks)
- **Version Control**: Git & GitHub

---

## 📂 Project Structure

Backend/
├── pharmacy/
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   └── urls.py
│
├── tokens/
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   └── urls.py
│
├── patients/
│   ├── models.py
│   └── admin.py
│
├── ml/
│   ├── generate_data.py
│   ├── train_model.py
│   └── predict.py
│
├── manage.py
└── requirements.txt



---

## 🔄 System Workflow

### 1️⃣ Token Generation
- Patient generates a token
- Token is assigned to a free counter if available
- Else, token waits in FIFO queue

### 2️⃣ Billing Phase
- Billing can be completed:
  - **Manually** by staff
  - **Automatically** after billing time expires
- After billing:
  - Token is marked completed
  - Prescription is created (only once)

### 3️⃣ Pharmacy Phase
- Prescriptions move to pharmacy
- Assigned to free pharmacy staff
- Medicine preparation:
  - Manual finish
  - Automatic finish after predicted time

---

## 🔌 API Endpoints (Key)

### Token APIs
- `POST /api/tokens/<pharmacy_id>/generate/`
- `POST /api/tokens/set-medicine-count/`
- `POST /api/tokens/billing-done/`
- `GET  /api/tokens/<pharmacy_id>/display/`

### Pharmacy APIs
- `GET  /pharmacy/<pharmacy_id>/display/`
- `POST /pharmacy/finish/<token_number>/`
- `GET  /pharmacy/prescription/<token_number>/status/`

---

## ⚠️ Edge Cases Handled

- Multiple counters with limited staff
- Tokens generated when all counters are busy
- Counters added dynamically
- Staff added dynamically
- Manual + automatic billing mixed
- Manual + automatic pharmacy preparation mixed
- Duplicate prescription prevention
- FIFO consistency guaranteed

---

## ▶️ How to Run Locally

## 1️⃣Create Virtual Environment
python -m venv .venv
.venv\Scripts\activate   # Windows

## 2️⃣ Install Dependencies
pip install -r requirements.txt

## 3️⃣ Run Migrations
python manage.py makemigrations
python manage.py migrate

## 4️⃣ Create Superuser
python manage.py createsuperuser

## 5️⃣ Run Server
python manage.py runserver

## Future Enhancements

- Frontend UI (React / Flutter)

- Role-based authentication

- SMS / WhatsApp notifications

- Real-time dashboard

- Analytics & reports

- Cloud deployment
