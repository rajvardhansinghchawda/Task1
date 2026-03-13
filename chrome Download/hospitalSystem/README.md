# Mini Hospital Management System (HMS)

A modern, Django-based Hospital Management System with full appointment scheduling, automated email notifications via a microservice, and Google Calendar synchronization for both doctors and patients.

## 🚀 Key Features

- **Dual-Role Dashboards**: Specialized views for Doctors (slot management) and Patients (booking & doctor discovery).
- **Secure Authentication**: Email-based signup with OTP verification and seamless Google OAuth integration.
- **Smart Booking Engine**: Transactional booking logic to prevent overbooking and race conditions.
- **Google Calendar Integration**: Automatically creates calendar events for both parties upon appointment confirmation.
- **Real-time Notifications**: 
  - OTP verification emails.
  - Welcome emails for new users.
  - Booking confirmation emails to patients.
  - New appointment alerts to doctors.

## 🛠 Tech Stack

- **Backend**: Django (Python 3.13)
- **Database**: PostgreSQL
- **Authentication**: `django-allauth` (Customized for OTP and Social Signup)
- **Integrations**: Google Calendar API v3
- **Notifications**: Local Email Microservice (Node.js/Python compatible)
- **Styling**: Vanilla CSS with modern aesthetics

---

## 📋 Prerequisites

- **Python 3.13+**
- **PostgreSQL** (running locally or remotely)
- **Google Cloud Console Account** (for OAuth credentials)

---

## ⚙️ Installation & Setup

### 1. Clone & Environment
```bash
git clone https://github.com/rajvardhansinghchawda/Task1.git
cd hospitalSystem
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration (`.env`)
Copy the template and fill in your credentials:
```bash
cp .env.example .env
```
Ensure you provide:
- `DB_PASSWORD` for PostgreSQL.
- `EMAIL_HOST_PASSWORD` (Use a Gmail App Password).
- `GOOGLE_CALENDAR_REDIRECT_URI` (Matches your Google Cloud Console).

### 3. Google OAuth Setup
1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable **Google Calendar API**.
3. Create **OAuth 2.0 Client IDs** (Web Application).
4. Add Authorized Redirect URIs:
   - `http://127.0.0.1:8000/accounts/google/login/callback/`
   - `http://127.0.0.1:8000/integrations/oauth2callback/`
5. Download your secret and rename it to `client_secret.json` in the project root.

### 4. Database Setup
```bash
# Ensure your local PostgreSQL server is running
python manage.py migrate
python manage.py createsuperuser
```

---

## 🚦 Running the System

You need to run **two** separate servers:

### A. The Email Microservice
```bash
cd email-service
python local_server.py
```
*Listens on http://127.0.0.1:3000*

### B. The Django Application
```bash
# In the project root
python manage.py runserver
```
*Listens on http://127.0.0.1:8000*

---

## 🔗 Connectivity Logic

### Google Calendar Flow
- **Initiate**: Dashboard → Click "Connect Calendar".
- **Consent**: User grants `https://www.googleapis.com/auth/calendar` permissions.
- **Persistence**: The app requests a `refresh_token` (using `prompt='consent'`) to ensure the connection stays alive indefinitely.
- **Trigger**: When a patient books a slot, `create_calendar_event` is called for both the Doctor's and Patient's calendars.

### Email Flow
- The Django `notifications` app sends a JSON payload to the local email service.
- The service processes different types: `OTP_VERIFICATION`, `SIGNUP_WELCOME`, `BOOKING_CONFIRMATION`, etc.
- If the service is down, Django fails over to the standard SMTP backend configured in `.env`.

---

## 📂 Project Structure

- `users/`: Custom User model, OTP logic, and Role-based adapters.
- `doctors/`: Slot generation and doctor dashboards.
- `appointments/`: Booking logic and patient dashboards.
- `integrations/`: OAuth flows and Google API interaction.
- `email-service/`: The standalone microservice for handling SMTP tasks.
- `templates/`: Modern HTML UIs for all components.

---

## 🔒 Security
- **Strict Gitignore**: Secrets like `.env` and `client_secret.json` are excluded from version control.
- **Environment Variables**: Managed via `python-dotenv`.
- **Transaction Safety**: Uses `select_for_update()` to handle concurrent booking requests.
