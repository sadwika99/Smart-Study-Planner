from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from config import Config
from models import User, Subject
from dp_logic import optimize_study_plan
from bson.objectid import ObjectId

app = Flask(__name__)
app.config.from_object(Config)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class UserSession(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.name = user_data['name']
        self.email = user_data['email']
        self.role = user_data['role']

@login_manager.user_loader
def load_user(user_id):
    user_data = User.find_user_by_id(user_id)
    if user_data:
        return UserSession(user_data)
    return None

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.find_user_by_email(email):
            flash('Email already exists', 'error')
            return redirect(url_for('register'))
        
        User.create_user(name, email, password)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_data = User.find_user_by_email(email)
        if user_data and bcrypt.check_password_hash(user_data['password'], password):
            user_obj = UserSession(user_data)
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    subjects = Subject.get_subjects_by_user(current_user.id)
    return render_template('dashboard.html', subjects=subjects)

@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.get_all_users()
    subjects = Subject.get_all_subjects()
    return render_template('admin.html', users=users, total_subjects=len(subjects))

@app.route('/add_subject', methods=['POST'])
@login_required
def add_subject():
    name = request.form.get('name')
    study_time = request.form.get('study_time')
    importance = request.form.get('importance')
    
    Subject.add_subject(current_user.id, name, study_time, importance)
    flash('Subject added successfully', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_subject/<subject_id>')
@login_required
def delete_subject(subject_id):
    Subject.delete_subject(subject_id)
    flash('Subject deleted', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_user/<user_id>')
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    
    User.delete_user(user_id)
    flash('User and their subjects deleted', 'success')
    return redirect(url_for('admin'))

@app.route('/optimize', methods=['POST'])
@login_required
def optimize():
    try:
        available_time = int(request.form.get('available_time', 0))
        subjects = list(Subject.get_subjects_by_user(current_user.id))
        
        print(f"DEBUG: Optimizing for {current_user.name} with {available_time}h")
        print(f"DEBUG: Subjects count: {len(subjects)}")

        # Convert MongoDB documents to list of dicts for DP
        subjects_list = []
        for s in subjects:
            subjects_list.append({
                'name': s['name'],
                'study_time': int(s['study_time']),
                'importance': int(s['importance'])
            })
            
        result = optimize_study_plan(subjects_list, available_time)
        print(f"DEBUG: Optimization Result Score: {result['total_score']}")
        
        return jsonify(result)
    except Exception as e:
        print(f"ERROR in /optimize: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
