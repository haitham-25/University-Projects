# 🎓 College Exam System

A JavaFX-based desktop application for managing college examinations, providing role-based access for Admins, Lecturers, and Students.

## 📋 Overview

The College Exam System is a comprehensive examination management platform that enables educational institutions to digitize their exam processes. The system features a modern, gradient-styled user interface and supports complete exam lifecycle management from creation to evaluation.

## ✨ Features

### 👨‍💼 Admin Features
- **User Management**
  - Add and manage students
  - Add and manage lecturers
  - Add new administrators
  - Update user information
  - Delete users from the system

- **Subject Management**
  - Create and manage subjects
  - Assign subjects to students
  - Assign subjects to lecturers

- **System Oversight**
  - View all registered users
  - Monitor all subjects
  - Access all exam data
  - View student scores across all subjects

### 👨‍🏫 Lecturer Features
- **Exam Management**
  - Create exams for assigned subjects
  - Add multiple-choice or text-based questions
  - Set exam duration
  - Define correct answers

- **Score Review**
  - View scores of all students
  - Filter scores by subject
  - Monitor student performance

- **Profile Management**
  - Update personal information
  - Change login credentials

### 👨‍🎓 Student Features
- **Exam Taking**
  - Take exams for assigned subjects
  - Navigate through questions with Next button
  - Submit answers
  - Instant score feedback

- **Score Tracking**
  - View personal exam scores
  - Track performance across subjects

- **Profile Management**
  - Update personal information
  - Change login credentials

## 🛠️ Technical Stack

- **Language**: Java
- **GUI Framework**: JavaFX
- **Data Persistence**: File-based storage (CSV format)
- **Architecture**: Object-Oriented Programming with inheritance

## 📦 Installation

### Prerequisites
- Java Development Kit (JDK) 11 or higher
- JavaFX SDK (if not included in your JDK)

### Setup Steps

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd college-exam-system
   ```

2. **Ensure JavaFX is configured**
   - If using JDK 11+, download JavaFX SDK separately
   - Set up the JavaFX library path in your IDE or build configuration

3. **Compile the application**
   ```bash
   javac --module-path /path/to/javafx-sdk/lib --add-modules javafx.controls CollegeExamSystem.java
   ```

4. **Run the application**
   ```bash
   java --module-path /path/to/javafx-sdk/lib --add-modules javafx.controls CollegeExamSystem
   ```

## 🚀 Usage

### First Time Login

The system comes with a default admin account:
- **Username**: `admin`
- **Password**: `admin123`

### User Workflow

1. **Login Screen**
   - Select user type (Admin/Lecturer/Student)
   - Enter username and password
   - Click Login

2. **Admin Workflow**
   - Add subjects first
   - Create student and lecturer accounts
   - Assign subjects to students and lecturers

3. **Lecturer Workflow**
   - Create exams for assigned subjects
   - Add questions and answers
   - Review student scores

4. **Student Workflow**
   - Take available exams
   - View scores after completion

## 💾 Data Storage

The application uses text files for data persistence:

- `students.txt` - Student records (ID, Name, Username, Password)
- `lecturers.txt` - Lecturer records (ID, Name, Username, Password)
- `admin.txt` - Admin records (ID, Name, Username, Password)
- `subjects.txt` - Subject information (ID, Name)
- `exams.txt` - Exam data (Subject ID, Lecturer ID, Duration, Questions, Answers)
- `scores.txt` - Student scores (Student ID, Subject ID, Score)

**Note**: Data is automatically saved when the application closes and loaded when it starts.

## 🏗️ System Architecture

### Class Structure

```
User (Abstract)
├── Admin
├── Lecturer
└── Student

Other Classes:
├── Subject
├── Exam
└── CollegeExamSystem (Main Application)
```

### Key Components

- **User Hierarchy**: Abstract base class with concrete implementations for different user roles
- **Subject Management**: Tracks academic subjects
- **Exam Engine**: Handles exam creation and evaluation
- **Score Tracking**: Maps students to their exam results
- **File I/O**: Persistent storage using CSV-style text files

## 🎨 UI Design

The application features a modern, user-friendly interface with:
- Gradient blue backgrounds
- Rounded buttons with hover effects
- Clean, organized layouts
- Intuitive navigation
- Color-coded user feedback

## 🔒 Security Notes

- Passwords are stored in plain text (for educational purposes)
- For production use, implement:
  - Password hashing (BCrypt, Argon2)
  - Secure session management
  - Input validation and sanitization
  - Role-based access control enforcement

## 🐛 Known Limitations

- No database integration (file-based storage only)
- Plain text password storage
- Limited to 3 questions per exam
- No exam time enforcement during exam taking
- Basic error handling
- Single-session concurrent use (file locking not implemented)

## 🔮 Future Enhancements

- Database integration (MySQL, PostgreSQL)
- Enhanced security with password encryption
- Configurable number of questions per exam
- Timer implementation during exams
- Report generation (PDF export)
- Email notifications
- Advanced analytics and statistics
- Multi-language support
- Responsive design for different screen sizes

## 📄 File Format Examples

### students.txt
```
S001,John Doe,john.doe,password123
S002,Jane Smith,jane.smith,pass456
```

### exams.txt
```
SUBJ001|LEC001|60|Question1;Question2;Question3|Answer1;Answer2;Answer3
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is available for educational purposes. Please check the license file for more details.

## 👥 Authors

- Initial development for academic/learning purposes

## 📧 Support

For questions or issues, please open an issue in the repository.

---

**Note**: This is an educational project. For production deployment, implement proper security measures, database integration, and comprehensive error handling.
