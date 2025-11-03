from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from database import get_db_connection, init_db
from aeries_parser import parse_aeries_grades, calculate_grade

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for sessions

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'])
    return None

# Initialize database on startup
with app.app_context():
    if not os.path.exists('grades.db'):
        init_db()

@app.route('/')
def home():
    """Home page - redirects to dashboard if logged in, otherwise to login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            user_obj = User(user['id'], user['username'])
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        
        # Check if user already exists
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user:
            flash('Username already exists', 'error')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        hashed_password = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard showing all classes"""
    conn = get_db_connection()
    classes = conn.execute(
        'SELECT * FROM classes WHERE user_id = ? ORDER BY created_at DESC',
        (current_user.id,)
    ).fetchall()
    conn.close()
    
    return render_template('dashboard.html', classes=classes)

@app.route('/add_class', methods=['GET', 'POST'])
@login_required
def add_class():
    """Create a new class with manual grade entry"""
    if request.method == 'POST':
        class_name = request.form.get('class_name', '').strip()
        teacher_name = request.form.get('teacher_name', '').strip()
        
        if not class_name:
            flash('Please enter a class name', 'error')
            return redirect(url_for('add_class'))
            
        # Create a new class with default category
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO classes (user_id, class_name, teacher_name) VALUES (?, ?, ?)',
                (current_user.id, class_name, teacher_name)
            )
            class_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            
            # Add default category
            conn.execute(
                'INSERT INTO categories (class_id, name, weight) VALUES (?, ?, ?)',
                (class_id, 'Assignments', 100.0)
            )
            conn.commit()
            flash(f'Class "{class_name}" created successfully!', 'success')
            return redirect(url_for('view_class', class_id=class_id))
        finally:
            conn.close()
    
    return render_template('add_class.html')

@app.route('/class/<int:class_id>')
@login_required
def view_class(class_id):
    """View a specific class with all assignments and calculated grade"""
    conn = get_db_connection()
    
    # Get class info
    class_info = conn.execute(
        'SELECT * FROM classes WHERE id = ? AND user_id = ?',
        (class_id, current_user.id)
    ).fetchone()
    
    if not class_info:
        flash('Class not found', 'error')
        conn.close()
        return redirect(url_for('dashboard'))
    
    # Get categories
    categories = conn.execute(
        'SELECT * FROM categories WHERE class_id = ?',
        (class_id,)
    ).fetchall()
    
    # Get assignments grouped by category
    assignments = conn.execute(
        'SELECT a.*, c.name as category_name FROM assignments a JOIN categories c ON a.category_id = c.id WHERE a.class_id = ? ORDER BY c.name, a.id',
        (class_id,)
    ).fetchall()
    
    conn.close()
    
    # Convert to dictionaries for calculation
    categories_dict = {cat['name']: cat['weight'] for cat in categories}
    assignments_list = [dict(assignment) for assignment in assignments]
    
    # Rename category field for calculation
    for assignment in assignments_list:
        assignment['category'] = assignment['category_name']
    
    # Calculate grade
    grade_info = calculate_grade(assignments_list, categories_dict)
    
    return render_template('class_view.html', 
                         class_info=class_info, 
                         categories=categories,
                         assignments=assignments,
                         grade_info=grade_info)

@app.route('/class/<int:class_id>/add_assignment', methods=['GET', 'POST'])
@login_required
def add_assignment(class_id):
    """Add a new assignment to a class"""
    conn = get_db_connection()
    
    # Verify class belongs to user
    class_info = conn.execute(
        'SELECT * FROM classes WHERE id = ? AND user_id = ?',
        (class_id, current_user.id)
    ).fetchone()
    
    if not class_info:
        flash('Class not found', 'error')
        conn.close()
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        points_earned = request.form.get('points_earned')
        points_possible = request.form.get('points_possible')
        comment = request.form.get('comment', '')
        
        # Convert empty string to None for points_earned
        points_earned = float(points_earned) if points_earned else None
        
        conn.execute(
            'INSERT INTO assignments (class_id, category_id, description, points_earned, points_possible, comment) VALUES (?, ?, ?, ?, ?, ?)',
            (class_id, category_id, description, points_earned, float(points_possible), comment)
        )
        conn.commit()
        conn.close()
        
        flash('Assignment added successfully!', 'success')
        return redirect(url_for('view_class', class_id=class_id))
    
    # Get categories for the form
    categories = conn.execute(
        'SELECT * FROM categories WHERE class_id = ?',
        (class_id,)
    ).fetchall()
    conn.close()
    
    return render_template('add_assignment.html', class_info=class_info, categories=categories)

@app.route('/assignment/<int:assignment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_assignment(assignment_id):
    """Edit an existing assignment"""
    conn = get_db_connection()
    
    # Get assignment and verify user owns it
    assignment = conn.execute(
        'SELECT a.*, c.user_id FROM assignments a JOIN classes c ON a.class_id = c.id WHERE a.id = ?',
        (assignment_id,)
    ).fetchone()
    
    if not assignment or assignment['user_id'] != current_user.id:
        flash('Assignment not found', 'error')
        conn.close()
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        points_earned = request.form.get('points_earned')
        points_possible = request.form.get('points_possible')
        comment = request.form.get('comment', '')
        
        # Convert empty string to None for points_earned
        points_earned = float(points_earned) if points_earned else None
        
        conn.execute(
            'UPDATE assignments SET description = ?, category_id = ?, points_earned = ?, points_possible = ?, comment = ? WHERE id = ?',
            (description, category_id, points_earned, float(points_possible), comment, assignment_id)
        )
        conn.commit()
        conn.close()
        
        flash('Assignment updated successfully!', 'success')
        return redirect(url_for('view_class', class_id=assignment['class_id']))
    
    # Get categories for the form
    categories = conn.execute(
        'SELECT * FROM categories WHERE class_id = ?',
        (assignment['class_id'],)
    ).fetchall()
    conn.close()
    
    return render_template('edit_assignment.html', assignment=assignment, categories=categories)

@app.route('/assignment/<int:assignment_id>/delete', methods=['POST'])
@login_required
def delete_assignment(assignment_id):
    """Delete an assignment"""
    conn = get_db_connection()
    
    # Get assignment and verify user owns it
    assignment = conn.execute(
        'SELECT a.*, c.user_id FROM assignments a JOIN classes c ON a.class_id = c.id WHERE a.id = ?',
        (assignment_id,)
    ).fetchone()
    
    if not assignment or assignment['user_id'] != current_user.id:
        flash('Assignment not found', 'error')
        conn.close()
        return redirect(url_for('dashboard'))
    
    class_id = assignment['class_id']
    
    conn.execute('DELETE FROM assignments WHERE id = ?', (assignment_id,))
    conn.commit()
    conn.close()
    
    flash('Assignment deleted successfully!', 'success')
    return redirect(url_for('view_class', class_id=class_id))


@app.route('/class/<int:class_id>/delete', methods=['POST'])
@login_required
def delete_class(class_id):
    """Delete a class and all its assignments and categories"""
    conn = get_db_connection()
    
    # First verify the class exists and belongs to the current user
    class_info = conn.execute(
        'SELECT * FROM classes WHERE id = ? AND user_id = ?',
        (class_id, current_user.id)
    ).fetchone()
    
    if not class_info:
        flash('Class not found or you do not have permission to delete it', 'error')
        conn.close()
        return redirect(url_for('dashboard'))
    
    try:
        # Delete all assignments for this class (cascading delete should handle this, but being explicit)
        conn.execute('DELETE FROM assignments WHERE class_id = ?', (class_id,))
        # Delete all categories for this class
        conn.execute('DELETE FROM categories WHERE class_id = ?', (class_id,))
        # Delete the class
        conn.execute('DELETE FROM classes WHERE id = ?', (class_id,))
        
        conn.commit()
        flash(f'Class "{class_info["class_name"]}" and all its data have been deleted.', 'success')
    except Exception as e:
        conn.rollback()
        flash('An error occurred while deleting the class.', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)