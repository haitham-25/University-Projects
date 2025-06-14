# 🖥️ CLI-Based Social Media Platform (User Role File Manager)

This project simulates a **social media platform** using a **command-line interface** in C, where users can perform operations based on their roles — **Admin**, **Moderator**, or **Regular User**. The program provides functionality for file management, directory navigation, symbolic links, and basic content creation/viewing.

---

## 📁 Project Overview

### 🧑‍💼 User Roles

- **Admin**  
  - Full control over directories and files.
  - Can create symlinks, move/copy files, search for content, and modify permissions.

- **Moderator**  
  - Can view and manage flagged content.
  - Can copy/move files and search within the `/moderators` directory.

- **Regular User**  
  - Can list user content, create or update posts/comments, view or copy their files.

---

## 📂 Directory Structure

```plaintext
/socialmedia
├── admin/                 # Admin-specific data
├── moderators/            # Moderator-level access
│   ├── flagged/           # Flagged content area
│   └── reports/           # Moderator reports
└── users/                 # Regular user content
    └── <username>/        # Each user's personal directory
