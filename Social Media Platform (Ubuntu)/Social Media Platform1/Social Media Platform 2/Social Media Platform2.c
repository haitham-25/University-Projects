#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>

// Function prototypes
void list_directory(const char *dir_path);
void change_permissions();
void create_symlink();
void copy_file();
void move_file();
void create_or_update_file();
void view_file_content();
void find_files();
void set_alias();

// Main menu for the social media platform
void admin_menu();
void moderator_menu();
void user_menu();

int main() {
    int user_type;

    while (1) {
        // User selection menu
        printf("\nSocial Media Platform Menu:\n");
        printf("1. Admin\n");
        printf("2. Moderator\n");
        printf("3. User\n");
        printf("4. Exit\n");
        printf("Select your role (1-3): ");
        scanf("%d", &user_type);

        // Display menu based on user type
        switch (user_type) {
            case 1:
                admin_menu();
                break;
            case 2:
                moderator_menu();
                break;
            case 3:
                user_menu();
                break;
            case 4:
                printf("Exiting...\n");
                exit(0);
            default:
                printf("Invalid selection. Try again.\n");
        }
    }

    return 0;
}

// Function to list a directory
void list_directory(const char *dir_path) {
    char command[256];
    snprintf(command, sizeof(command), "ls -l %s", dir_path);
    system(command);
}

// Function to change file permissions
void change_permissions() {
    char file_path[100];
    mode_t mode;
    printf("Enter file path to change permissions: ");
    scanf("%s", file_path);
    printf("Enter new permission mode (e.g., 0644): ");
    scanf("%o", &mode);
    if (chmod(file_path, mode) == 0) {
        printf("Permissions changed successfully.\n");
    } else {
        perror("chmod failed");
    }
}

// Function to create a symbolic link
void create_symlink() {
    char target[100], linkpath[100];
    printf("Enter the target file path: ");
    scanf("%s", target);
    printf("Enter the symbolic link path: ");
    scanf("%s", linkpath);
    if (symlink(target, linkpath) == 0) {
        printf("Symbolic link created successfully.\n");
    } else {
        perror("symlink failed");
    }
}

// Function to copy files
void copy_file() {
    char src[100], dest[100];
    printf("Enter the source file path: ");
    scanf("%s", src);
    printf("Enter the destination file path: ");
    scanf("%s", dest);
    char command[256];
    snprintf(command, sizeof(command), "cp %s %s", src, dest);
    system(command);
}

// Function to move files
void move_file() {
    char src[100], dest[100];
    printf("Enter the source file path: ");
    scanf("%s", src);
    printf("Enter the destination file path: ");
    scanf("%s", dest);
    if (rename(src, dest) == 0) {
        printf("File moved successfully.\n");
    } else {
        perror("rename failed");
    }
}

// Function to create or update files (redirection)
void create_or_update_file() {
    char file_path[100], content[256];
    printf("Enter the file path to update: ");
    scanf("%s", file_path);
    printf("Enter content to add: ");
    scanf(" %[^\n]", content);  // Allows multi-word input
    FILE *file = fopen(file_path, "a");
    if (file != NULL) {
        fprintf(file, "%s\n", content);
        fclose(file);
        printf("File updated.\n");
    } else {
        perror("fopen failed");
    }
}

// Function to view file content
void view_file_content() {
    char file_path[100];
    printf("Enter the file path to view: ");
    scanf("%s", file_path);
    char command[256];
    snprintf(command, sizeof(command), "cat %s", file_path);
    system(command);
}

// Function to find files
void find_files() {
    char dir[100], filename[100];
    printf("Enter directory to search: ");
    scanf("%s", dir);
    printf("Enter filename to search for: ");
    scanf("%s", filename);
    char command[256];
    snprintf(command, sizeof(command), "find %s -name %s", dir, filename);
    system(command);
}

// Admin menu
void admin_menu() {
    int choice;
    while (1) {
        printf("\nAdmin Menu:\n");
        printf("1. List directory\n");
        printf("2. Change permissions\n");
        printf("3. Create symbolic link\n");
        printf("4. Copy files\n");
        printf("5. Move files\n");
        printf("6. Find files\n");
        printf("7. Exit to main menu\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);

        switch (choice) {
            case 1:
                list_directory("/socialmedia/admin");
                break;
            case 2:
                change_permissions();
                break;
            case 3:
                create_symlink();
                break;
            case 4:
                copy_file();
                break;
            case 5:
                move_file();
                break;
            case 6:
                find_files();
                break;
            case 7:
                return;
            default:
                printf("Invalid choice. Try again.\n");
        }
    }
}

// Moderator menu
void moderator_menu() {
    int choice;
    while (1) {
        printf("\nModerator Menu:\n");
        printf("1. List directory\n");
        printf("2. View flagged posts\n");
        printf("3. Copy flagged content\n");
        printf("4. Move flagged content\n");
        printf("5. Find files\n");
        printf("6. Exit to main menu\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);

        switch (choice) {
            case 1:
                list_directory("/socialmedia/moderators");
                break;
            case 2:
                view_file_content();
                break;
            case 3:
                copy_file();
                break;
            case 4:
                move_file();
                break;
            case 5:
                find_files();
                break;
            case 6:
                return;
            default:
                printf("Invalid choice. Try again.\n");
        }
    }
}

// User menu
void user_menu() {
    int choice;
    while (1) {
        printf("\nUser Menu:\n");
        printf("1. List directory\n");
        printf("2. Create or update posts/comments\n");
        printf("3. View posts/comments\n");
        printf("4. Copy posts/comments\n");
        printf("5. Exit to main menu\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);

        switch (choice) {
            case 1:
                list_directory("/socialmedia/users");
                break;
            case 2:
                create_or_update_file();
                break;
            case 3:
                view_file_content();
                break;
            case 4:
                copy_file();
                break;
            case 5:
                return;
            default:
                printf("Invalid choice. Try again.\n");
        }
    }
}
