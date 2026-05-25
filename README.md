# ENCDEC - Secure File Encryptor/Decryptor (Tkinter GUI)

A simple Python desktop application that encrypts and decrypts files using a graphical user interface (Tkinter).

It supports multiple encryption algorithms using **PyCryptodome**, including:
- AES
- DES
- 3DES
- Blowfish
- RSA

---

## Features

- 🖥️ GUI-based file selection (no command line required)
- 🔒 Encrypt files into `.enc` format
- 🔑 Save encryption keys as `.key` files
- 🔓 Decrypt `.enc` files back to original format
- ⚙️ Algorithm selection dropdown (AES / DES / 3DES / Blowfish / RSA)

---

## 📦 Requirements

- Python 3.x
- PyCryptodome library

### Install dependency:
```bash id="m3p8q1"
pip install pycryptodome

🧭 How to Use
Open the application
Select an encryption algorithm from dropdown
Click Browse and choose a file
Click Encrypt
Creates .enc file
Generates .key file(s)
🔓 To Decrypt
Select encrypted .enc file
Click Decrypt
Provide correct key file when prompted
Decrypted file is generated
📁 Output Files
🔐 Symmetric Algorithms (AES, DES, 3DES, Blowfish)
Encrypted file: yourfile.ext.enc
Key file: key_yourfile.ext.key
🔐 RSA Algorithm
Encrypted file: yourfile.ext.enc
Public key: public_key_yourfile.ext.key
Private key: private_key_yourfile.ext.key
📄 Decryption Output
yourfile.ext_decrypted.txt
🧠 Encryption Structure

For symmetric encryption:

nonce (16 bytes) + tag (16 bytes) + ciphertext
⚠️ Notes / Limitations
RSA is only suitable for small files (not large data)
For real-world usage, hybrid encryption is recommended:
RSA → encrypt AES key
AES → encrypt file data
Keep .key files secure
Do NOT upload keys or .enc files to GitHub
🛡️ Security Warning

Anyone with the key file can decrypt your data. Handle keys carefully.
