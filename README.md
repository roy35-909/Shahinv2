# Django Project with Celery & Firebase Integration

A Django application with Celery task scheduling for push notifications, Firebase authentication (Google & Apple login), and automated badge creation.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [Firebase Setup](#firebase-setup)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

## Features

- **Django REST Framework** for API endpoints
- **Celery Worker** for asynchronous task processing
- **Celery Beat** for scheduled tasks
- **Django Celery Scheduler** for managing scheduled push notifications
- **Google OAuth 2.0** authentication for web, Android, and iOS
- **Apple Sign In** authentication
- **Stripe Payment Integration** for subscriptions and payments
- **Email Notifications** with Gmail/SMTP support
- **OpenAI API Integration** for AI-powered features
- **Automated Badge Creation** system
- **CORS enabled** for cross-origin requests

## Prerequisites

Before running this project, ensure you have the following installed:

- Python 3.8 or higher
- pip (Python package manager)
- Redis or RabbitMQ (for Celery broker)
- PostgreSQL/MySQL (recommended) or SQLite for development
- Google Cloud Project (for OAuth)
- Apple Developer Account (for Apple Sign In)
- Stripe Account (for payments)
- OpenAI API Key (optional, if using AI features)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the project root directory:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=*
CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOW_CREDENTIALS=True

# Database Configuration (Optional - if not using SQLite)
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_HOST_USER=office.simantaroy@gmail.com
EMAIL_HOST_PASSWORD=your-email-password-or-app-password

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Google OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
GOOGLE_OAUTH_CALLBACK_URL=http://localhost:8000/auth/google/callback

# OpenAI API (if using AI features)
OPENAI_API_KEY=your-openai-api-key

# Stripe Payment Configuration
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret
STRIPE_PUBLISHER_SECRET=your-stripe-publishable-key

# Android Client Configuration
ANDROID_CLIENT_ID=your-android-client-id
ANDROID_PACKAGE_NAME=com.yourapp.package

# iOS Client Configuration
IOS_CLIENT_ID=your-ios-client-id
IOS_BUNDLE_ID=com.yourapp.bundle

# Apple Sign In Configuration
APPLE_PUBLIC_KEYS_URL=https://appleid.apple.com/auth/keys
APPLE_AUDIENCE=your-apple-service-id
APPLE_SHARED_SECRET=your-apple-shared-secret
```

**Important Notes:**
- Replace all placeholder values with your actual credentials
- Never commit the `.env` file to version control
- Add `.env` to your `.gitignore` file
- For production, set `DEBUG=False` and specify exact domains in `ALLOWED_HOSTS`
- Use Django's `django-environ` or `python-decouple` to load environment variables

### 5. Database Migration

```bash
python manage.py migrate
```

## Configuration

### Third-Party Service Configuration

#### Google OAuth Setup

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable OAuth 2.0**
   - Navigate to APIs & Services > Credentials
   - Create OAuth 2.0 Client ID
   - Add authorized redirect URIs: `http://localhost:8000/auth/google/callback`
   - Copy Client ID and Client Secret to `.env`

3. **Configure Android Client**
   - Create Android OAuth client
   - Add SHA-1 fingerprint
   - Copy Android Client ID to `.env`

4. **Configure iOS Client**
   - Create iOS OAuth client
   - Add Bundle ID
   - Copy iOS Client ID to `.env`

#### Apple Sign In Setup

1. **Apple Developer Account**
   - Go to [Apple Developer Portal](https://developer.apple.com/)
   - Navigate to Certificates, Identifiers & Profiles

2. **Create Service ID**
   - Register a Services ID
   - Enable Sign in with Apple
   - Configure return URLs and domains

3. **Generate Private Key**
   - Create a Sign in with Apple private key
   - Download and save securely

4. **Configure Environment**
   - Set `APPLE_AUDIENCE` to your Service ID
   - Add shared secret for in-app purchases/subscriptions
   - Apple public keys URL is standard: `https://appleid.apple.com/auth/keys`

#### Stripe Payment Setup

1. **Create Stripe Account**
   - Go to [Stripe Dashboard](https://dashboard.stripe.com/)
   - Complete account setup

2. **Get API Keys**
   - Navigate to Developers > API Keys
   - Copy Secret Key and Publishable Key to `.env`

3. **Setup Webhooks**
   - Go to Developers > Webhooks
   - Add endpoint: `https://yourdomain.com/webhooks/stripe/`
   - Select events to listen for
   - Copy webhook signing secret to `.env`

#### Email Configuration

1. **Gmail App Password** (if using Gmail)
   - Enable 2-Factor Authentication on your Google account
   - Generate App Password: Account > Security > App Passwords
   - Use this password in `EMAIL_HOST_PASSWORD`

2. **Alternative Email Services**
   - SendGrid, Mailgun, or AWS SES
   - Follow their documentation for SMTP credentials

#### OpenAI API Setup (Optional)

1. **Create OpenAI Account**
   - Go to [OpenAI Platform](https://platform.openai.com/)
   - Navigate to API Keys

2. **Generate API Key**
   - Create new secret key
   - Copy to `.env` as `OPENAI_API_KEY`

### Redis Setup

Ensure Redis is running for Celery:

```bash
# Install Redis (Ubuntu/Debian)
sudo apt-get install redis-server

# Start Redis
sudo service redis-server start

# Verify Redis is running
redis-cli ping  # Should return PONG
```

## Running the Project

Follow these steps in order to run the complete application:

### 1. Create Badges

Execute the badge creation script:

```bash
chmod +x create_badges.sh  # Make script executable (first time only)
./create_badges.sh
```

This script creates necessary badge configurations for the application.

### 2. Create Superuser

Create an admin account for Django admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter username, email, and password.

### 3. Start Django Development Server

```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

### 4. Start Celery Worker

Open a new terminal window/tab:

```bash
source venv/bin/activate  # Activate virtual environment
celery -A <project_name> worker --loglevel=info
```

Replace `<project_name>` with your Django project name (the folder containing `settings.py`).

### 5. Start Celery Beat Scheduler

Open another terminal window/tab:

```bash
source venv/bin/activate  # Activate virtual environment
celery -A <project_name> beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

This starts the Celery beat scheduler which manages periodic tasks for push notifications.

### Production Deployment

For production, use process managers to keep services running:

```bash
# Using supervisor or systemd for process management
# Example with celery multi:

celery -A <project_name> multi start worker1 \
    --pidfile=/var/run/celery/%n.pid \
    --logfile=/var/log/celery/%n%I.log

celery -A <project_name> beat \
    --pidfile=/var/run/celery/beat.pid \
    --logfile=/var/log/celery/beat.log \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## Firebase Setup

### Google Login Configuration

1. Enable Google Sign-in in Firebase Console
2. Add authorized domains in Firebase Authentication settings
3. Frontend integration:

```javascript
import { signInWithPopup, GoogleAuthProvider } from 'firebase/auth';

const provider = new GoogleAuthProvider();
const result = await signInWithPopup(auth, provider);
```

### Apple Login Configuration

1. Enable Apple Sign-in in Firebase Console
2. Configure Apple Developer account:
   - Create Service ID
   - Configure Sign in with Apple
   - Add return URLs
3. Add Team ID and Key ID in Firebase

### Push Notification Setup

1. **Web Push Notifications**
   - Generate Web Push certificates in Firebase Console
   - Add `firebase-messaging-sw.js` to your static files

2. **Mobile Push Notifications**
   - Add `google-services.json` (Android) or `GoogleService-Info.plist` (iOS)
   - Configure FCM in your mobile app

3. **Backend Implementation**
   - Device tokens are stored when users log in
   - Scheduled tasks send notifications via Celery Beat

## Project Structure

```
project-root/
├── manage.py
├── create_badges.sh
├── requirements.txt
├── .env
├── firebase-credentials.json
├── <project_name>/
│   ├── __init__.py
│   ├── settings.py
│   ├── celery.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── authentication/
│   ├── notifications/
│   └── badges/
└── static/
```

## Scheduled Push Notifications

The project uses Django Celery Beat to schedule push notifications at specific time windows.

### Managing Scheduled Tasks

1. **Via Django Admin**
   - Access `/admin/django_celery_beat/`
   - Create Periodic Tasks
   - Set intervals, crontabs, or clocked schedules

2. **Programmatically**

```python
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

# Create interval schedule (every 30 minutes)
schedule, created = IntervalSchedule.objects.get_or_create(
    every=30,
    period=IntervalSchedule.MINUTES,
)

# Create periodic task
PeriodicTask.objects.create(
    interval=schedule,
    name='Send Push Notification',
    task='apps.notifications.tasks.send_scheduled_notification',
    args=json.dumps(['user_id', 'notification_message']),
)
```

## Troubleshooting

### Celery Worker Not Starting

- Verify Redis/RabbitMQ is running
- Check `CELERY_BROKER_URL` in settings
- Ensure virtual environment is activated

### Firebase Authentication Issues

- Verify Firebase credentials in `.env`
- Check Firebase Console for enabled auth methods
- Ensure API keys are not restricted inappropriately

### Push Notifications Not Sending

- Verify FCM server key is correct
- Check device tokens are being saved correctly
- Review Celery worker logs for errors
- Ensure Firebase Cloud Messaging is enabled

### Database Migration Errors

```bash
# Reset migrations if needed (development only)
python manage.py migrate --run-syncdb
```

### Permission Denied on create_badges.sh

```bash
chmod +x create_badges.sh
```

## Additional Commands

### Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Run Tests

```bash
python manage.py test
```

### Monitor Celery Tasks

```bash
# Flower - Celery monitoring tool
pip install flower
celery -A <project_name> flower
```

Access Flower at `http://localhost:5555`

## Support

For issues and questions:
- Check Django documentation: https://docs.djangoproject.com/
- Celery documentation: https://docs.celeryq.dev/
- Firebase documentation: https://firebase.google.com/docs

