#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <time.h>

#define MAX_PATH 256
#define MAX_CMD 1024
#define MAX_CONTENT 2048
#define MAX_USERNAME 64
#define MAX_PASSWORD 64

// User types
#define ADMIN 1
#define MODERATOR 2
#define REGULAR_USER 3

// User structure
typedef struct {
    char username[MAX_USERNAME];
    char password[MAX_PASSWORD];
    int type;
} User;

// Function prototypes
void initializeSystem(void);
int loginUser(User *user);
void executeCommand(const char *cmd);
void logAction(const char *username, const char *action);
int validatePath(const char *path);
void sanitizeInput(char *str);

// Admin functions
void adminMenu(User *user);
void manageUsers(void);
void manageDirectories(void);
void managePermissions(void);
void createSymlink(void);
void monitorSystem(void);

// Moderator functions
void moderatorMenu(User *user);
void viewFlaggedContent(void);
void manageFlaggedContent(void);
void createReport(void);
void moveViolatingFiles(void);
void readUserContent(void);

// Regular user functions
void regularUserMenu(User *user);
void createPost(const char *username);
void addComment(const char *username);
void viewPosts(const char *username);
void backupFiles(const char *username);

// Main function
int main() {
    User currentUser;

    initializeSystem();

    while (1) {
        printf("\n=== Social Media Platform ===\n");
        printf("1. Login\n");
        printf("2. Exit\n");
        printf("Choice: ");

        int choice;
        scanf("%d", &choice);
        getchar();

        if (choice == 2) break;

        if (loginUser(&currentUser)) {
            switch (currentUser.type) {
                case ADMIN:
                    adminMenu(&currentUser);
                    break;
                case MODERATOR:
                    moderatorMenu(&currentUser);
                    break;
                case REGULAR_USER:
                    regularUserMenu(&currentUser);
                    break;
            }
        } else {
            printf("Login failed!\n");
        }
    }

    return 0;
}

// System initialization
void initializeSystem() {
    char command[MAX_CMD];

    // Create main directories with proper command formatting
    snprintf(command, sizeof(command), "mkdir -p /socialmedia/admin");
    executeCommand(command);

    snprintf(command, sizeof(command), "mkdir -p /socialmedia/moderators/flagged");
    executeCommand(command);

    snprintf(command, sizeof(command), "mkdir -p /socialmedia/moderators/reports");
    executeCommand(command);

    snprintf(command, sizeof(command), "mkdir -p /socialmedia/users");
    executeCommand(command);

    // Set permissions
    snprintf(command, sizeof(command), "chmod 700 /socialmedia/admin");
    executeCommand(command);

    snprintf(command, sizeof(command), "chmod 750 /socialmedia/moderators");
    executeCommand(command);

    snprintf(command, sizeof(command), "chmod 755 /socialmedia/users");
    executeCommand(command);
}

// User authentication
int loginUser(User *user) {
    printf("Username: ");
    fgets(user->username, sizeof(user->username), stdin);
    user->username[strcspn(user->username, "\n")] = 0;

    printf("Password: ");
    fgets(user->password, sizeof(user->password), stdin);
    user->password[strcspn(user->password, "\n")] = 0;

    if (strcmp(user->username, "admin") == 0 && strcmp(user->password, "admin123") == 0) {
        user->type = ADMIN;
        return 1;
    } else if (strcmp(user->username, "mod") == 0 && strcmp(user->password, "mod123") == 0) {
        user->type = MODERATOR;
        return 1;
    } else {
        user->type = REGULAR_USER;
        return 1;
    }
}

// Admin menu and functions
void adminMenu(User *user) {
    int choice;

    while (1) {
        printf("\n=== Admin Menu ===\n");
        printf("1. Manage Users\n");
        printf("2. Manage Directories\n");
        printf("3. Manage Permissions\n");
        printf("4. Create Symbolic Links\n");
        printf("5. Monitor System\n");
        printf("6. Logout\n");
        printf("Choice: ");

        scanf("%d", &choice);
        getchar();

        switch (choice) {
            case 1: manageUsers(); break;
            case 2: manageDirectories(); break;
            case 3: managePermissions(); break;
            case 4: createSymlink(); break;
            case 5: monitorSystem(); break;
            case 6: return;
        }
    }
}

void manageUsers() {
    char command[MAX_CMD];
    char username[64];
    int choice;

    printf("\n=== User Management ===\n");
    printf("1. Add User\n");
    printf("2. Delete User\n");
    printf("3. List Users\n");
    printf("4. Back\n");

    printf("Choice: ");
    scanf("%d", &choice);
    getchar();

    switch (choice) {
        case 1:
            printf("Enter username: ");
            fgets(username, sizeof(username), stdin);
            username[strcspn(username, "\n")] = 0;

            snprintf(command, sizeof(command), "mkdir -p /socialmedia/users/%s", username);
            executeCommand(command);
            printf("User created successfully!\n");
            break;

        case 2:
            printf("Enter username to delete: ");
            fgets(username, sizeof(username), stdin);
            username[strcspn(username, "\n")] = 0;

            snprintf(command, sizeof(command), "rm -r /socialmedia/users/%s", username);
            executeCommand(command);
            printf("User deleted successfully!\n");
            break;

        case 3:
            snprintf(command, sizeof(command), "ls -l /socialmedia/users");
            executeCommand(command);
            break;
    }
}

// Utility functions
void executeCommand(const char *cmd) {
    system(cmd);
}

void logAction(const char *username, const char *action) {
    char command[MAX_CMD];
    time_t now = time(NULL);

    snprintf(command, sizeof(command),
             "echo \"%s: %s - %s\" >> /socialmedia/admin/activity_log.txt",
             ctime(&now), username, action);
    executeCommand(command);
}
