from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///guest_faculty.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'faculty', 'college', 'student'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    faculty_profile = db.relationship('FacultyProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    college_profile = db.relationship('CollegeProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')

class FacultyProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    qualification = db.Column(db.String(200))
    experience_years = db.Column(db.Integer)
    subjects = db.Column(db.Text)  # Comma-separated subjects
    specialization = db.Column(db.String(200))
    location = db.Column(db.String(100))
    availability = db.Column(db.String(50))  # 'Available', 'Not Available', 'Partially Available'
    bio = db.Column(db.Text)
    linkedin_url = db.Column(db.String(200))
    resume_url = db.Column(db.String(200))

class CollegeProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    college_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    affiliation = db.Column(db.String(200))
    website = db.Column(db.String(200))
    
    # Relationships
    requirements = db.relationship('Requirement', backref='college', cascade='all, delete-orphan')

class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    college_name = db.Column(db.String(200))
    course = db.Column(db.String(100))
    semester = db.Column(db.String(20))
    city = db.Column(db.String(100))
    
    # Relationships
    requests = db.relationship('StudentRequest', backref='student', cascade='all, delete-orphan')

class Requirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.Integer, db.ForeignKey('college_profile.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    qualification_required = db.Column(db.String(200))
    experience_required = db.Column(db.Integer)
    location = db.Column(db.String(100))
    salary_range = db.Column(db.String(100))
    employment_type = db.Column(db.String(50))  # 'Full-time', 'Part-time', 'Visiting'
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Open')  # 'Open', 'Closed', 'Filled'

class StudentRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profile.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    urgency = db.Column(db.String(20))  # 'High', 'Medium', 'Low'
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Open')

class ConnectionRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.Integer, db.ForeignKey('college_profile.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty_profile.id'), nullable=False)
    status = db.Column(db.String(20), default='Pending')  # 'Pending', 'Accepted', 'Rejected'
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    college = db.relationship('CollegeProfile', backref='sent_requests')
    faculty = db.relationship('FacultyProfile', backref='received_requests')

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

class OnlineClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.Integer, db.ForeignKey('college_profile.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty_profile.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    schedule_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    meeting_link = db.Column(db.String(200), nullable=False)
    secure_token = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), default='Scheduled')  # 'Scheduled', 'Completed', 'Cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    college = db.relationship('CollegeProfile', backref='scheduled_classes')
    faculty = db.relationship('FacultyProfile', backref='assigned_classes')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))
        
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            user_type=user_type
        )
        db.session.add(user)
        db.session.commit()
        
        # Create corresponding profile
        if user_type == 'faculty':
            profile = FacultyProfile(user_id=user.id, full_name='')
            db.session.add(profile)
        elif user_type == 'college':
            profile = CollegeProfile(user_id=user.id, college_name='')
            db.session.add(profile)
        elif user_type == 'student':
            profile = StudentProfile(user_id=user.id, full_name='')
            db.session.add(profile)
        
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        
        user = User.query.filter_by(email=email, user_type=user_type).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type == 'faculty':
        return redirect(url_for('faculty_dashboard'))
    elif current_user.user_type == 'college':
        return redirect(url_for('college_dashboard'))
    elif current_user.user_type == 'student':
        return redirect(url_for('student_dashboard'))
    else:
        # Fallback for invalid user types
        flash('Invalid user type. Please contact support.', 'error')
        logout_user()
        return redirect(url_for('index'))

# Faculty Routes
@app.route('/faculty/dashboard')
@login_required
def faculty_dashboard():
    if current_user.user_type != 'faculty':
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    profile = current_user.faculty_profile
    requirements = Requirement.query.filter_by(status='Open').order_by(Requirement.posted_at.desc()).all()
    return render_template('faculty_dashboard.html', profile=profile, requirements=requirements)

@app.route('/faculty/profile', methods=['GET', 'POST'])
@login_required
def faculty_profile():
    if current_user.user_type != 'faculty':
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    profile = current_user.faculty_profile
    
    if request.method == 'POST':
        profile.full_name = request.form.get('full_name')
        profile.phone = request.form.get('phone')
        profile.qualification = request.form.get('qualification')
        profile.experience_years = request.form.get('experience_years')
        profile.subjects = request.form.get('subjects')
        profile.specialization = request.form.get('specialization')
        profile.location = request.form.get('location')
        profile.availability = request.form.get('availability')
        profile.bio = request.form.get('bio')
        profile.linkedin_url = request.form.get('linkedin_url')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('faculty_dashboard'))
    
    return render_template('faculty_profile.html', profile=profile)

# College Routes
@app.route('/college/dashboard')
@login_required
def college_dashboard():
    if current_user.user_type != 'college':
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    profile = current_user.college_profile
    requirements = Requirement.query.filter_by(college_id=profile.id).order_by(Requirement.posted_at.desc()).all()
    return render_template('college_dashboard.html', profile=profile, requirements=requirements)

@app.route('/college/profile', methods=['GET', 'POST'])
@login_required
def college_profile():
    if current_user.user_type != 'college':
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    profile = current_user.college_profile
    
    if request.method == 'POST':
        profile.college_name = request.form.get('college_name')
        profile.contact_person = request.form.get('contact_person')
        profile.phone = request.form.get('phone')
        profile.address = request.form.get('address')
        profile.city = request.form.get('city')
        profile.state = request.form.get('state')
        profile.affiliation = request.form.get('affiliation')
        profile.website = request.form.get('website')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('college_dashboard'))
    
    return render_template('college_profile.html', profile=profile)

@app.route('/college/search-faculty')
@login_required
def search_faculty():
    if current_user.user_type != 'college':
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    subject = request.args.get('subject', '')
    location = request.args.get('location', '')
    qualification = request.args.get('qualification', '')
    
    query = FacultyProfile.query.filter(FacultyProfile.full_name != '')
    
    if subject:
        query = query.filter(FacultyProfile.subjects.contains(subject))
    if location:
        query = query.filter(FacultyProfile.location.contains(location))
    if qualification:
        query = query.filter(FacultyProfile.qualification.contains(qualification))
    
    faculties = query.all()
    return render_template('search_faculty.html', faculties=faculties)

@app.route('/college/view-faculty/<int:faculty_id>')
@login_required
def college_view_faculty(faculty_id):
    if current_user.user_type != 'college':
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    faculty = FacultyProfile.query.get_or_404(faculty_id)
    return render_template('college_view_faculty.html', faculty=faculty)

@app.route('/college/post-requirement', methods=['GET', 'POST'])
@login_required
def post_requirement():
    if current_user.user_type != 'college':
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        requirement = Requirement(
            college_id=current_user.college_profile.id,
            subject=request.form.get('subject'),
            description=request.form.get('description'),
            qualification_required=request.form.get('qualification_required'),
            experience_required=request.form.get('experience_required'),
            location=request.form.get('location'),
            salary_range=request.form.get('salary_range'),
            employment_type=request.form.get('employment_type')
        )
        db.session.add(requirement)
        db.session.commit()
        flash('Requirement posted successfully!', 'success')
        return redirect(url_for('college_dashboard'))
    
    return render_template('post_requirement.html')

# Student Routes
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.user_type != 'student':
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    profile = current_user.student_profile
    requests = StudentRequest.query.filter_by(student_id=profile.id).order_by(StudentRequest.posted_at.desc()).all()
    return render_template('student_dashboard.html', profile=profile, requests=requests)

@app.route('/student/profile', methods=['GET', 'POST'])
@login_required
def student_profile():
    if current_user.user_type != 'student':
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    profile = current_user.student_profile
    
    if request.method == 'POST':
        profile.full_name = request.form.get('full_name')
        profile.phone = request.form.get('phone')
        profile.college_name = request.form.get('college_name')
        profile.course = request.form.get('course')
        profile.semester = request.form.get('semester')
        profile.city = request.form.get('city')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student_dashboard'))
    
    return render_template('student_profile.html', profile=profile)

@app.route('/student/search-faculty')
@login_required
def student_search_faculty():
    if current_user.user_type != 'student':
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    subject = request.args.get('subject', '')
    location = request.args.get('location', '')
    
    query = FacultyProfile.query.filter(FacultyProfile.full_name != '')
    
    if subject:
        query = query.filter(FacultyProfile.subjects.contains(subject))
    if location:
        query = query.filter(FacultyProfile.location.contains(location))
    
    faculties = query.all()
    return render_template('student_search_faculty.html', faculties=faculties)

@app.route('/student/post-request', methods=['GET', 'POST'])
@login_required
def post_student_request():
    if current_user.user_type != 'student':
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        student_request = StudentRequest(
            student_id=current_user.student_profile.id,
            subject=request.form.get('subject'),
            description=request.form.get('description'),
            urgency=request.form.get('urgency')
        )
        db.session.add(student_request)
        db.session.commit()
        flash('Request posted successfully!', 'success')
        return redirect(url_for('student_dashboard'))
    
    return render_template('post_student_request.html')

# Browse all requirements
@app.route('/requirements')
def browse_requirements():
    requirements = Requirement.query.filter_by(status='Open').order_by(Requirement.posted_at.desc()).all()
    return render_template('browse_requirements.html', requirements=requirements)

# Connection and Chat Routes
@app.route('/college/send-request/<int:faculty_id>', methods=['POST'])
@login_required
def send_connection_request(faculty_id):
    if current_user.user_type != 'college':
        flash('Only colleges can send requests!', 'error')
        return redirect(url_for('dashboard'))
    
    college_profile = current_user.college_profile
    
    # Check if a request already exists
    existing_request = ConnectionRequest.query.filter_by(
        college_id=college_profile.id,
        faculty_id=faculty_id
    ).first()
    
    if existing_request:
        flash('Request already sent!', 'info')
    else:
        new_request = ConnectionRequest(
            college_id=college_profile.id,
            faculty_id=faculty_id,
            message=request.form.get('message', 'I am interested in your profile.')
        )
        db.session.add(new_request)
        db.session.commit()
        flash('Request sent successfully!', 'success')
    
    return redirect(url_for('search_faculty'))

@app.route('/faculty/requests')
@login_required
def view_faculty_requests():
    if current_user.user_type != 'faculty':
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    profile = current_user.faculty_profile
    requests = ConnectionRequest.query.filter_by(faculty_id=profile.id).order_by(ConnectionRequest.created_at.desc()).all()
    return render_template('faculty_requests.html', requests=requests)

@app.route('/faculty/respond-request/<int:request_id>/<string:action>')
@login_required
def respond_request(request_id, action):
    if current_user.user_type != 'faculty':
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    req = ConnectionRequest.query.get_or_404(request_id)
    if req.faculty_id != current_user.faculty_profile.id:
        flash('Unauthorized!', 'error')
        return redirect(url_for('dashboard'))
    
    if action == 'accept':
        req.status = 'Accepted'
        flash('Request accepted! You can now chat.', 'success')
    elif action == 'reject':
        req.status = 'Rejected'
        flash('Request rejected.', 'info')
    
    db.session.commit()
    return redirect(url_for('view_faculty_requests'))

@app.route('/chat/<int:other_user_id>', methods=['GET', 'POST'])
@login_required
def chat(other_user_id):
    other_user = User.query.get_or_404(other_user_id)
    
    # Check if communication is allowed
    # Allowed if a request has been accepted between the two parties (or if profile is complete - though accepted request is safer)
    allowed = False
    if current_user.user_type == 'college' and other_user.user_type == 'faculty':
        req = ConnectionRequest.query.filter_by(
            college_id=current_user.college_profile.id,
            faculty_id=other_user.faculty_profile.id,
            status='Accepted'
        ).first()
        if req:
            allowed = True
    elif current_user.user_type == 'faculty' and other_user.user_type == 'college':
        req = ConnectionRequest.query.filter_by(
            college_id=other_user.college_profile.id,
            faculty_id=current_user.faculty_profile.id,
            status='Accepted'
        ).first()
        if req:
            allowed = True
            
    if not allowed:
        flash('Chat is only available after a connection request is accepted.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            msg = ChatMessage(sender_id=current_user.id, receiver_id=other_user_id, content=content)
            db.session.add(msg)
            db.session.commit()
            return redirect(url_for('chat', other_user_id=other_user_id))

    messages = ChatMessage.query.filter(
        ((ChatMessage.sender_id == current_user.id) & (ChatMessage.receiver_id == other_user_id)) |
        ((ChatMessage.sender_id == other_user_id) & (ChatMessage.receiver_id == current_user.id))
    ).order_by(ChatMessage.timestamp.asc()).all()
    
    return render_template('chat.html', other_user=other_user, messages=messages)

@app.route('/messages')
@login_required
def view_all_chats():
    # Show list of people user has accepted connections with
    connections = []
    if current_user.user_type == 'college':
        reqs = ConnectionRequest.query.filter_by(college_id=current_user.college_profile.id, status='Accepted').all()
        for r in reqs:
            connections.append(r.faculty.user)
    elif current_user.user_type == 'faculty':
        reqs = ConnectionRequest.query.filter_by(faculty_id=current_user.faculty_profile.id, status='Accepted').all()
        for r in reqs:
            connections.append(r.college.user)
            
    return render_template('messages_list.html', connections=connections)

# Online Class Routes
@app.route('/college/schedule-class/<int:faculty_id>', methods=['GET', 'POST'])
@login_required
def schedule_class(faculty_id):
    if current_user.user_type != 'college':
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    faculty = FacultyProfile.query.get_or_404(faculty_id)
    
    # Check if a connection exists
    connection = ConnectionRequest.query.filter_by(
        college_id=current_user.college_profile.id,
        faculty_id=faculty_id,
        status='Accepted'
    ).first()
    
    if not connection:
        flash('You must have an accepted connection to schedule a class.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        subject = request.form.get('subject')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        duration = int(request.form.get('duration', 60))
        
        # Browser time inputs can vary; handle HH:MM and HH:MM:SS
        time_clean = time_str[:5] if len(time_str) >= 5 else time_str
        try:
            schedule_time = datetime.strptime(f"{date_str} {time_clean}", "%Y-%m-%d %H:%M")
        except ValueError:
            # Fallback if somehow date format is different
            flash('Invalid date or time format. Please try again.', 'error')
            return redirect(url_for('view_all_chats'))
        
        token = str(uuid.uuid4())
        # Demo link - in real app would be Zoom/Jitsi/etc.
        meeting_link = url_for('join_class', token=token, _external=True)
        
        new_class = OnlineClass(
            college_id=current_user.college_profile.id,
            faculty_id=faculty_id,
            subject=subject,
            schedule_time=schedule_time,
            duration_minutes=duration,
            meeting_link=meeting_link,
            secure_token=token
        )
        db.session.add(new_class)
        db.session.commit()
        
        flash('Online class scheduled successfully!', 'success')
        return redirect(url_for('view_classes'))
        
    return render_template('schedule_class.html', faculty=faculty)

@app.route('/classes')
@login_required
def view_classes():
    if current_user.user_type == 'college':
        classes = OnlineClass.query.filter_by(college_id=current_user.college_profile.id).order_by(OnlineClass.schedule_time.asc()).all()
    elif current_user.user_type == 'faculty':
        classes = OnlineClass.query.filter_by(faculty_id=current_user.faculty_profile.id).order_by(OnlineClass.schedule_time.asc()).all()
    else:
        classes = OnlineClass.query.filter(OnlineClass.status == 'Scheduled').all()
        
    return render_template('view_classes.html', classes=classes, now=datetime.now())

@app.route('/join-class/<string:token>')
@login_required
def join_class(token):
    online_class = OnlineClass.query.filter_by(secure_token=token).first_or_404()
    
    # Check if class is active - using local time to match form input
    now = datetime.now()
    # Class starts 10 mins before and ends 1 hour after duration
    start_time = online_class.schedule_time - timedelta(minutes=10)
    end_time = online_class.schedule_time + timedelta(minutes=online_class.duration_minutes)
    
    if now < start_time:
        flash('Class has not started yet.', 'info')
        return redirect(url_for('view_classes'))
    
    if now > end_time:
        online_class.status = 'Completed'
        db.session.commit()
        flash('This class link has expired.', 'error')
        return redirect(url_for('view_classes'))
        
    # Authorization check
    authorized = False
    if current_user.user_type == 'college' and current_user.college_profile.id == online_class.college_id:
        authorized = True
    elif current_user.user_type == 'faculty' and current_user.faculty_profile.id == online_class.faculty_id:
        authorized = True
    elif current_user.user_type == 'student':
        # More robust check: trim and case-insensitive
        user_college = (current_user.student_profile.college_name or "").strip().lower()
        class_college = (online_class.college.college_name or "").strip().lower()
        if user_college == class_college or not user_college:
            # If student hasn't specified college yet, allow for demo/simplicity
            # but ideally they should have it.
            authorized = True
            
    if not authorized:
        flash('You are not authorized to join this class.', 'error')
        return redirect(url_for('dashboard'))
        
    return render_template('class_room.html', online_class=online_class)

# Browse all student requests
@app.route('/student-requests')
def browse_student_requests():
    requests = StudentRequest.query.filter_by(status='Open').order_by(StudentRequest.posted_at.desc()).all()
    return render_template('browse_student_requests.html', requests=requests)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
