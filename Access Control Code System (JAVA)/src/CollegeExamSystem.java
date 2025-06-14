import javafx.application.Application;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.GridPane;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;//gui
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.File;//file handling
import java.util.*;//handling arrays and lists

abstract class User {
    protected String id, name, username, password;

    public User(String id, String name, String username, String password) {
        this.id = id;
        this.name = name;
        this.username = username;
        this.password = password;
    }

    public boolean login(String username, String password) {
        return this.username.equals(username) && this.password.equals(password);
    }

    public void updateInfo(String name, String username, String password) {
        this.name = name;
        this.username = username;
        this.password = password;
    }

    public String getId() {
        return id;
    }
}

class Admin extends User {
    public Admin(String id, String name, String username, String password) {
        super(id, name, username, password);
    }
}

class Lecturer extends User {
    List<Subject> assignedSubjects = new ArrayList<>();

    public Lecturer(String id, String name, String username, String password) {
        super(id, name, username, password);
    }

    public void assignSubject(Subject subject) {
        assignedSubjects.add(subject);
    }
}

class Student extends User {
    List<Subject> assignedSubjects = new ArrayList<>();

    public Student(String id, String name, String username, String password) {
        super(id, name, username, password);
    }

    public void assignSubject(Subject subject) {
        assignedSubjects.add(subject);
    }
}

class Subject {
    String id, name;

    public Subject(String id, String name) {
        this.id = id;
        this.name = name;
    }
}

class Exam {
    String subjectId, lecturerId;
    int duration;
    List<String> questions = new ArrayList<>();
    List<String> correctAnswers = new ArrayList<>();

    public Exam(String subjectId, String lecturerId, int duration) {
        this.subjectId = subjectId;
        this.lecturerId = lecturerId;
        this.duration = duration;
    }

    public int evaluate(List<String> answers) {
        int score = 0;
        for (int i = 0; i < correctAnswers.size(); i++) {
            if (i < answers.size() && correctAnswers.get(i).equalsIgnoreCase(answers.get(i))) {
                score++;
            }
        }
        return score;
    }
}

public class CollegeExamSystem extends Application {
    static List<Admin> admins = new ArrayList<>(List.of(new Admin("A1", "Admin", "admin", "admin123")));
    static List<Student> students = new ArrayList<>();
    static List<Lecturer> lecturers = new ArrayList<>();
    static List<Subject> subjects = new ArrayList<>();
    static List<Exam> exams = new ArrayList<>();
    static Map<String, Map<String, Integer>> scores = new HashMap<>();

    private Stage primaryStage;


    public void start(Stage primaryStage) {
        this.primaryStage = primaryStage;
        primaryStage.setTitle("College Exam System");
        showLoginScreen();
    }

    private void showLoginScreen() {
        VBox layout = new VBox(15);
        layout.setPadding(new Insets(40));
        layout.setAlignment(Pos.CENTER);
        layout.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #0000);");

        Label title = new Label("🎓 College Exam System");
        title.setStyle("-fx-font-size: 28px; -fx-text-fill: white; -fx-font-weight: bold;");

        ComboBox<String> userType = new ComboBox<>();
        userType.getItems().addAll("Admin", "Lecturer", "Student");
        userType.setPromptText("Select User Type");
        userType.setMaxWidth(250);
        userType.setStyle("-fx-background-radius: 10; -fx-padding: 10;");

        TextField usernameField = new TextField();
        usernameField.setPromptText("Username");
        usernameField.setMaxWidth(250);
        usernameField.setStyle("-fx-background-radius: 10; -fx-padding: 10;");

        PasswordField passwordField = new PasswordField();
        passwordField.setPromptText("Password");
        passwordField.setMaxWidth(250);
        passwordField.setStyle("-fx-background-radius: 10; -fx-padding: 10;");

        Button loginButton = new Button("Login");
        loginButton.setMaxWidth(250);
        loginButton.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-weight: bold; -fx-background-radius: 20; -fx-padding: 10 20;");

        Label messageLabel = new Label();
        messageLabel.setStyle("-fx-text-fill: red; -fx-font-weight: bold;");

        loginButton.setOnAction(e -> {
            String type = userType.getValue();
            String username = usernameField.getText();
            String password = passwordField.getText();

            if (type == null || username.isEmpty() || password.isEmpty()) {
                messageLabel.setText("Please fill all fields.");
                return;
            }
            switch (type) {
                case "Admin":
                    Admin admin = admins.stream().filter(a -> a.login(username, password)).findFirst().orElse(null);
                    if (admin != null) {
                        showAdminMenu(admin);
                    } else {
                        messageLabel.setText("Login failed.");
                    }
                    break;
                case "Lecturer":
                    Lecturer lecturer = lecturers.stream().filter(l -> l.login(username, password)).findFirst().orElse(null);
                    if (lecturer != null) {
                        showLecturerMenu(lecturer);
                    } else {
                        messageLabel.setText("Login failed.");
                    }
                    break;
                case "Student":
                    Student student = students.stream().filter(s -> s.login(username, password)).findFirst().orElse(null);
                    if (student != null) {
                        showStudentMenu(student);
                    } else {
                        messageLabel.setText("Login failed.");
                    }
                    break;
            }
        });

        layout.getChildren().addAll(title, userType, usernameField, passwordField, loginButton, messageLabel);
        Scene scene = new Scene(layout, 450, 400);
        primaryStage.setTitle("Login | College Exam System");
        primaryStage.setScene(scene);
        primaryStage.show();

    }

    private void showAdminMenu(Admin admin) {
        VBox rootLayout = new VBox(20);
        rootLayout.setPadding(new Insets(30));
        rootLayout.setAlignment(Pos.TOP_CENTER);

        Label title = new Label("🔧 Admin Dashboard");
        title.setStyle("-fx-font-size: 26px; -fx-text-fill: white; -fx-font-weight: bold;");

        String buttonStyle = "-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; " +
                "-fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;";

        Button[] buttons = new Button[] {
                new Button("Add Student"),
                new Button("Add Lecturer"),
                new Button("Add New Admin"),
                new Button("Add Subject"),
                new Button("Search User by Username"),
                new Button("Assign Subject to Lecturer"),
                new Button("Assign Subject to Student"),
                new Button("Delete Student"),
                new Button("Delete Lecturer"),
                new Button("Update Student Info"),
                new Button("Update Lecturer Info"),
                new Button("List Students"),
                new Button("List Lecturers"),
                new Button("Logout")
        };

        for (Button btn : buttons) {
            btn.setStyle(buttonStyle);
            btn.setPrefWidth(250);
        }

        buttons[0].setOnAction(e -> showAddStudentScreen());
        buttons[1].setOnAction(e -> showAddLecturerScreen());
        buttons[2].setOnAction(e -> showAddAdminScreen());
        buttons[3].setOnAction(e -> showAddSubjectScreen());
        buttons[4].setOnAction(e -> showSearchUserScreen());
        buttons[5].setOnAction(e -> showAssignSubjectToLecturerScreen());
        buttons[6].setOnAction(e -> showAssignSubjectToStudentScreen());
        buttons[7].setOnAction(e -> showDeleteStudentScreen());
        buttons[8].setOnAction(e -> showDeleteLecturerScreen());
        buttons[9].setOnAction(e -> showUpdateStudentScreen());
        buttons[10].setOnAction(e -> showUpdateLecturerScreen());
        buttons[11].setOnAction(e -> showListStudentsScreen());
        buttons[12].setOnAction(e -> showListLecturersScreen());
        buttons[13].setOnAction(e -> showLoginScreen());

        GridPane grid = new GridPane();
        grid.setHgap(20);
        grid.setVgap(20);
        grid.setAlignment(Pos.CENTER);

        for (int i = 0; i < buttons.length; i++) {
            grid.add(buttons[i], i % 2, i / 2);
        }

        rootLayout.getChildren().addAll(title, grid);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #00f2fe);");
        background.getChildren().add(rootLayout);

        Scene scene = new Scene(background, 600, 650);
        primaryStage.setScene(scene);
        primaryStage.setTitle("Admin Menu");
    }private void showAddStudentScreen() {
        VBox layout = new VBox(20);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);
        layout.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #00f2fe);");

        Label title = new Label("➕ Add New Student");
        title.setStyle("-fx-font-size: 22px; -fx-text-fill: white; -fx-font-weight: bold;");

        TextField idField = new TextField();
        idField.setPromptText("Student ID");
        idField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 5px;");

        TextField nameField = new TextField();
        nameField.setPromptText("Name");
        nameField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 5px;");

        TextField usernameField = new TextField();
        usernameField.setPromptText("Username");
        usernameField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 5px;");

        PasswordField passwordField = new PasswordField();
        passwordField.setPromptText("Password");
        passwordField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 5px;");

        Button submit = new Button("Add Student");
        Button back = new Button("Back");
        Label message = new Label();
        message.setStyle("-fx-text-fill: yellow; -fx-font-weight: bold;");

        String buttonStyle = "-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; " +
                "-fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;";
        submit.setStyle(buttonStyle);
        back.setStyle(buttonStyle);
        submit.setPrefWidth(200);
        back.setPrefWidth(200);

        submit.setOnAction(e -> {
            String id = idField.getText().trim();
            String name = nameField.getText().trim();
            String username = usernameField.getText().trim();
            String password = passwordField.getText();

            if (id.isEmpty() || name.isEmpty() || username.isEmpty() || password.isEmpty()) {
                message.setText("All fields are required.");
                return;
            }

            students.add(new Student(id, name, username, password));
            message.setText("Student added successfully.");

            idField.clear();
            nameField.clear();
            usernameField.clear();
            passwordField.clear();
        });

        back.setOnAction(e -> showAdminMenu(null));

        layout.getChildren().addAll(title, idField, nameField, usernameField, passwordField, submit, back, message);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #00f2fe);");
        background.getChildren().add(layout);

        Scene scene = new Scene(background, 450, 500);
        primaryStage.setScene(scene);
        primaryStage.setTitle("Add Student");
    }
    private void showAddLecturerScreen() {
        VBox layout = new VBox(20);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        // Title
        Label title = new Label("👨‍🏫 Add Lecturer");
        title.setStyle("-fx-font-size: 22px; -fx-text-fill: white; -fx-font-weight: bold;");

        // Input fields
        TextField idField = new TextField();
        idField.setPromptText("Lecturer ID");
        idField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #43cea2; -fx-font-size: 14px; -fx-background-radius: 5px;");

        TextField nameField = new TextField();
        nameField.setPromptText("Name");
        nameField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #43cea2; -fx-font-size: 14px; -fx-background-radius: 5px;");

        TextField usernameField = new TextField();
        usernameField.setPromptText("Username");
        usernameField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #43cea2; -fx-font-size: 14px; -fx-background-radius: 5px;");

        PasswordField passwordField = new PasswordField();
        passwordField.setPromptText("Password");
        passwordField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #43cea2; -fx-font-size: 14px; -fx-background-radius: 5px;");

        Label message = new Label();
        message.setStyle("-fx-text-fill: yellow; -fx-font-weight: bold;");

        Button submit = new Button("Add Lecturer");
        Button back = new Button("Back");

        String buttonStyle = "-fx-background-color: #ffffff; -fx-text-fill: #43cea2; -fx-font-size: 14px; -fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;";
        submit.setStyle(buttonStyle);
        back.setStyle(buttonStyle);
        submit.setPrefWidth(200);
        back.setPrefWidth(200);


        submit.setOnAction(e -> {
            String id = idField.getText().trim();
            String name = nameField.getText().trim();
            String username = usernameField.getText().trim();
            String password = passwordField.getText();

            if (id.isEmpty() || name.isEmpty() || username.isEmpty() || password.isEmpty()) {
                message.setText("All fields are required.");
                return;
            }

            lecturers.add(new Lecturer(id, name, username, password));
            message.setText("Lecturer added successfully.");


            idField.clear();
            nameField.clear();
            usernameField.clear();
            passwordField.clear();
        });

        back.setOnAction(e -> showAdminMenu(null));

        layout.getChildren().addAll(title, idField, nameField, usernameField, passwordField, submit, back, message);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #43cea2, #185a9d);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 500));
        primaryStage.setTitle("Add Lecturer");
    }

    private void showAddAdminScreen() {
        VBox layout = new VBox(15);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        Label title = new Label("👨‍💼 Add Admin");
        title.setStyle("-fx-font-size: 22px; -fx-text-fill: white; -fx-font-weight: bold;");

        TextField idField = new TextField();
        idField.setPromptText("Admin ID");
        idField.setStyle("-fx-font-size: 14px; -fx-padding: 10px;");

        TextField nameField = new TextField();
        nameField.setPromptText("Name");
        nameField.setStyle("-fx-font-size: 14px; -fx-padding: 10px;");

        TextField usernameField = new TextField();
        usernameField.setPromptText("Username");
        usernameField.setStyle("-fx-font-size: 14px; -fx-padding: 10px;");

        PasswordField passwordField = new PasswordField();
        passwordField.setPromptText("Password");
        passwordField.setStyle("-fx-font-size: 14px; -fx-padding: 10px;");

        Label message = new Label();
        message.setStyle("-fx-text-fill: yellow; -fx-font-weight: bold;");

        Button submit = new Button("Add Admin");
        Button back = new Button("Back");

        String buttonStyle = "-fx-background-color: #ffffff; -fx-text-fill: #43cea2; -fx-font-size: 14px; " +
                "-fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;";
        submit.setStyle(buttonStyle);
        back.setStyle(buttonStyle);
        submit.setPrefWidth(200);
        back.setPrefWidth(200);

        // Submit action to add admin
        submit.setOnAction(e -> {
            String id = idField.getText();
            String name = nameField.getText();
            String username = usernameField.getText();
            String password = passwordField.getText();

            if (id.isEmpty() || name.isEmpty() || username.isEmpty() || password.isEmpty()) {
                message.setText("All fields are required.");
                return;
            }

            admins.add(new Admin(id, name, username, password));
            message.setText("Admin added successfully.");

            idField.clear();
            nameField.clear();
            usernameField.clear();
            passwordField.clear();
        });

        back.setOnAction(e -> showAdminMenu(null));

        layout.getChildren().addAll(title, idField, nameField, usernameField, passwordField, submit, back, message);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #43cea2, #185a9d);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 450));
        primaryStage.setTitle("Add Admin");
    }

    private void showAddSubjectScreen() {
        VBox content = new VBox(20);
        content.setPadding(new Insets(30));
        content.setAlignment(Pos.CENTER);

        Label title = new Label("➕ Add Subject");
        title.setStyle("-fx-font-size: 22px; -fx-text-fill: white; -fx-font-weight: bold;");

        TextField idField = new TextField();
        idField.setPromptText("Subject ID");
        idField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 5px;");

        TextField nameField = new TextField();
        nameField.setPromptText("Subject Name");
        nameField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 5px;");

        Label message = new Label();
        message.setStyle("-fx-text-fill: yellow; -fx-font-weight: bold;");

        Button submit = new Button("Add Subject");
        Button back = new Button("Back");

        String buttonStyle = "-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;";
        submit.setStyle(buttonStyle);
        back.setStyle(buttonStyle);
        submit.setPrefWidth(200);
        back.setPrefWidth(200);

        submit.setOnAction(e -> {
            String id = idField.getText().trim();
            String name = nameField.getText().trim();

            if (id.isEmpty() || name.isEmpty()) {
                message.setText("All fields are required.");
                return;
            }

            subjects.add(new Subject(id, name));
            message.setText("Subject added successfully.");

            idField.clear();
            nameField.clear();
        });

        back.setOnAction(e -> showAdminMenu(null));

        content.getChildren().addAll(title, idField, nameField, submit, back, message);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #00f2fe);");
        background.getChildren().add(content);

        primaryStage.setScene(new Scene(background, 450, 400));
        primaryStage.setTitle("Add Subject");
    }
    private void showAssignSubjectToLecturerScreen() {
        VBox layout = new VBox(20);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        Label title = new Label("📚 Assign Subject to Lecturer");
        title.setStyle("-fx-font-size: 22px; -fx-text-fill: white; -fx-font-weight: bold;");

        TextField lecturerIdField = new TextField();
        lecturerIdField.setPromptText("Lecturer ID");
        lecturerIdField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 5px;");

        TextField subjectIdField = new TextField();
        subjectIdField.setPromptText("Subject ID");
        subjectIdField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 5px;");

        Label message = new Label();
        message.setStyle("-fx-text-fill: yellow; -fx-font-weight: bold;");

        Button submit = new Button("Assign Subject");
        Button back = new Button("Back");

        String buttonStyle = "-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;";
        submit.setStyle(buttonStyle);
        back.setStyle(buttonStyle);
        submit.setPrefWidth(200);
        back.setPrefWidth(200);

        submit.setOnAction(e -> {
            String lecturerId = lecturerIdField.getText().trim();
            String subjectId = subjectIdField.getText().trim();

            Lecturer lecturer = findLecturerById(lecturerId);
            Subject subject = findSubjectById(subjectId);

            if (lecturer == null) {
                message.setText("Lecturer not found.");
            } else if (subject == null) {
                message.setText("Subject not found.");
            } else {
                lecturer.assignSubject(subject);
                message.setText("Subject assigned successfully.");
            }
            lecturerIdField.clear();
            subjectIdField.clear();
        });


        back.setOnAction(e -> showAdminMenu(null));

        layout.getChildren().addAll(title, lecturerIdField, subjectIdField, submit, back, message);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #00f2fe);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 400));
        primaryStage.setTitle("Assign Subject to Lecturer");
    }
    private void showAssignSubjectToStudentScreen() {
        VBox layout = new VBox(20);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        Label title = new Label("🎓 Assign Subject to Student");
        title.setStyle("-fx-font-size: 22px; -fx-text-fill: white; -fx-font-weight: bold;");

        TextField studentIdField = new TextField();
        studentIdField.setPromptText("Student ID");
        studentIdField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 5px;");

        TextField subjectIdField = new TextField();
        subjectIdField.setPromptText("Subject ID");
        subjectIdField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 5px;");

        Label message = new Label();
        message.setStyle("-fx-text-fill: yellow; -fx-font-weight: bold;");

        Button submit = new Button("Assign Subject");
        Button back = new Button("Back");

        String buttonStyle = "-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;";
        submit.setStyle(buttonStyle);
        back.setStyle(buttonStyle);
        submit.setPrefWidth(200);
        back.setPrefWidth(200);

        submit.setOnAction(e -> {
            String studentId = studentIdField.getText().trim();
            String subjectId = subjectIdField.getText().trim();

            Student student = findStudentById(studentId);
            Subject subject = findSubjectById(subjectId);

            if (student == null) {
                message.setText("Student not found.");
            } else if (subject == null) {
                message.setText("Subject not found.");
            } else {
                student.assignSubject(subject);
                message.setText("Subject assigned successfully.");
            }
            studentIdField.clear();
            subjectIdField.clear();
        });

        back.setOnAction(e -> showAdminMenu(null));

        layout.getChildren().addAll(title, studentIdField, subjectIdField, submit, back, message);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #00f2fe);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 400));
        primaryStage.setTitle("Assign Subject to Student");
    }
    private void showDeleteStudentScreen() {
        VBox layout = new VBox(20);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        Label title = new Label("❌ Delete Student");
        title.setStyle("-fx-font-size: 22px; -fx-text-fill: white; -fx-font-weight: bold;");

        TextField idField = new TextField();
        idField.setPromptText("Student ID");
        idField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 5px;");

        Label message = new Label();
        message.setStyle("-fx-text-fill: yellow; -fx-font-weight: bold;");

        Button submit = new Button("Delete Student");
        Button back = new Button("Back");

        String buttonStyle = "-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;";
        submit.setStyle(buttonStyle);
        back.setStyle(buttonStyle);
        submit.setPrefWidth(200);
        back.setPrefWidth(200);

        submit.setOnAction(e -> {
            String id = idField.getText().trim();
            if (students.removeIf(s -> s.getId().equals(id))) {
                message.setText("Student deleted successfully.");
            } else {
                message.setText("Student not found.");
            }
        });

        back.setOnAction(e -> showAdminMenu(null));

        layout.getChildren().addAll(title, idField, submit, back, message);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #00f2fe);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 350));
        primaryStage.setTitle("Delete Student");
    }
    private void showDeleteLecturerScreen() {
        VBox layout = new VBox(20);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        Label title = new Label("❌ Delete Lecturer");
        title.setStyle("-fx-font-size: 22px; -fx-text-fill: white; -fx-font-weight: bold;");

        TextField idField = new TextField();
        idField.setPromptText("Lecturer ID");
        idField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 5px;");

        Label message = new Label();
        message.setStyle("-fx-text-fill: yellow; -fx-font-weight: bold;");

        Button submit = new Button("Delete Lecturer");
        Button back = new Button("Back");

        String buttonStyle = "-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;";
        submit.setStyle(buttonStyle);
        back.setStyle(buttonStyle);
        submit.setPrefWidth(200);
        back.setPrefWidth(200);

        submit.setOnAction(e -> {
            String id = idField.getText().trim();
            if (lecturers.removeIf(l -> l.getId().equals(id))) {
                message.setText("Lecturer deleted successfully.");
            } else {
                message.setText("Lecturer not found.");
            }
        });

        back.setOnAction(e -> showAdminMenu(null));

        layout.getChildren().addAll(title, idField, submit, back, message);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #43cea2, #185a9d);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 350));
        primaryStage.setTitle("Delete Lecturer");
    }
    private void showUpdateStudentScreen() {
        VBox layout = new VBox(20);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        Label title = new Label("🔄 Update Student");
        title.setStyle("-fx-font-size: 22px; -fx-text-fill: white; -fx-font-weight: bold;");

        TextField idField = new TextField();
        idField.setPromptText("Student ID");
        idField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 5px;");

        TextField nameField = new TextField();
        nameField.setPromptText("New Name");
        nameField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 5px;");

        TextField usernameField = new TextField();
        usernameField.setPromptText("New Username");
        usernameField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 5px;");

        PasswordField passwordField = new PasswordField();
        passwordField.setPromptText("New Password");
        passwordField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 5px;");

        Label message = new Label();
        message.setStyle("-fx-text-fill: yellow; -fx-font-weight: bold;");

        Button submit = new Button("Update Student");
        Button back = new Button("Back");

        String buttonStyle = "-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;";
        submit.setStyle(buttonStyle);
        back.setStyle(buttonStyle);
        submit.setPrefWidth(200);
        back.setPrefWidth(200);

        submit.setOnAction(e -> {
            String id = idField.getText().trim();
            String name = nameField.getText().trim();
            String username = usernameField.getText().trim();
            String password = passwordField.getText().trim();

            Student student = findStudentById(id);
            if (student == null) {
                message.setText("Student not found.");
            } else if (name.isEmpty() || username.isEmpty() || password.isEmpty()) {
                message.setText("All fields are required.");
            } else {
                student.updateInfo(name, username, password);
                message.setText("Student updated successfully.");
            }
        });

        back.setOnAction(e -> showAdminMenu(null));

        layout.getChildren().addAll(title, idField, nameField, usernameField, passwordField, submit, back, message);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #00f2fe);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 500));
        primaryStage.setTitle("Update Student");
    }
    private void showUpdateLecturerScreen() {
        VBox layout = new VBox(20);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        Label title = new Label("🔄 Update Lecturer");
        title.setStyle("-fx-font-size: 22px; -fx-text-fill: white; -fx-font-weight: bold;");

        TextField idField = new TextField();
        idField.setPromptText("Lecturer ID");
        idField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 5px;");

        TextField nameField = new TextField();
        nameField.setPromptText("New Name");
        nameField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 5px;");

        TextField usernameField = new TextField();
        usernameField.setPromptText("New Username");
        usernameField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 5px;");

        PasswordField passwordField = new PasswordField();
        passwordField.setPromptText("New Password");
        passwordField.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 5px;");

        Label message = new Label();
        message.setStyle("-fx-text-fill: yellow; -fx-font-weight: bold;");

        Button submit = new Button("Update Lecturer");
        Button back = new Button("Back");

        String buttonStyle = "-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;";
        submit.setStyle(buttonStyle);
        back.setStyle(buttonStyle);
        submit.setPrefWidth(200);
        back.setPrefWidth(200);

        submit.setOnAction(e -> {
            String id = idField.getText().trim();
            String name = nameField.getText().trim();
            String username = usernameField.getText().trim();
            String password = passwordField.getText().trim();

            Lecturer lecturer = findLecturerById(id);
            if (lecturer == null) {
                message.setText("Lecturer not found.");
            } else if (name.isEmpty() || username.isEmpty() || password.isEmpty()) {
                message.setText("All fields are required.");
            } else {
                lecturer.updateInfo(name, username, password);
                message.setText("Lecturer updated successfully.");
            }
        });

        back.setOnAction(e -> showAdminMenu(null));

        layout.getChildren().addAll(title, idField, nameField, usernameField, passwordField, submit, back, message);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #00f2fe);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 500));
        primaryStage.setTitle("Update Lecturer");
    }

    private void showListStudentsScreen() {
        VBox layout = new VBox(20);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        Label title = new Label("📚 Students List");
        title.setStyle("-fx-font-size: 22px; -fx-text-fill: white; -fx-font-weight: bold;");

        ListView<String> studentList = new ListView<>();
        studentList.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px;");
        studentList.setPrefHeight(200);

        for (Student s : students) {
            studentList.getItems().add("ID: " + s.getId() + ", Name: " + s.name + ", Username: " + s.username);
        }

        Button back = new Button("Back");
        back.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; -fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;");
        back.setPrefWidth(200);
        back.setOnAction(e -> showAdminMenu(null));

        layout.getChildren().addAll(title, studentList, back);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #00f2fe);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 500));
        primaryStage.setTitle("Students List");
    }

    private void showListLecturersScreen() {
        VBox layout = new VBox(20);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        Label title = new Label("👨‍🏫 Lecturers List");
        title.setStyle("-fx-font-size: 22px; -fx-text-fill: white; -fx-font-weight: bold;");

        ListView<String> lecturerList = new ListView<>();
        lecturerList.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #43cea2; -fx-font-size: 14px;");
        lecturerList.setPrefHeight(200);

        for (Lecturer l : lecturers) {
            lecturerList.getItems().add("ID: " + l.getId() + ", Name: " + l.name + ", Username: " + l.username);
        }

        Button back = new Button("Back");
        back.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #43cea2; -fx-font-size: 14px; -fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;");
        back.setPrefWidth(200);
        back.setOnAction(e -> showAdminMenu(null));

        layout.getChildren().addAll(title, lecturerList, back);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #43cea2, #185a9d);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 500));
        primaryStage.setTitle("Lecturers List");
    }

    private void showSearchUserScreen() {
        VBox layout = new VBox(15);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        Label title = new Label("🔍 Search User");
        title.setStyle("-fx-font-size: 22px; -fx-text-fill: white; -fx-font-weight: bold;");

        TextField usernameField = new TextField();
        usernameField.setPromptText("Enter Username");
        usernameField.setStyle("-fx-font-size: 14px; -fx-padding: 10px;");

        ListView<String> results = new ListView<>();
        results.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #43cea2; -fx-font-size: 14px;");
        results.setPrefHeight(200);

        Button search = new Button("Search");
        search.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #43cea2; -fx-font-size: 14px; -fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;");
        search.setPrefWidth(200);

        Button back = new Button("Back");
        back.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #43cea2; -fx-font-size: 14px; -fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;");
        back.setPrefWidth(200);


        search.setOnAction(e -> {
            results.getItems().clear();
            String username = usernameField.getText().trim();
            boolean found = false;


            for (Student s : students) {
                if (s.username.equals(username)) {
                    results.getItems().add("Student: " + s.name + " (ID: " + s.getId() + ")");
                    found = true;
                }
            }
            for (Lecturer l : lecturers) {
                if (l.username.equals(username)) {
                    results.getItems().add("Lecturer: " + l.name + " (ID: " + l.getId() + ")");
                    found = true;
                }
            }
            for (Admin a : admins) {
                if (a.username.equals(username)) {
                    results.getItems().add("Admin: " + a.name + " (ID: " + a.getId() + ")");
                    found = true;
                }
            }

            if (!found) {
                results.getItems().add("User not found.");
            }
        });

        back.setOnAction(e -> showAdminMenu(null));

        layout.getChildren().addAll(title, usernameField, search, results, back);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #43cea2, #185a9d);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 500));
        primaryStage.setTitle("Search User");
    }


    private void showLecturerMenu(Lecturer lecturer) {
        VBox layout = new VBox(15);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        Label title = new Label("Lecturer Menu");
        title.setStyle("-fx-font-size: 22px; -fx-font-weight: bold; -fx-text-fill: white;");

        Button addExam = new Button("Add Exam");
        Button deleteExam = new Button("Delete Exam");
        Button updateExam = new Button("Update Exam");
        Button listExams = new Button("List Exams");
        Button viewSubjects = new Button("View Assigned Subjects");
        Button back = new Button("Logout");

        String buttonStyle = "-fx-background-color: #ffffff; -fx-text-fill: #43cea2; -fx-font-size: 14px; " +
                "-fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;";
        addExam.setStyle(buttonStyle);
        deleteExam.setStyle(buttonStyle);
        updateExam.setStyle(buttonStyle);
        listExams.setStyle(buttonStyle);
        viewSubjects.setStyle(buttonStyle);
        back.setStyle(buttonStyle);

        addExam.setPrefWidth(200);
        deleteExam.setPrefWidth(200);
        updateExam.setPrefWidth(200);
        listExams.setPrefWidth(200);
        viewSubjects.setPrefWidth(200);
        back.setPrefWidth(200);

        addExam.setOnAction(e -> showAddExamScreen(lecturer));
        deleteExam.setOnAction(e -> showDeleteExamScreen(lecturer));
        updateExam.setOnAction(e -> showUpdateExamScreen(lecturer));
        listExams.setOnAction(e -> showListExamsScreen(lecturer));
        viewSubjects.setOnAction(e -> showViewSubjectsScreen(lecturer));
        back.setOnAction(e -> showLoginScreen());

        layout.getChildren().addAll(title, addExam, deleteExam, updateExam, listExams, viewSubjects, back);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #00f2fe);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 550));
    }

    private void showAddExamScreen(Lecturer lecturer) {
        VBox layout = new VBox(15);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        Label title = new Label("Add Exam");
        title.setStyle("-fx-font-size: 22px; -fx-font-weight: bold; -fx-text-fill: white;");

        TextField subjectIdField = new TextField();
        subjectIdField.setPromptText("Subject ID");

        TextField durationField = new TextField();
        durationField.setPromptText("Duration (minutes)");

        TextField q1 = new TextField();
        q1.setPromptText("Question 1");
        TextField a1 = new TextField();
        a1.setPromptText("Answer 1");

        TextField q2 = new TextField();
        q2.setPromptText("Question 2");
        TextField a2 = new TextField();
        a2.setPromptText("Answer 2");

        TextField q3 = new TextField();
        q3.setPromptText("Question 3");
        TextField a3 = new TextField();
        a3.setPromptText("Answer 3");

        Button submit = new Button("Add Exam");
        Button back = new Button("Back");
        Label message = new Label();
        message.setStyle("-fx-text-fill: yellow; -fx-font-weight: bold;");

        String buttonStyle = "-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; " +
                "-fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;";
        submit.setStyle(buttonStyle);
        back.setStyle(buttonStyle);

        submit.setPrefWidth(200);
        back.setPrefWidth(200);

        submit.setOnAction(e -> {
            try {
                String subjectId = subjectIdField.getText();
                int duration = Integer.parseInt(durationField.getText());

                if (subjectId.isEmpty() || q1.getText().isEmpty() || a1.getText().isEmpty() ||
                        q2.getText().isEmpty() || a2.getText().isEmpty() || q3.getText().isEmpty() || a3.getText().isEmpty()) {
                    message.setText("All fields are required.");
                    return;
                }

                Exam exam = new Exam(subjectId, lecturer.getId(), duration);
                exam.questions.addAll(Arrays.asList(q1.getText(), q2.getText(), q3.getText()));
                exam.correctAnswers.addAll(Arrays.asList(a1.getText(), a2.getText(), a3.getText()));
                exams.add(exam);

                message.setText("Exam added successfully.");
            } catch (NumberFormatException ex) {
                message.setText("Duration must be a number.");
            }
        });

        back.setOnAction(e -> showLecturerMenu(lecturer));

        layout.getChildren().addAll(title, subjectIdField, durationField, q1, a1, q2, a2, q3, a3, submit, back, message);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #00f2fe);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 650));
    }

    private void showDeleteExamScreen(Lecturer lecturer) {
        VBox layout = new VBox(15);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        Label title = new Label("Delete Exam");
        title.setStyle("-fx-font-size: 22px; -fx-font-weight: bold; -fx-text-fill: white;");

        TextField subjectIdField = new TextField();
        subjectIdField.setPromptText("Enter Subject ID");

        Button submit = new Button("Delete Exam");
        Button back = new Button("Back");
        Label message = new Label();
        message.setStyle("-fx-text-fill: yellow; -fx-font-weight: bold;");


        String buttonStyle = "-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; " +
                "-fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;";
        submit.setStyle(buttonStyle);
        back.setStyle(buttonStyle);

        submit.setPrefWidth(200);
        back.setPrefWidth(200);

        submit.setOnAction(e -> {
            String subjectId = subjectIdField.getText();
            if (subjectId.isEmpty()) {
                message.setText("Subject ID is required.");
                return;
            }

            boolean deleted = exams.removeIf(ex -> ex.subjectId.equals(subjectId) && ex.lecturerId.equals(lecturer.getId()));
            if (deleted) {
                message.setText("Exam deleted successfully.");
            } else {
                message.setText("Exam not found.");
            }
        });

        back.setOnAction(e -> showLecturerMenu(lecturer));

        layout.getChildren().addAll(title, subjectIdField, submit, back, message);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #00f2fe);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 300));
    }

    private void showUpdateExamScreen(Lecturer lecturer) {
        VBox layout = new VBox(15);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        Label title = new Label("Update Exam");
        title.setStyle("-fx-font-size: 22px; -fx-font-weight: bold; -fx-text-fill: white;");

        TextField subjectIdField = new TextField();
        subjectIdField.setPromptText("Enter Subject ID");

        TextField durationField = new TextField();
        durationField.setPromptText("New Duration (minutes)");

        TextField q1 = new TextField();
        q1.setPromptText("New Question 1");

        TextField a1 = new TextField();
        a1.setPromptText("New Answer 1");

        TextField q2 = new TextField();
        q2.setPromptText("New Question 2");

        TextField a2 = new TextField();
        a2.setPromptText("New Answer 2");

        TextField q3 = new TextField();
        q3.setPromptText("New Question 3");

        TextField a3 = new TextField();
        a3.setPromptText("New Answer 3");

        Button submit = new Button("Update Exam");
        Button back = new Button("Back");
        Label message = new Label();
        message.setStyle("-fx-text-fill: yellow; -fx-font-weight: bold;");

        String buttonStyle = "-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; " +
                "-fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;";
        submit.setStyle(buttonStyle);
        back.setStyle(buttonStyle);

        submit.setPrefWidth(200);
        back.setPrefWidth(200);

        submit.setOnAction(e -> {
            try {
                String subjectId = subjectIdField.getText();
                Exam exam = exams.stream().filter(ex -> ex.subjectId.equals(subjectId) && ex.lecturerId.equals(lecturer.getId())).findFirst().orElse(null);
                if (exam == null) {
                    message.setText("Exam not found.");
                    return;
                }

                int duration = Integer.parseInt(durationField.getText());
                if (q1.getText().isEmpty() || a1.getText().isEmpty() || q2.getText().isEmpty() || a2.getText().isEmpty() ||
                        q3.getText().isEmpty() || a3.getText().isEmpty()) {
                    message.setText("All fields are required.");
                    return;
                }

                exam.duration = duration;
                exam.questions.clear();
                exam.correctAnswers.clear();
                exam.questions.addAll(Arrays.asList(q1.getText(), q2.getText(), q3.getText()));
                exam.correctAnswers.addAll(Arrays.asList(a1.getText(), a2.getText(), a3.getText()));
                message.setText("Exam updated successfully.");
            } catch (NumberFormatException ex) {
                message.setText("Duration must be a number.");
            }
        });

        back.setOnAction(e -> showLecturerMenu(lecturer));

        layout.getChildren().addAll(title, subjectIdField, durationField, q1, a1, q2, a2, q3, a3, submit, back, message);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #00f2fe);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 650));
    }

    private void showListExamsScreen(Lecturer lecturer) {
        VBox layout = new VBox(15);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        Label title = new Label("Exams List");
        title.setStyle("-fx-font-size: 22px; -fx-font-weight: bold; -fx-text-fill: white;");

        ListView<String> examList = new ListView<>();
        for (Exam e : exams) {
            if (e.lecturerId.equals(lecturer.getId())) {
                examList.getItems().add("Subject: " + e.subjectId + ", Duration: " + e.duration + " minutes");
            }
        }

        if (examList.getItems().isEmpty()) {
            examList.getItems().add("No exams found.");
        }

        Button back = new Button("Back");
        back.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; " +
                "-fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;");
        back.setPrefWidth(200);

        back.setOnAction(e -> showLecturerMenu(lecturer));

        layout.getChildren().addAll(title, examList, back);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #00f2fe);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 600));
    }

    private void showViewSubjectsScreen(Lecturer lecturer) {
        VBox layout = new VBox(15);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        Label title = new Label("Assigned Subjects");
        title.setStyle("-fx-font-size: 22px; -fx-font-weight: bold; -fx-text-fill: white;");

        ListView<String> subjectList = new ListView<>();
        for (Subject s : lecturer.assignedSubjects) {
            subjectList.getItems().add("Subject: " + s.name);
        }

        if (subjectList.getItems().isEmpty()) {
            subjectList.getItems().add("No subjects assigned.");
        }

        Button back = new Button("Back");
        back.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 14px; " +
                "-fx-background-radius: 20; -fx-font-weight: bold; -fx-padding: 10 20;");
        back.setPrefWidth(200);

        back.setOnAction(e -> showLecturerMenu(lecturer));

        layout.getChildren().addAll(title, subjectList, back);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #00f2fe);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 600));
    }

    private void showStudentMenu(Student student) {
        VBox layout = new VBox(20);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        Label title = new Label("Student Menu");
        title.setStyle("-fx-font-size: 24px; -fx-font-weight: bold; -fx-text-fill: white;");

        Button takeExam = new Button("Take Exam");
        Button viewScores = new Button("View Scores");
        Button back = new Button("Logout");

        takeExam.setStyle("-fx-background-color: #4facfe; -fx-text-fill: white; -fx-font-size: 16px; -fx-font-weight: bold; -fx-background-radius: 20; -fx-padding: 10 20;");
        viewScores.setStyle("-fx-background-color: #00f2fe; -fx-text-fill: white; -fx-font-size: 16px; -fx-font-weight: bold; -fx-background-radius: 20; -fx-padding: 10 20;");
        back.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 16px; -fx-font-weight: bold; -fx-background-radius: 20; -fx-padding: 10 20;");

        takeExam.setOnAction(e -> showTakeExamScreen(student));
        viewScores.setOnAction(e -> showViewScoresScreen(student));
        back.setOnAction(e -> showLoginScreen());

        layout.getChildren().addAll(title, takeExam, viewScores, back);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #00f2fe);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 400));
    }

    private void showTakeExamScreen(Student student) {
        VBox layout = new VBox(20);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        Label title = new Label("Take Exam");
        title.setStyle("-fx-font-size: 24px; -fx-font-weight: bold; -fx-text-fill: white;");

        TextField subjectIdField = new TextField();
        subjectIdField.setPromptText("Subject ID");
        subjectIdField.setStyle("-fx-font-size: 16px; -fx-padding: 10;");

        Button startExam = new Button("Start Exam");
        Button back = new Button("Back");

        startExam.setStyle("-fx-background-color: #4facfe; -fx-text-fill: white; -fx-font-size: 16px; -fx-font-weight: bold; -fx-background-radius: 20; -fx-padding: 10 20;");
        back.setStyle("-fx-background-color: #ffffff; -fx-text-fill: #4facfe; -fx-font-size: 16px; -fx-font-weight: bold; -fx-background-radius: 20; -fx-padding: 10 20;");

        Label message = new Label();
        message.setStyle("-fx-font-size: 14px; -fx-text-fill: red;");

        startExam.setOnAction(e -> {
            String subjectId = subjectIdField.getText();
            Exam exam = exams.stream().filter(ex -> ex.subjectId.equals(subjectId)).findFirst().orElse(null);
            if (exam == null) {
                message.setText("Exam not found.");
                return;
            }
            showExamQuestionsScreen(student, exam);
        });

        back.setOnAction(e -> showStudentMenu(student));

        layout.getChildren().addAll(title, subjectIdField, startExam, back, message);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #00f2fe);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 350));
    }

    private void showExamQuestionsScreen(Student student, Exam exam) {
        VBox layout = new VBox(15);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        Label title = new Label("Exam Questions");
        title.setStyle("-fx-font-size: 24px; -fx-font-weight: bold; -fx-text-fill: white;");

        Label questionLabel = new Label();
        questionLabel.setStyle("-fx-font-size: 18px; -fx-font-weight: bold; -fx-text-fill: white;");


        TextField answerField = new TextField();
        answerField.setPromptText("Your Answer");
        answerField.setStyle("-fx-font-size: 16px; -fx-padding: 10;");

        Button next = new Button("Next");
        Button submit = new Button("Submit");
        submit.setVisible(false);

        next.setStyle("-fx-background-color: #4facfe; -fx-text-fill: white; -fx-font-size: 16px; -fx-font-weight: bold; -fx-background-radius: 20; -fx-padding: 10 20;");
        submit.setStyle("-fx-background-color: #00f2fe; -fx-text-fill: white; -fx-font-size: 16px; -fx-font-weight: bold; -fx-background-radius: 20; -fx-padding: 10 20;");

        List<String> answers = new ArrayList<>();
        final int[] currentQuestion = {0};

        questionLabel.setText("Q1: " + exam.questions.get(0));

        next.setOnAction(e -> {
            answers.add(answerField.getText());
            answerField.clear();
            currentQuestion[0]++;

            if (currentQuestion[0] < exam.questions.size()) {
                questionLabel.setText("Q" + (currentQuestion[0] + 1) + ": " + exam.questions.get(currentQuestion[0]));

                if (currentQuestion[0] == exam.questions.size() - 1) {
                    next.setVisible(false);
                    submit.setVisible(true);
                }
            }
        });

        submit.setOnAction(e -> {
            answers.add(answerField.getText());
            int score = exam.evaluate(answers);
            scores.computeIfAbsent(student.getId(), k -> new HashMap<>()).put(exam.subjectId, score);

            Alert alert = new Alert(Alert.AlertType.INFORMATION);
            alert.setTitle("Exam Submitted");
            alert.setHeaderText(null);
            alert.setContentText("Your score: " + score);
            alert.showAndWait();

            showStudentMenu(student);
        });

        layout.getChildren().addAll(title, questionLabel, answerField, next, submit);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #00f2fe);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 400));
    }

    private void showViewScoresScreen(Student student) {
        VBox layout = new VBox(15);
        layout.setPadding(new Insets(30));
        layout.setAlignment(Pos.CENTER);

        Label title = new Label("Your Scores");
        title.setStyle("-fx-font-size: 24px; -fx-font-weight: bold; -fx-text-fill: white;");

        ListView<String> scoreList = new ListView<>();
        scoreList.setStyle("-fx-font-size: 16px; -fx-background-color: #f5f5f5; -fx-border-color: #4facfe; -fx-border-width: 2;");

        Map<String, Integer> userScores = scores.get(student.getId());
        if (userScores == null || userScores.isEmpty()) {
            scoreList.getItems().add("No scores available.");
        } else {
            userScores.forEach((subj, scr) -> scoreList.getItems().add("Subject: " + subj + " - Score: " + scr));
        }

        Button back = new Button("Back");
        back.setStyle("-fx-background-color: #4facfe; -fx-text-fill: white; -fx-font-size: 16px; -fx-font-weight: bold; -fx-background-radius: 20; -fx-padding: 10 20;");
        back.setOnAction(e -> showStudentMenu(student));

        layout.getChildren().addAll(title, scoreList, back);

        StackPane background = new StackPane();
        background.setStyle("-fx-background-color: linear-gradient(to bottom right, #4facfe, #00f2fe);");
        background.getChildren().add(layout);

        primaryStage.setScene(new Scene(background, 450, 400));
    }

    private Student findStudentById(String id) {
        return students.stream().filter(s -> s.getId().equals(id)).findFirst().orElse(null);
    }

    private Lecturer findLecturerById(String id) {
        return lecturers.stream().filter(l -> l.getId().equals(id)).findFirst().orElse(null);
    }

    private Subject findSubjectById(String id) {
        return subjects.stream().filter(s -> s.id.equals(id)).findFirst().orElse(null);
    }

    private static void loadAll() throws IOException {
        File f;
        f = new File("students.txt");
        if (f.exists()) {
            try (BufferedReader br = new BufferedReader(new FileReader(f))) {
                String line;
                while ((line = br.readLine()) != null) {
                    String[] a = line.split(",");
                    students.add(new Student(a[0], a[1], a[2], a[3]));
                }
            }

        }
        f = new File("lecturers.txt");
        if (f.exists()) {
            try (BufferedReader br = new BufferedReader(new FileReader(f))) {
                String line;
                while ((line = br.readLine()) != null) {
                    String[] a = line.split(",");
                    lecturers.add(new Lecturer(a[0], a[1], a[2], a[3]));
                }
            }
        }
        f = new File("admin.txt");
        if (f.exists()) {
            try (BufferedReader br = new BufferedReader(new FileReader(f))) {
                String line;
                while ((line = br.readLine()) != null) {
                    String[] a = line.split(",");
                    admins.add(new Admin(a[0], a[1], a[2], a[3]));
                }
            }
        }

        f = new File("subjects.txt");
        if (f.exists()) {
            try (BufferedReader br = new BufferedReader(new FileReader(f))) {
                String line;
                while ((line = br.readLine()) != null) {
                    String[] a = line.split(",");
                    subjects.add(new Subject(a[0], a[1]));
                }
            }
        }
        f = new File("exams.txt");
        if (f.exists()) {
            try (BufferedReader br = new BufferedReader(new FileReader(f))) {
                String line;
                while ((line = br.readLine()) != null) {
                    String[] a = line.split("\\|");
                    Exam e = new Exam(a[0], a[1], Integer.parseInt(a[2]));
                    e.questions = Arrays.asList(a[3].split(";")).subList(0, 3);
                    e.correctAnswers = Arrays.asList(a[4].split(";")).subList(0, 3);
                    exams.add(e);
                }
            }
        }
        f = new File("scores.txt");
        if (f.exists()) {
            try (BufferedReader br = new BufferedReader(new FileReader(f))) {
                String line;
                while ((line = br.readLine()) != null) {
                    String[] a = line.split(",");
                    scores.computeIfAbsent(a[0], k -> new HashMap<>()).put(a[1], Integer.parseInt(a[2]));
                }
            }
        }
    }

    private void saveAll() throws IOException {
        try (PrintWriter pw = new PrintWriter("students.txt")) {
            for (Student s : students)
                pw.println(s.id + "," + s.name + "," + s.username + "," + s.password);
        } catch (IOException e) {
            System.err.println("Error saving students: " + e.getMessage());
        }

        try (PrintWriter pw = new PrintWriter("lecturers.txt")) {
            for (Lecturer l : lecturers)
                pw.println(l.id + "," + l.name + "," + l.username + "," + l.password);
        } catch (IOException e) {
            System.err.println("Error saving lecturers: " + e.getMessage());
        }

        try (PrintWriter pw = new PrintWriter("admin.txt")) {
            for (Admin a : admins)
                pw.println(a.id + "," + a.name + "," + a.username + "," + a.password);
        } catch (IOException e) {
            System.err.println("Error saving admins: " + e.getMessage());
        }

        try (PrintWriter pw = new PrintWriter("subjects.txt")) {
            for (Subject s : subjects)
                pw.println(s.id + "," + s.name);
        } catch (IOException e) {
            System.err.println("Error saving subjects: " + e.getMessage());
        }

        try (PrintWriter pw = new PrintWriter("exams.txt")) {
            for (Exam e : exams) {
                String questions = String.join(";", e.questions);
                String answers = String.join(";", e.correctAnswers);
                pw.println(e.subjectId + "|" + e.lecturerId + "|" + e.duration + "|" + questions + "|" + answers);
            }
        } catch (IOException e) {
            System.err.println("Error saving exams: " + e.getMessage());
        }

        try (PrintWriter pw = new PrintWriter("scores.txt")) {
            for (Map.Entry<String, Map<String, Integer>> entry : scores.entrySet()) {
                String studentId = entry.getKey();
                for (Map.Entry<String, Integer> scoreEntry : entry.getValue().entrySet()) {
                    String subjectId = scoreEntry.getKey();
                    int score = scoreEntry.getValue();
                    pw.println(studentId + "," + subjectId + "," + score);
                }
            }
        } catch (IOException e) {
            System.err.println("Error saving scores: " + e.getMessage());
        }
    }

    public static void main(String[] args) {
        try {
            loadAll();
            launch(args);
        } catch (IOException e) {
            System.err.println("Error loading data: " + e.getMessage());
        }
    }

    @Override
    public void stop() {
        try {
            saveAll();
            System.out.println("Data saved on exit.");
        } catch (IOException e) {
            System.err.println("Error saving data on exit: " + e.getMessage());
        }
    }
}
