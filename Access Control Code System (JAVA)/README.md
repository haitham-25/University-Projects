College Exam System
Overview
The College Exam System is a JavaFX-based application designed to manage examinations within a college environment. It provides a user-friendly interface for three types of users: Admins, Lecturers, and Students. The system allows for user management, subject assignment, exam creation, and score tracking, with data persistence using file storage.
Features
Admin Features

Add, update, and delete students, lecturers, and admins.
Assign subjects to students and lecturers.
Search users by username.
List all students and lecturers.

Lecturer Features

Create, update, and delete exams for assigned subjects.
View assigned subjects.
List all exams created by the lecturer.

Student Features

Take exams for assigned subjects.
View exam scores.

Prerequisites

Java Development Kit (JDK) 8 or higher
JavaFX SDK (included in JDK 8; for later versions, ensure JavaFX is configured)
An IDE like IntelliJ IDEA, Eclipse, or NetBeans (optional, for easier development)

Installation

Clone or download the project repository.
Ensure JDK is installed and configured in your environment.
If using JDK 11 or higher, download and configure the JavaFX SDK:
Add JavaFX libraries to your project.
Configure VM options (e.g., --module-path /path/to/javafx-sdk/lib --add-modules javafx.controls,javafx.fxml).


Compile and run the CollegeExamSystem.java file.

Usage

Launch the Application:

Run the main method in CollegeExamSystem.java.
The application starts with a login screen.


Login:

Select user type (Admin, Lecturer, or Student).
Enter username and password.
Default admin credentials: username: admin, password: admin123.


Navigation:

Admins: Access a dashboard to manage users, subjects, and assignments.
Lecturers: Create and manage exams, view assigned subjects.
Students: Take exams and view scores.


Data Persistence:

Data (users, subjects, exams, scores) is saved to text files (students.txt, lecturers.txt, admin.txt, subjects.txt, exams.txt, scores.txt) on application exit.
Files are loaded automatically on startup if they exist.



File Structure

CollegeExamSystem.java: Main application class with JavaFX UI and logic.
Data files:
students.txt: Stores student information (ID, name, username, password).
lecturers.txt: Stores lecturer information.
admin.txt: Stores admin information.
subjects.txt: Stores subject information (ID, name).
exams.txt: Stores exam details (subject ID, lecturer ID, duration, questions, answers).
scores.txt: Stores student scores (student ID, subject ID, score).



Code Structure

Classes:
User: Abstract base class for Admin, Lecturer, and Student.
Admin: Manages system-wide operations.
Lecturer: Manages exams and assigned subjects.
Student: Takes exams and views scores.
Subject: Represents a subject with an ID and name.
Exam: Represents an exam with questions, answers, and evaluation logic.


UI:
Built using JavaFX with a gradient-themed interface.
Features responsive layouts with VBox, GridPane, and StackPane.


Data Management:
Uses ArrayList for in-memory storage of users, subjects, and exams.
Uses HashMap for storing student scores.
File I/O with BufferedReader and PrintWriter for persistence.



Limitations

Exams are limited to three questions each.
No advanced validation (e.g., duplicate IDs or usernames).
Basic error handling for file I/O and input validation.
No encryption for stored passwords (stored in plain text).

Future Improvements

Add input validation for unique IDs and usernames.
Implement password encryption for security.
Support multiple-choice or other question types.
Add a database (e.g., SQLite) for better data management.
Enhance UI with more interactive elements or themes.

Troubleshooting

JavaFX not found: Ensure JavaFX is included and VM options are set correctly.
File I/O errors: Check file permissions in the project directory.
Login issues: Verify credentials or check data files for corruption.

License
This project is for educational purposes and is not licensed for commercial use.
