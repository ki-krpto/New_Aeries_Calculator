# How Everything Works - Simple Explanation

## The Main Idea

Traditional grade calculators just average percentages. But that's wrong! A 30/50 (60%) should count more than a 3/5 (60%) because it's worth more points.

**Our solution:** Sum up all the actual points in each category FIRST, then calculate the percentage.

## File Breakdown

### 1. `app.py` - The Main Application

This is the "brain" of the app. It handles all the web requests.

**Key parts:**
- **Routes**: URLs that users can visit (like `/login`, `/dashboard`, `/import`)
- **Authentication**: Makes sure users are logged in before they can see grades
- **Database queries**: Gets and saves data to SQLite

**Main Flow:**
1. User logs in → Flask-Login creates a session
2. User imports grades → Parser extracts data → Saves to database
3. User views class → Gets data from database → Calculates grade → Shows results

### 2. `database.py` - Database Setup

Creates 4 tables in SQLite:
- **users**: Who can login
- **classes**: Each class you're taking
- **categories**: Categories within a class (Tests, Labs, etc.) with their weights
- **assignments**: Individual assignments with points

**Key function:**
```python
def get_db_connection():
    conn = sqlite3.connect('grades.db')
    conn.row_factory = sqlite3.Row  # Lets us access columns by name
    return conn
```

This creates a connection to the database. Always remember to `conn.close()` when done!

### 3. `aeries_parser.py` - The Parser

This is the clever part. It takes messy copy-pasted text from Aeries and extracts structured data.

**Two main functions:**

#### `parse_aeries_grades(text)`
Uses regex to find patterns in the text:
- Class name (looks for `<< 1- Class Name- Trimester >>`)
- Teacher name (finds `Name Email` pattern)
- Categories and weights (parses the totals table)
- Each assignment (multi-line parsing)

Returns a dictionary:
```python
{
    'class_name': 'AP Physics',
    'teacher_name': 'John Doe',
    'categories': {'Tests': 60.0, 'Labs': 30.0, 'Classwork': 10.0},
    'assignments': [
        {'description': 'Test 1', 'category': 'Tests', 'points_earned': 45, 'points_possible': 50},
        # ... more assignments
    ]
}
```

#### `calculate_grade(assignments, categories)`
The grade calculation logic:

1. **Group by category**: Put all Tests together, all Labs together, etc.
2. **Sum points**: For each category, add up all points earned and all points possible
3. **Calculate percentage**: (total earned / total possible) × 100
4. **Apply weight**: percentage × category weight
5. **Sum contributions**: Add up all weighted contributions = final grade

**Example:**
```
Tests (60% of grade):
- Test 1: 45/50
- Test 2: 38/50
- Total: 83/100 = 83%
- Contribution: 83% × 60% = 49.8%

Labs (40% of grade):
- Lab 1: 28/30
- Lab 2: 26/30
- Total: 54/60 = 90%
- Contribution: 90% × 40% = 36%

Final Grade: 49.8% + 36% = 85.8%
```

### 4. Templates - The HTML Pages

**`base.html`** - The template all other pages extend
- Has the navigation bar
- Includes the CSS file
- Has a spot for flash messages (success/error alerts)
- Has a `{% block content %}` where other pages put their content

**Other templates:**
- `login.html` / `register.html` - Authentication forms
- `dashboard.html` - Shows all your classes
- `import.html` - Big textarea to paste Aeries data
- `class_view.html` - Shows grade breakdown and all assignments
- `add_assignment.html` / `edit_assignment.html` - Forms to manage assignments

**Jinja2 Syntax:**
- `{{ variable }}` - Print a variable
- `{% for item in list %}` - Loop through a list
- `{% if condition %}` - Conditional
- `{% extends "base.html" %}` - Inherit from another template

### 5. `style.css` - The Styling

Simple, clean CSS with:
- **Reset styles**: Makes everything look consistent
- **Navbar**: Dark blue bar at top
- **Cards**: White boxes with shadows for content
- **Tables**: Styled assignment and category tables
- **Buttons**: Primary (blue), secondary (gray), danger (red)
- **Forms**: Clean input fields and labels
- **Responsive**: Works on mobile (media queries at bottom)

## Key Python/Flask Concepts

### 1. Decorators
```python
@app.route('/dashboard')
@login_required
def dashboard():
    pass
```
- `@app.route()` - Maps a URL to a function
- `@login_required` - Only allows logged-in users

### 2. Flask Request/Response
```python
if request.method == 'POST':
    username = request.form.get('username')
    # ... process form
    return redirect(url_for('dashboard'))
```
- `request.form` - Get form data from POST
- `redirect()` - Send user to different page
- `url_for()` - Generate URL for a route name

### 3. Sessions
Flask-Login handles this automatically. When you call `login_user(user_obj)`, it creates a cookie in the browser. Then `current_user` is available in all routes.

### 4. Database Pattern
```python
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('INSERT INTO table VALUES (?, ?)', (val1, val2))
conn.commit()  # Save changes
conn.close()   # Always close!
```

### 5. SQLite Row Factory
```python
conn.row_factory = sqlite3.Row
user = conn.execute('SELECT * FROM users WHERE id = ?', (1,)).fetchone()
print(user['username'])  # Access by column name!
```

## How to Modify

### Change the parser for different Aeries formats
Edit `aeries_parser.py` and update the regex patterns. Use regex101.com to test patterns.

### Add new features to a class
1. Add column to database in `database.py`
2. Update INSERT/UPDATE queries in `app.py`
3. Update forms in templates
4. Update display in `class_view.html`

### Change styling
Edit `style.css`. The classes are named semantically (`.class-card`, `.grade-summary`, etc.).

### Add new routes
In `app.py`:
```python
@app.route('/new-page')
@login_required
def new_page():
    return render_template('new_page.html')
```

Create `templates/new_page.html`:
```html
{% extends "base.html" %}
{% block content %}
    <h1>My New Page</h1>
{% endblock %}
```

## Common Tasks

**Reset everything:**
```bash
rm grades.db
python database.py
```

**Check database contents:**
```bash
sqlite3 grades.db
sqlite> SELECT * FROM users;
sqlite> .exit
```

**Debug Flask:**
- Look at terminal output where you ran `python app.py`
- Add `print()` statements in routes
- Check browser console (F12) for frontend errors

**Test parser:**
```python
python
>>> from aeries_parser import parse_aeries_grades
>>> text = "..." # paste Aeries text
>>> result = parse_aeries_grades(text)
>>> print(result)
```

## What Happens When You Import Grades

1. User pastes text → POST to `/import`
2. `parse_aeries_grades(text)` extracts data
3. Create new class row in database
4. For each category, create category row
5. For each assignment, create assignment row with foreign keys
6. Redirect to `/class/<id>`
7. `view_class()` queries database for class, categories, assignments
8. `calculate_grade()` computes the final grade
9. Render template with all the data
10. Browser displays the results!

## Security Notes

- Passwords are hashed with werkzeug (never stored in plain text)
- SQL uses parameterized queries (protects against SQL injection)
- Flask-Login manages sessions securely
- `@login_required` prevents unauthorized access

## Next Steps

Now that you understand how it works, you can:
- Add a "What If" calculator to predict grades
- Add charts with matplotlib or Chart.js
- Export to PDF/Excel
- Add multiple grading periods
- Make the parser more robust
- Add dark mode
- Deploy it online with PythonAnywhere or Heroku

Have fun coding! 🚀
