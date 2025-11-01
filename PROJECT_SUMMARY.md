# 🎓 Aeries Grade Calculator - Project Summary

## What This Does

A web app that calculates your grades **the right way** - based on actual point values, not just averaging percentages. 

**The Problem:** A 30/50 assignment and a 3/5 assignment both = 60%, but the first is worth WAY more points. Traditional calculators don't account for this.

**Our Solution:** Sum all the points in each category FIRST, then calculate the percentage. This gives accurate grades that reflect the weight of each assignment.

## Quick Start

### Windows (Easiest):
1. Double-click `setup.bat` (installs everything)
2. Double-click `run.bat` (starts the app)
3. Open browser to http://127.0.0.1:5000
4. Login with: `demo` / `demo`

### Manual:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python database.py
python app.py
```

## Main Features

✅ **Copy-Paste Import** - Paste your entire Aeries gradebook, parser extracts everything  
✅ **Point-Based Math** - Real grade calculation using actual points  
✅ **User Accounts** - Register, login, secure password hashing  
✅ **Multiple Classes** - Manage all your classes in one place  
✅ **CRUD Operations** - Add/edit/delete assignments  
✅ **Category Weights** - Handles weighted categories (Tests 60%, Labs 30%, etc.)  
✅ **SQLite Database** - All data stored locally  
✅ **Clean UI** - Simple, responsive design  

## File Structure

```
📁 New_Aeries_Calculator/
├── 📄 app.py                     # Main Flask app (327 lines)
├── 📄 database.py                # Database setup
├── 📄 aeries_parser.py           # Text parser & grade calculator
├── 📄 requirements.txt           # Dependencies (flask, flask-login, werkzeug)
├── 📄 grades.db                  # SQLite database (created on first run)
│
├── 📁 templates/                 # HTML pages (Jinja2)
│   ├── base.html                # Base template with navbar
│   ├── login.html               # Login page
│   ├── register.html            # Registration
│   ├── dashboard.html           # View all classes
│   ├── import.html              # Import Aeries grades
│   ├── class_view.html          # View class & calculated grade
│   ├── add_assignment.html      # Add new assignment
│   └── edit_assignment.html     # Edit assignment
│
├── 📁 static/
│   └── style.css                # Styling (~350 lines)
│
├── 📁 Documentation/
│   ├── README.md                # Full technical documentation
│   ├── HOW_IT_WORKS.md          # Detailed explanations
│   ├── SETUP.md                 # Setup instructions
│   └── PROJECT_SUMMARY.md       # This file!
│
└── 📁 Scripts/
    ├── setup.bat                # Windows auto-setup
    └── run.bat                  # Windows run script
```

## How It Works (Simple Version)

### 1. Import Grades
User copies entire Aeries page → Parser uses regex to extract:
- Class name & teacher
- Categories & weights
- All assignments with points

### 2. Store in Database
SQLite stores:
- Users (with hashed passwords)
- Classes (linked to users)
- Categories (with weights, linked to classes)
- Assignments (with points, linked to categories)

### 3. Calculate Grade
For each category:
1. Sum all points earned
2. Sum all points possible
3. Calculate: (earned/possible) × 100
4. Multiply by category weight
5. Add up all weighted contributions = **Final Grade**

### 4. Display Results
Shows:
- Overall grade
- Category breakdown with actual points
- Table of all assignments
- Options to add/edit/delete

## Key Technologies

| Technology | Purpose |
|------------|---------|
| **Flask** | Python web framework |
| **Flask-Login** | User authentication & sessions |
| **SQLite** | Lightweight database |
| **Jinja2** | HTML templating |
| **Werkzeug** | Password hashing (security) |
| **Regex** | Parsing Aeries text |

## Database Schema

```
users (id, username, password, created_at)
  ↓
classes (id, user_id, class_name, teacher_name)
  ↓
categories (id, class_id, name, weight)
  ↓
assignments (id, class_id, category_id, description, points_earned, points_possible)
```

## Routes Overview

| URL | What It Does |
|-----|--------------|
| `/` | Home (redirects to dashboard or login) |
| `/login` | Login page |
| `/register` | Create account |
| `/dashboard` | View all your classes |
| `/import` | Import Aeries grades |
| `/class/<id>` | View class with calculated grade |
| `/class/<id>/add_assignment` | Add assignment |
| `/assignment/<id>/edit` | Edit assignment |
| `/assignment/<id>/delete` | Delete assignment |

## Example Grade Calculation

```
Class: AP Physics
Teacher: Ms. Smith

Categories:
- Tests & Quizzes: 60%
- Labs: 30%
- Classwork: 10%

Tests & Quizzes:
  Unit 1 Test: 34.83/50
  Quiz 1: 7/10
  Quiz 2: 6/10
  → Total: 47.83/70 = 68.33%
  → Weighted: 68.33% × 60% = 41.0%

Labs:
  Lab 1: 22/25
  Lab 2: 21/25
  → Total: 43/50 = 86%
  → Weighted: 86% × 30% = 25.8%

Classwork:
  Homework 1: 10/10
  Homework 2: 10/10
  → Total: 20/20 = 100%
  → Weighted: 100% × 10% = 10%

Final Grade: 41.0% + 25.8% + 10% = 76.8% (C+)
```

## Security Features

✅ Password hashing (werkzeug PBKDF2)  
✅ SQL injection protection (parameterized queries)  
✅ Session management (Flask-Login)  
✅ Login required decorators  
✅ User data isolation (queries filtered by user_id)  

## Next Steps / Ideas

- [ ] Grade prediction ("What do I need on final?")
- [ ] Charts/graphs visualization
- [ ] Export to PDF/CSV
- [ ] Multiple grading periods
- [ ] Dark mode
- [ ] Mobile app version
- [ ] Share grades with parents
- [ ] GPA calculator
- [ ] "What If" scenarios

## Known Limitations

- Parser is specific to current Aeries format (may break if they update)
- No support for extra credit yet
- Single grading period only
- Desktop-focused (mobile works but not optimized)

## Troubleshooting

**App won't start?**
→ Run `setup.bat` or check SETUP.md

**Parser not working?**
→ Make sure you copy the ENTIRE Aeries page including the category totals

**Wrong grade calculated?**
→ Check that category weights add up to 100% in Aeries

**Can't login?**
→ Use demo account: demo/demo

## Learning Resources

Since you know Python better than JS, this is a GREAT project because:
- **90% Python** (Flask routes, database, parser)
- **10% HTML/CSS** (mostly templates)
- **0% JavaScript** (not needed!)

**To learn more:**
1. Flask Tutorial: https://flask.palletsprojects.com/tutorial/
2. SQLite in Python: https://docs.python.org/3/library/sqlite3.html
3. Regex: https://regex101.com (test patterns)
4. Flask-Login: https://flask-login.readthedocs.io/

## Credits

Built for students who want accurate grade calculations based on actual point values, not misleading percentage averages.

Made with ❤️ and Python 🐍
