SecureVault — Multi-User File Encryption & Decryption System

A secure Python desktop application that allows multiple users to encrypt and decrypt files through a graphical user interface (Tkinter). The system uses PostgreSQL for centralized database management and implements Role-Based Access Control (RBAC) with Admin and User functionalities.

The project is designed to provide secure file protection, user isolation, activity monitoring, and centralized encryption key management.

🚀 Features
👤 Authentication & User Management
User Signup & Login System
Admin and Regular User roles
Pending account approval workflow
Secure password hashing using Bcrypt
User isolation and access control
🔒 File Encryption & Decryption

Supports multiple encryption algorithms using PyCryptodome:

AES
DES
3DES
Blowfish
CAST
ChaCha20
RC4
🗄️ Database Integration (PostgreSQL)
Centralized storage of:
User accounts
Encryption keys
Activity logs
Secure database-driven architecture
No manual .key file management required
📊 Admin Dashboard

Admin can:

Approve or reject users
Delete users
Monitor encryption/decryption activities
View timestamps and algorithms used
Track system usage logs
🖥️ GUI Features
Modern Tkinter-based desktop interface
Login & Signup screens
User dashboard for encryption/decryption
Admin control panel
File browser integration
📦 Technologies Used
Python 3.x
Tkinter
PostgreSQL
Psycopg2
PyCryptodome
Bcrypt
📥 Requirements

Install required Python libraries:

pip install pycryptodome psycopg2 bcrypt

Install PostgreSQL and create a database before running the application.

🧭 How to Use
1️⃣ Start the Application

Run:

python main.py
2️⃣ Signup/Login
New users must create an account using Signup.
Accounts remain in pending status until approved by the Admin.
Approved users can log in and access the system.
3️⃣ Encrypt a File
Select encryption algorithm
Browse and choose a file
Generate or select a stored encryption key
Click Encrypt

The system:

Encrypts the file
Stores key securely in PostgreSQL
Logs the activity in the database
4️⃣ Decrypt a File
Select encrypted file
Choose stored key
Click Decrypt

The system:

Retrieves key from database
Verifies integrity using MAC validation
Decrypts the file successfully
🔐 Supported Algorithms
Algorithm	Type
AES	Block Cipher
DES	Block Cipher
3DES	Block Cipher
Blowfish	Block Cipher
CAST	Block Cipher
ChaCha20	Stream Cipher
RC4	Stream Cipher
🧠 Encryption Structure
Symmetric Encryption (AES, DES, 3DES, Blowfish, CAST)

Encrypted file structure:

Nonce + MAC Tag + Ciphertext
ChaCha20
Nonce + Ciphertext
RC4
Ciphertext Only
🗄️ Database Tables

The system uses three main PostgreSQL tables:

users
encryption_keys
activity_logs

These tables manage:

User authentication
Key storage
Encryption/decryption history
Admin monitoring
🔒 Security Features
Password hashing using Bcrypt
Role-Based Access Control (RBAC)
SQL Injection protection using parameterized queries
Secure key storage inside PostgreSQL
User activity auditing
User data isolation
MAC verification for integrity checking
📁 Output Files
Encryption Output
yourfile.ext.enc
Decryption Output
yourfile_decrypted.ext
⚠️ Security Notes
Users can only access their own keys and files.
Admins can monitor activities but cannot access user passwords.
Encryption keys are securely stored in the database.
Do NOT share database credentials publicly.
Always keep PostgreSQL backups for recovery.
📌 Future Enhancements
Two-Factor Authentication (2FA)
Cloud Storage Integration
Hybrid RSA + AES Encryption
Web-based version
File sharing system
Backup & Recovery module
Project Goal

The goal of SecureVault is to provide a secure, centralized, and enterprise-level multi-user encryption management system that ensures:

Confidentiality
Integrity
Accountability
Secure Access Control

through modern cryptographic techniques and database-driven architecture.
