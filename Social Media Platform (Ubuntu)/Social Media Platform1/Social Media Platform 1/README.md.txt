# 📦 CLI-Based Social Media File Manager (Role-Based)

This C program simulates a command-line **social media platform** that supports user roles: **Admin**, **Moderator**, and **Regular User**. Each role has different permissions and capabilities related to file management and system operations.

---

## 🧩 Features

### 👤 User Roles

- **Admin**
  - Manage users (add, delete, list)
  - Manage directories and permissions
  - Create symbolic links
  - Monitor system activity (logs)
  
- **Moderator**
  - View and manage flagged content
  - Create violation reports
  - Move suspicious content
  - Read user content for moderation

- **Regular User**
  - Create posts and add comments
  - View their own posts
  - Backup their content

---

## 📁 File & Directory Structure

```plaintext
/socialmedia/
├── admin/                      # Admin operations and logs
│   └── activity_log.txt        # System logs
├── moderators/
│   ├── flagged/                # Flagged content
│   └── reports/                # Reports created by moderators
└── users/
    └── <username>/             # Individual user directories
