# ============================================================
#  gui_login.py — Login / Signup Screen
# ============================================================

import tkinter as tk
from tkinter import ttk
import auth

# ── Colour palette ────────────────────────────────────────────────
C_BG       = "#0d1117"
C_SURFACE  = "#161b22"
C_BORDER   = "#30363d"
C_ACCENT   = "#58a6ff"
C_GREEN    = "#3fb950"
C_RED      = "#f85149"
C_TEXT     = "#f0f6fc"
C_TEXT_DIM = "#8b949e"
C_INPUT_BG = "#0d1117"


class LoginFrame(tk.Frame):
    """Login / Signup screen shown at startup."""

    def __init__(self, master, on_login_success):
        super().__init__(master, bg=C_BG)
        self.on_login_success = on_login_success
        self._mode = "login"   # "login" | "signup"
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        # ── outer wrapper (centres the card) ──────────────────────
        wrapper = tk.Frame(self, bg=C_BG)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        # ── header logo / title ───────────────────────────────────
        tk.Label(
            wrapper, text="🔐", font=("Segoe UI Emoji", 36),
            bg=C_BG, fg=C_ACCENT
        ).pack(pady=(0, 4))

        tk.Label(
            wrapper, text="SecureVault",
            font=("Segoe UI", 22, "bold"),
            bg=C_BG, fg=C_TEXT
        ).pack()

        tk.Label(
            wrapper, text="File Encryption & Decryption System",
            font=("Segoe UI", 9),
            bg=C_BG, fg=C_TEXT_DIM
        ).pack(pady=(2, 20))

        # ── card ──────────────────────────────────────────────────
        self.card = tk.Frame(
            wrapper, bg=C_SURFACE,
            highlightbackground=C_BORDER, highlightthickness=1,
            padx=36, pady=30
        )
        self.card.pack(ipadx=10, ipady=6)

        # mode-toggle bar
        toggle_row = tk.Frame(self.card, bg=C_SURFACE)
        toggle_row.pack(fill="x", pady=(0, 22))

        self.btn_login_tab  = self._tab_btn(toggle_row, "Login",  self._switch_login)
        self.btn_signup_tab = self._tab_btn(toggle_row, "Sign Up", self._switch_signup)
        self.btn_login_tab.pack(side="left", expand=True, fill="x")
        self.btn_signup_tab.pack(side="left", expand=True, fill="x")

        # ── form ──────────────────────────────────────────────────
        self.form = tk.Frame(self.card, bg=C_SURFACE)
        self.form.pack(fill="x")

        # username
        self._field_label(self.form, "Username")
        self.entry_user = self._field_entry(self.form)

        # password
        self._field_label(self.form, "Password")
        self.entry_pass = self._field_entry(self.form, show="●")

        # confirm password (signup only)
        self.lbl_confirm = self._field_label(self.form, "Confirm Password")
        self.entry_confirm = self._field_entry(self.form, show="●")

        # error message
        self.lbl_error = tk.Label(
            self.form, text="", fg=C_RED,
            bg=C_SURFACE, font=("Segoe UI", 9),
            wraplength=300
        )
        self.lbl_error.pack(pady=(6, 0))

        # action button
        self.btn_action = tk.Button(
            self.form,
            text="Login",
            font=("Segoe UI", 11, "bold"),
            bg=C_ACCENT, fg="#0d1117",
            activebackground="#79c0ff", activeforeground="#0d1117",
            relief="flat", cursor="hand2",
            padx=10, pady=10,
            command=self._on_action
        )
        self.btn_action.pack(fill="x", pady=(18, 0))

        # bind Enter key
        for e in (self.entry_user, self.entry_pass, self.entry_confirm):
            e.bind("<Return>", lambda _: self._on_action())

        # initialise tabs
        self._switch_login()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _tab_btn(self, parent, text, cmd):
        return tk.Button(
            parent, text=text,
            font=("Segoe UI", 10, "bold"),
            relief="flat", cursor="hand2",
            padx=12, pady=8,
            command=cmd
        )

    def _field_label(self, parent, text):
        lbl = tk.Label(
            parent, text=text,
            font=("Segoe UI", 9),
            bg=C_SURFACE, fg=C_TEXT_DIM, anchor="w"
        )
        lbl.pack(fill="x", pady=(10, 2))
        return lbl

    def _field_entry(self, parent, show=None):
        entry = tk.Entry(
            parent,
            font=("Segoe UI", 11),
            bg=C_INPUT_BG, fg=C_TEXT,
            insertbackground=C_TEXT,
            relief="flat",
            highlightbackground=C_BORDER,
            highlightcolor=C_ACCENT,
            highlightthickness=1,
        )
        if show:
            entry.config(show=show)
        entry.pack(fill="x", ipady=7)
        return entry

    def _set_error(self, msg):
        self.lbl_error.config(text=msg, fg=C_RED)

    def _set_success(self, msg):
        self.lbl_error.config(text=msg, fg=C_GREEN)

    # ------------------------------------------------------------------
    # Mode Switching
    # ------------------------------------------------------------------

    def _switch_login(self):
        self._mode = "login"
        self.btn_login_tab.config(bg=C_ACCENT,   fg="#0d1117")
        self.btn_signup_tab.config(bg=C_SURFACE,  fg=C_TEXT_DIM)
        self.lbl_confirm.pack_forget()
        self.entry_confirm.pack_forget()
        self.btn_action.config(text="Login")
        self._set_error("")

    def _switch_signup(self):
        self._mode = "signup"
        self.btn_signup_tab.config(bg=C_ACCENT,  fg="#0d1117")
        self.btn_login_tab.config(bg=C_SURFACE,   fg=C_TEXT_DIM)
        # Re-insert confirm widgets after the password entry
        self.lbl_confirm.pack(fill="x", pady=(10, 2))
        self.entry_confirm.pack(fill="x", ipady=7)
        # Keep error and button below
        self.lbl_error.pack_forget()
        self.btn_action.pack_forget()
        self.lbl_error.pack(pady=(6, 0))
        self.btn_action.pack(fill="x", pady=(18, 0))
        self.btn_action.config(text="Create Account")
        self._set_error("")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _on_action(self):
        self._set_error("")
        username = self.entry_user.get().strip()
        password = self.entry_pass.get()

        if not username or not password:
            self._set_error("Please fill in all fields.")
            return

        if self._mode == "login":
            user, err = auth.login(username, password)
            if err:
                self._set_error(err)
            else:
                self.on_login_success(user)

        else:  # signup
            confirm = self.entry_confirm.get()
            if password != confirm:
                self._set_error("Passwords do not match.")
                return
            user_id, err = auth.signup(username, password)
            if err:
                self._set_error(err)
            else:
                self._set_success("Account created! You can now log in.")
                self._switch_login()
                self.entry_user.delete(0, tk.END)
                self.entry_user.insert(0, username)
                self.entry_pass.delete(0, tk.END)
