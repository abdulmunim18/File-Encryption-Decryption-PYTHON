# ============================================================
#  main.py — Entry Point for SecureVault
# ============================================================

import tkinter as tk
from tkinter import messagebox
import sys


class App:
    """
    Top-level application controller.
    Manages window sizing and frame transitions:
      Login  →  User Main  (or)  Admin Dashboard
    """

    # Window sizes per screen
    SIZES = {
        "login": "520x640",
        "main":  "1050x760",
        "admin": "1200x780",
    }

    def __init__(self, root: tk.Tk):
        self.root          = root
        self.current_frame = None

        self.root.title("SecureVault — File Encryption System")
        self.root.configure(bg="#0d1117")
        self.root.resizable(True, True)

        # Show login on startup
        self.show_login()

    # ──────────────────────────────────────────────────────────────
    # Screen transitions
    # ──────────────────────────────────────────────────────────────

    def _clear(self):
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None

    def show_login(self):
        self._clear()
        self.root.geometry(self.SIZES["login"])
        self._centre_window()
        from gui_login import LoginFrame
        self.current_frame = LoginFrame(self.root, self._on_login_success)
        self.current_frame.pack(fill="both", expand=True)

    def _on_login_success(self, user: dict):
        self._clear()
        if user["role"] == "admin":
            self.root.geometry(self.SIZES["admin"])
            self._centre_window()
            from gui_admin import AdminFrame
            self.current_frame = AdminFrame(self.root, user, self.show_login)
        else:
            self.root.geometry(self.SIZES["main"])
            self._centre_window()
            from gui_main import MainFrame
            self.current_frame = MainFrame(self.root, user, self.show_login)
        self.current_frame.pack(fill="both", expand=True)

    def _centre_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"+{x}+{y}")


# ================================================================
# Bootstrap
# ================================================================

def main():
    # 1) Initialise the database (create tables + seed admin)
    try:
        import db
        db.initialize_db()
    except Exception as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Database Connection Failed",
            f"Could not connect to PostgreSQL.\n\n"
            f"Error: {exc}\n\n"
            f"Steps to fix:\n"
            f"  1. Open db_config.py and set your PostgreSQL password.\n"
            f"  2. Make sure PostgreSQL is running.\n"
            f"  3. Create the database:\n"
            f"       CREATE DATABASE file_encryptor;\n"
        )
        root.destroy()
        sys.exit(1)

    # 2) Launch the GUI
    root = tk.Tk()
    app  = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
