# Quick Setup Guide

## Step 1: Install Dependencies

Open PowerShell or Command Prompt in this directory and run:

```bash
# If you don't have a virtual environment set up:
python -m venv .venv

# Activate it (Windows):
.venv\Scripts\activate

# Or if that doesn't work:
.venv\Scripts\Activate.ps1

# Install dependencies:
pip install -r requirements.txt
```

## Step 2: Initialize Database

```bash
python database.py
```

You should see:
- "Database initialized successfully!"
- "Demo user created! Username: demo, Password: demo"

## Step 3: Run the App

```bash
python app.py
```

The app will start at: **http://127.0.0.1:5000**

Open your browser and go to that URL.

## Step 4: Login

Use the demo account:
- **Username:** demo
- **Password:** demo

Or register your own account!

## Quick Test

1. Login with demo/demo
2. Click "Import Grades"
3. Paste the Aeries text (from your request or copy from actual Aeries)
4. Click "Import Grades"
5. View your calculated grade!

## Troubleshooting

**"Python was not found"**
- Install Python from python.org
- Or use `py` command instead of `python`
- Or use `python3` if on Linux/Mac

**PowerShell execution policy error**
- Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Then try activating the venv again

**Module not found errors**
- Make sure you activated the virtual environment
- Make sure you ran `pip install -r requirements.txt`

**Can't access the website**
- Make sure the Flask app is running
- Check that nothing else is using port 5000
- Try http://localhost:5000 instead of 127.0.0.1:5000
