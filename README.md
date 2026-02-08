# Guest Faculty Information System

A comprehensive web platform connecting colleges, faculty members, and students for teaching opportunities.

## 🎯 Features

### For Faculty Members
- Create professional profiles with qualifications, experience, and subjects
- List subjects you can teach
- Browse college hiring requirements
- Get discovered by colleges looking for educators
- Manage availability status

### For Colleges/Institutions
- Post faculty hiring requirements
- Search qualified faculty by subject, location, and experience
- Manage posted positions (Full-time, Part-time, Visiting, etc.)
- View and contact faculty candidates directly
- Track application status

### For Students
- Search faculty members by subject
- Post faculty requests for specific subjects
- Help institutions identify teaching needs
- Browse available faculty profiles

## 📁 Project Structure

```
guest-faculty/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── static/
│   └── style.css         # Premium CSS styling
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Homepage
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── faculty_*.html    # Faculty pages
│   ├── college_*.html    # College pages
│   ├── student_*.html    # Student pages
│   └── browse_*.html     # Public browse pages
└── guest_faculty.db      # SQLite database (auto-created)
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

### Step 3: Access the Application
Open your web browser and navigate to:
```
http://localhost:5000
```

## 👥 User Roles

### 1. Faculty Member
- Register with email and password
- Complete profile with qualifications, subjects, and experience
- Browse and apply for college requirements
- Manage availability status

### 2. College/Institution
- Register institutional account
- Post faculty requirements with details
- Search and filter faculty database
- Contact potential candidates

### 3. Student
- Register student account
- Search faculty by subject
- Post faculty requests
- Help connect educators with institutions

## 🎨 Design Features

- **Modern Dark Theme**: Premium dark mode with gradients
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Smooth Animations**: Micro-interactions and hover effects
- **Glassmorphism**: Modern UI with backdrop blur effects
- **Custom Color Palette**: Carefully selected HSL colors
- **Google Fonts**: Inter font family for clean typography

## 🔧 Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with password hashing
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript
- **Design**: Custom CSS with modern gradients and animations

## 📊 Database Models

### User
- Email, password (hashed), user type
- Relationships to profile tables

### FacultyProfile
- Personal information, qualifications
- Subjects, specialization, experience
- Availability status, bio, LinkedIn

### CollegeProfile
- Institution details, contact person
- Location, affiliation, website

### StudentProfile
- Personal information, college
- Course, semester, location

### Requirement
- Posted by colleges
- Subject, description, qualifications
- Employment type, salary range
- Status tracking

### StudentRequest
- Posted by students
- Subject, description, urgency
- Status tracking

## 🔐 Security Features

- Password hashing using Werkzeug
- Session-based authentication
- Role-based access control
- CSRF protection (built into Flask)
- Secure user data handling

## 🎯 Key Workflows

### Faculty Registration Flow
1. Register with email → Select "Faculty" role
2. Complete profile with subjects and qualifications
3. Browse requirements or wait to be discovered
4. Get contacted by colleges

### College Posting Flow
1. Register with email → Select "College" role
2. Complete institutional profile
3. Post faculty requirement with details
4. Search faculty database or receive applications

### Student Request Flow
1. Register with email → Select "Student" role
2. Complete student profile
3. Search faculty or post requirement
4. Help institution identify needs

## 📝 Future Enhancements

- [ ] Application/response system
- [ ] Email notifications
- [ ] Advanced filtering and sorting
- [ ] Faculty ratings and reviews
- [ ] Document upload (resume, certificates)
- [ ] Calendar integration for interviews
- [ ] Analytics dashboard
- [ ] Export reports (PDF/Excel)

## 🐛 Troubleshooting

### Database Issues
If you encounter database errors, delete `guest_faculty.db` and restart the application. The database will be recreated automatically.

### Port Already in Use
If port 5000 is busy, modify the last line in `app.py`:
```python
app.run(debug=True, port=5001)  # Change to any available port
```

### Missing Dependencies
Ensure all packages are installed:
```bash
pip install -r requirements.txt --upgrade
```

## 📄 License

This project is created for educational purposes.

## 👨‍💻 Support

For issues or questions, please check the code comments or review the Flask documentation at https://flask.palletsprojects.com/

---

**Built with ❤️ using Flask and modern web technologies**
