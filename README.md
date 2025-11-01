# Aeries Grade Calculator

A Python/Flask web application that calculates grades based on **actual point values** instead of just percentages. This matters because a 30/50 assignment should have more weight than a 3/5 assignment, even though both are 60%.

## Features

- **User Authentication**: Register and login with secure password hashing
- **Aeries Import**: Copy-paste your entire Aeries gradebook and automatically parse all assignments
- **Point-Based Calculation**: Grades calculated based on actual points, not simple percentage averages
- **Category Weighting**: Supports weighted categories (e.g., Tests 60%, Labs 30%, Classwork 10%)
- **CRUD Operations**: Add, edit, and delete assignments
- **Multiple Classes**: Manage grades for multiple classes
- **SQLite Database**: All data stored locally in a simple database

## How It Works

### 1. Architecture Overview

```
New_Aeries_Calculator/
├── app.py                 # Main Flask application with all routes
├── database.py            # Database setup and initialization
├── aeries_parser.py       # Parses copy-pasted Aeries text
├── grades.db             # SQLite database (created on first run)
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates (Jinja2)
│   ├── base.html         # Base template with navbar
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # Shows all classes
│   ├── import.html       # Import Aeries grades
│   ├── class_view.html   # View class and calculated grade
│   ├── add_assignment.html
│   └── edit_assignment.html
└── static/
    └── style.css         # Styling
```

### 2. Database Schema

**Users Table**
- `id`: Primary key
- `username`: Unique username
- `password`: Hashed password (using werkzeug)
- `created_at`: Timestamp

**Classes Table**
- `id`: Primary key
- `user_id`: Foreign key to users
- `class_name`: Name of the class
- `teacher_name`: Teacher's name
- `created_at`: Timestamp

**Categories Table**
- `id`: Primary key
- `class_id`: Foreign key to classes
- `name`: Category name (e.g., "Tests & Quizzes", "Labs", "Classwork")
- `weight`: Percentage weight (e.g., 60.0 for 60%)

**Assignments Table**
- `id`: Primary key
- `class_id`: Foreign key to classes
- `category_id`: Foreign key to categories
- `description`: Assignment name
- `points_earned`: Points you earned (can be NULL if not graded)
- `points_possible`: Total points possible
- `comment`: Optional comment
- `date_completed`: Date completed
- `due_date`: Due date

### 3. How Grade Calculation Works

The key difference from percentage-based calculators is that we sum **actual points** within each category before calculating percentages.

**Example:**
```python
Category: Tests & Quizzes (60% of grade)
- Test 1: 34.83/50 points
- Quiz 1: 7/10 points
- Quiz 2: 6/10 points

Total: 47.83/70 points = 68.33%
Contribution to final grade: 68.33% × 60% = 41.0%
```

**Code Flow:**
1. `aeries_parser.py` → `calculate_grade()` function
2. Groups assignments by category
3. For each category:
   - Sums points_earned and points_possible
   - Calculates percentage: (earned/possible) × 100
   - Calculates weighted contribution: percentage × weight
4. Final grade = sum of all weighted contributions

### 4. Aeries Parser

The `aeries_parser.py` file extracts data from copy-pasted Aeries text using regex patterns:

- **Class name**: Looks for pattern like `<< 1- IB Lang/LitHL1A- Trimester 1 >>`
- **Teacher**: Finds name and email pattern
- **Categories**: Parses the category totals table at the bottom
- **Assignments**: Uses multi-line parsing to extract:
  - Assignment number and description
  - Category
  - Points earned / points possible
  - Comments (like "retake", "Late", etc.)

### 5. Flask Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home page (redirects based on auth status) |
| `/login` | GET, POST | Login page |
| `/register` | GET, POST | Registration page |
| `/logout` | GET | Logout and redirect to login |
| `/dashboard` | GET | View all classes (requires auth) |
| `/import` | GET, POST | Import Aeries grades (requires auth) |
| `/class/<id>` | GET | View class with calculated grade (requires auth) |
| `/class/<id>/add_assignment` | GET, POST | Add new assignment (requires auth) |
| `/assignment/<id>/edit` | GET, POST | Edit assignment (requires auth) |
| `/assignment/<id>/delete` | POST | Delete assignment (requires auth) |

### 6. Authentication

- Uses **Flask-Login** for session management
- Passwords hashed with **werkzeug.security** (pbkdf2:sha256)
- Demo account created on first run: `username: demo`, `password: demo`
- `@login_required` decorator protects routes

## Installation & Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize database:**
   ```bash
   python database.py
   ```
   This creates `grades.db` and a demo user.

3. **Run the application:**
   ```bash
   python app.py
   ```
   App runs on `http://127.0.0.1:5000`

4. **Login:**
   - Use demo account: `demo` / `demo`
   - Or register a new account

## How to Use

1. **Import Grades:**
   - Go to Aeries → Gradebook Details
   - Select all (Ctrl+A) and copy (Ctrl+C)
   - In the app, click "Import Grades"
   - Paste the text and submit
   - The parser will extract all assignments and categories

2. **View Your Grade:**
   - Click on a class to see the calculated grade
   - View category breakdown showing actual points
   - See contribution of each category to final grade

3. **Manage Assignments:**
   - Click "Add Assignment" to manually add one
   - Click "Edit" on any assignment to modify it
   - Click "Delete" to remove an assignment
   - Grade automatically recalculates

## Key Python Concepts Used

### 1. SQLite with Context Managers
```python
def get_db_connection():
    conn = sqlite3.connect('grades.db')
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

# Usage:
conn = get_db_connection()
user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
conn.close()
```

### 2. Flask Sessions & Authentication
```python
from flask_login import LoginManager, login_user, current_user, login_required

# Protect routes
@app.route('/dashboard')
@login_required
def dashboard():
    # Only accessible if logged in
    pass
```

### 3. Jinja2 Templates
```html
{% extends "base.html" %}

{% block content %}
    {% for class in classes %}
        <h3>{{ class['class_name'] }}</h3>
    {% endfor %}
{% endblock %}
```

### 4. Regex for Parsing
```python
# Extract scores like "10 / 10" or "7.78 / 10"
score_match = re.search(r'([\d.]+|)\s*/\s*([\d.]+)', text)
points_earned = float(score_match.group(1)) if score_match.group(1) else None
points_possible = float(score_match.group(2))
```

## Future Enhancements

- Add grade prediction ("What do I need on the final?")
- Export grades to CSV
- Support for multiple grading periods
- Dark mode
- Mobile responsive improvements
- Add charts/graphs for grade visualization

## Troubleshooting

**Parser not working?**
- Make sure you copy the ENTIRE Aeries gradebook page
- Check that category totals are visible at the bottom
- The parser looks for specific patterns - if Aeries changes their format, the regex may need updates

**Database errors?**
- Delete `grades.db` and run `python database.py` to recreate

**Can't login?**
- Use demo account: `demo` / `demo`
- Check that the database was initialized

## License

This is a personal project for educational purposes. Feel free to modify and extend it!
