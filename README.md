# ToxicMeter Web Application

A Django project for analyzing toxicity in comments. 
This guide will walk you through setting up the project environment.

## Prerequisites

- Python 3.x
- Virtualenv
- Django (as per `requirements.txt`)

## Setup Guide

### 1. Clone the Repository

```bash
git clone <repository-url>
cd toxicmeter
```

### 2. Create a Virtual Environment

Create a virtual environment using `venv`:

```bash
python3 -m venv venv
```

Activate the virtual environment:

- **Linux/macOS:** `source venv/bin/activate`
- **Windows:** `venv\Scripts\activate`

### 3. Install Requirements

Install the necessary packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Setup Database (Optional)

If this project uses a database, run migrations to set up the tables:

```bash
python manage.py migrate
```

### 5. Run the Server

Start the Django development server:

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser to see the project.

### 6. Run the Tailwind Server

Start the Tailwind development server:

```bash
python manage.py tailwind start
```
---