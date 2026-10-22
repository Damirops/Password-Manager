# 🔐 Secure Password Manager with MySQL Integration

A desktop application for managing passwords and personal data, developed in 
**Python** using the **Tkinter** interface, with **MySQL** database support (featuring an automatic JSON fallback mechanism).

## 🚀 Features
- **Profile Management:** Store and view personal information (Gmail and phone number).
- **Password Management:** Add, edit, view, and delete passwords for various accounts and services.
- **MySQL & XAMPP Support:** Automatically checks the connection to the MySQL server, creates the database, and sets up required tables if they do not exist.
- **JSON Fallback:** If the MySQL/XAMPP server is inactive, the application automatically saves data to a local `passwords.json` file.
- **Modern UI:** A customized user interface featuring a password show/hide toggle (eye icon) and clean tables.

---

## 🛠️ Prerequisites & Installation

Before running the script, make sure you have the following ready:

1. **Python** (version 3.x recommended)
2. **XAMPP** (with **Apache** and **MySQL** services running)

### 1. Installation of Required Libraries
Open your terminal (`cmd` or PowerShell) and install `mysql-connector-python`:
```bash


pip install mysql-connector-python
