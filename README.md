# Expense Tracker

## 🛠️ Local Setup Guide

### 1. Clone the Repository
```bash
git clone <repository-url>
cd expense_tracker
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Local Settings
Copy the sample settings file and update it with your local configuration:
```bash
cp sample_settings.py local_settings.py
```
Then open `local_settings.py` and update your database credentials:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',       # e.g. expense_tracker
        'USER': 'your_db_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Apply Migrations
```bash
python manage.py migrate
```

### 6. Create a Superuser
```bash
python manage.py createsuperuser
```

### 7. Run the Development Server
```bash
python manage.py runserver
```

---

> ⚠️ **Important**
> - Never push `local_settings.py` to git — it is in `.gitignore`
> - Always edit only `local_settings.py` for your local DB and secrets
> - `sample_settings.py` is the template — do not put real credentials there
