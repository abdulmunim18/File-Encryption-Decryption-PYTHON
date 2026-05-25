# ============================================================
#  gui_main.py — Encryptor GUI for Regular Users
# ============================================================

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import db
from encryptor import Encryptor

# ── Colour palette ────────────────────────────────────────────────
C_BG       = "#0d1117"
C_SURFACE  = "#161b22"
C_SURFACE2 = "#1c2128"
C_BORDER   = "#30363d"
C_ACCENT   = "#58a6ff"
C_GREEN    = "#3fb950"
C_RED      = "#f85149"
C_YELLOW   = "#d29922"
C_TEXT     = "#f0f6fc"
C_TEXT_DIM = "#8b949e"

ALGORITHMS = ['AES', 'DES', '3DES', 'Blowfish', 'ChaCha20', 'RC4', 'CAST']


class MainFrame(tk.Frame):
    """Main encryptor/decryptor interface shown after user login."""

    def __init__(self, master, user: dict, on_logout):
        super().__init__(master, bg=C_BG)
        self.master      = master
        self.user        = user          # {'id', 'username', 'role', ...}
        self.on_logout   = on_logout
        self.current_key      = None    # bytes
        self.current_key_id   = None    # int (DB row id)
        self.current_key_name = None    # str
        self.current_key_algo = None    # str

        # Ensure the user's private output directory exists
        self.user_dir = os.path.join("user_files", user['username'])
        os.makedirs(self.user_dir, exist_ok=True)

        self._build_ui()
        self._refresh_keys()
        self._refresh_logs()

    # ================================================================
    # UI BUILD
    # ================================================================

    def _build_ui(self):
        self._build_topbar()

        # ── two-column layout ─────────────────────────────────────
        body = tk.Frame(self, bg=C_BG)
        body.pack(fill="both", expand=True, padx=16, pady=(8, 16))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        left  = tk.Frame(body, bg=C_BG)
        right = tk.Frame(body, bg=C_BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        right.grid(row=0, column=1, sticky="nsew")

        self._build_left(left)
        self._build_right(right)

    # ── Top bar ───────────────────────────────────────────────────
    def _build_topbar(self):
        bar = tk.Frame(self, bg="#010409", pady=10)
        bar.pack(fill="x")

        tk.Label(bar, text="🔐 SecureVault",
                 font=("Segoe UI", 14, "bold"),
                 bg="#010409", fg=C_ACCENT).pack(side="left", padx=16)

        tk.Label(bar, text="File Encryptor / Decryptor",
                 font=("Segoe UI", 9),
                 bg="#010409", fg=C_TEXT_DIM).pack(side="left")

        # right side
        right_bar = tk.Frame(bar, bg="#010409")
        right_bar.pack(side="right", padx=16)

        tk.Label(right_bar,
                 text=f"👤  {self.user['username']}",
                 font=("Segoe UI", 10, "bold"),
                 bg="#010409", fg=C_TEXT).pack(side="left", padx=(0, 16))

        tk.Button(right_bar, text="Logout",
                  font=("Segoe UI", 9),
                  bg=C_SURFACE, fg=C_TEXT_DIM,
                  activebackground=C_RED, activeforeground=C_TEXT,
                  relief="flat", cursor="hand2", padx=12, pady=4,
                  command=self._do_logout).pack(side="left")

    # ── Left column ───────────────────────────────────────────────
    def _build_left(self, parent):
        # Algorithm selection
        sec1 = self._section(parent, "⚙️  Algorithm")
        self.algo_var = tk.StringVar(value='AES')
        row = tk.Frame(sec1, bg=C_SURFACE)
        row.pack(fill="x")
        for alg in ALGORITHMS:
            rb = tk.Radiobutton(
                row, text=alg,
                variable=self.algo_var, value=alg,
                bg=C_SURFACE, fg=C_TEXT,
                selectcolor=C_BG,
                activebackground=C_SURFACE,
                activeforeground=C_ACCENT,
                font=("Segoe UI", 9),
                cursor="hand2"
            )
            rb.pack(side="left", padx=4, pady=4)

        # Key management
        sec2 = self._section(parent, "🗝️  Key Management")

        # Key list
        lbl_frame = tk.Frame(sec2, bg=C_SURFACE)
        lbl_frame.pack(fill="x", pady=(0, 6))
        tk.Label(lbl_frame, text="Saved Keys:",
                 font=("Segoe UI", 9), bg=C_SURFACE, fg=C_TEXT_DIM).pack(side="left")
        tk.Button(lbl_frame, text="⟳ Refresh",
                  font=("Segoe UI", 8), bg=C_SURFACE, fg=C_TEXT_DIM,
                  relief="flat", cursor="hand2",
                  command=self._refresh_keys).pack(side="right")

        list_frame = tk.Frame(sec2, bg=C_BORDER, pady=1, padx=1)
        list_frame.pack(fill="x")
        inner = tk.Frame(list_frame, bg=C_BG)
        inner.pack(fill="both")

        scrollbar = tk.Scrollbar(inner, orient="vertical", bg=C_BG)
        self.key_listbox = tk.Listbox(
            inner,
            bg=C_BG, fg=C_TEXT,
            selectbackground=C_ACCENT, selectforeground="#0d1117",
            font=("Segoe UI", 9),
            height=5, relief="flat",
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.key_listbox.yview)
        self.key_listbox.pack(side="left", fill="both", expand=True, padx=6, pady=4)
        scrollbar.pack(side="right", fill="y")

        self.key_listbox.bind("<<ListboxSelect>>", self._on_key_select)

        # Current key status
        self.lbl_key_status = tk.Label(
            sec2, text="No key selected",
            font=("Segoe UI", 9, "italic"),
            bg=C_SURFACE, fg=C_TEXT_DIM
        )
        self.lbl_key_status.pack(anchor="w", pady=(4, 8))

        # Key buttons
        key_btn_row = tk.Frame(sec2, bg=C_SURFACE)
        key_btn_row.pack(fill="x")
        self._btn(key_btn_row, "＋ Create Key", C_GREEN,    "#0d1117", self._create_key).pack(side="left", padx=(0, 6))
        self._btn(key_btn_row, "✕  Delete Key", C_RED,     C_TEXT,    self._delete_key).pack(side="left")

        # File selection
        sec3 = self._section(parent, "📁  File Selection")

        tk.Label(sec3, text="Source File:", font=("Segoe UI", 9),
                 bg=C_SURFACE, fg=C_TEXT_DIM).pack(anchor="w")
        src_row = tk.Frame(sec3, bg=C_SURFACE)
        src_row.pack(fill="x", pady=(2, 8))
        self.entry_src = self._entry(src_row)
        self.entry_src.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._btn(src_row, "Browse", C_SURFACE2, C_ACCENT, self._browse_src).pack(side="left")

        tk.Label(sec3, text="Output File:", font=("Segoe UI", 9),
                 bg=C_SURFACE, fg=C_TEXT_DIM).pack(anchor="w")
        dst_row = tk.Frame(sec3, bg=C_SURFACE)
        dst_row.pack(fill="x", pady=(2, 0))
        self.entry_dst = self._entry(dst_row)
        self.entry_dst.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self._btn(dst_row, "Browse", C_SURFACE2, C_ACCENT, self._browse_dst).pack(side="left")

        # Action buttons
        sec4 = self._section(parent, "⚡  Actions")
        action_row = tk.Frame(sec4, bg=C_SURFACE)
        action_row.pack(fill="x")
        self._btn(action_row, "🔒  Encrypt", C_ACCENT, "#0d1117", self._do_encrypt, width=14).pack(side="left", padx=(0, 10))
        self._btn(action_row, "🔓  Decrypt", C_GREEN,  "#0d1117", self._do_decrypt, width=14).pack(side="left")

        # Status bar
        self.lbl_status = tk.Label(
            parent, text="",
            font=("Segoe UI", 9),
            bg=C_BG, fg=C_TEXT_DIM,
            wraplength=500, justify="left"
        )
        self.lbl_status.pack(anchor="w", pady=(10, 0))

    # ── Right column: Activity Log ─────────────────────────────────
    def _build_right(self, parent):
        sec = self._section(parent, "📋  My Activity Log")

        hdr_row = tk.Frame(sec, bg=C_SURFACE)
        hdr_row.pack(fill="x", pady=(0, 6))
        tk.Button(hdr_row, text="⟳ Refresh",
                  font=("Segoe UI", 8), bg=C_SURFACE, fg=C_TEXT_DIM,
                  relief="flat", cursor="hand2",
                  command=self._refresh_logs).pack(side="right")

        cols = ("Action", "Algorithm", "File", "Status", "Time")
        self.log_tree = ttk.Treeview(sec, columns=cols, show="headings", height=20)
        self._style_tree(self.log_tree)
        self.log_tree.heading("Action",    text="Action")
        self.log_tree.heading("Algorithm", text="Algorithm")
        self.log_tree.heading("File",      text="Output File")
        self.log_tree.heading("Status",    text="Status")
        self.log_tree.heading("Time",      text="Timestamp")
        self.log_tree.column("Action",    width=70,  anchor="center")
        self.log_tree.column("Algorithm", width=80,  anchor="center")
        self.log_tree.column("File",      width=160, anchor="w")
        self.log_tree.column("Status",    width=70,  anchor="center")
        self.log_tree.column("Time",      width=140, anchor="center")

        vsb = ttk.Scrollbar(sec, orient="vertical",   command=self.log_tree.yview)
        hsb = ttk.Scrollbar(sec, orient="horizontal", command=self.log_tree.xview)
        self.log_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.log_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right",  fill="y")
        hsb.pack(side="bottom", fill="x")

    # ================================================================
    # Helper Widgets
    # ================================================================

    def _section(self, parent, title):
        outer = tk.Frame(parent, bg=C_BG, pady=6)
        outer.pack(fill="x")
        tk.Label(outer, text=title,
                 font=("Segoe UI", 10, "bold"),
                 bg=C_BG, fg=C_TEXT).pack(anchor="w", pady=(0, 4))
        card = tk.Frame(outer, bg=C_SURFACE,
                        highlightbackground=C_BORDER,
                        highlightthickness=1,
                        padx=12, pady=10)
        card.pack(fill="x")
        return card

    def _btn(self, parent, text, bg, fg, cmd, width=None):
        kw = dict(font=("Segoe UI", 9, "bold"),
                  bg=bg, fg=fg,
                  activebackground=C_BORDER, activeforeground=C_TEXT,
                  relief="flat", cursor="hand2", padx=10, pady=6,
                  command=cmd)
        if width:
            kw['width'] = width
        return tk.Button(parent, text=text, **kw)

    def _entry(self, parent):
        return tk.Entry(
            parent,
            font=("Segoe UI", 9),
            bg=C_INPUT_BG if hasattr(self, '_') else C_BG,
            fg=C_TEXT,
            insertbackground=C_TEXT,
            relief="flat",
            highlightbackground=C_BORDER,
            highlightcolor=C_ACCENT,
            highlightthickness=1
        )

    def _style_tree(self, tree):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=C_SURFACE,
                        fieldbackground=C_SURFACE,
                        foreground=C_TEXT,
                        rowheight=24,
                        font=("Segoe UI", 9))
        style.configure("Treeview.Heading",
                        background=C_SURFACE2,
                        foreground=C_TEXT_DIM,
                        font=("Segoe UI", 9, "bold"),
                        relief="flat")
        style.map("Treeview",
                  background=[("selected", C_ACCENT)],
                  foreground=[("selected", "#0d1117")])

    def _set_status(self, msg, color=C_TEXT_DIM):
        self.lbl_status.config(text=msg, fg=color)

    # ================================================================
    # Key Management
    # ================================================================

    def _refresh_keys(self):
        self.keys_data = db.get_user_keys(self.user['id'])
        self.key_listbox.delete(0, tk.END)
        for k in self.keys_data:
            ts = str(k['created_at'])[:16]
            self.key_listbox.insert(tk.END, f"  {k['key_name']}  [{k['algorithm']}]  —  {ts}")

    def _on_key_select(self, _event=None):
        sel = self.key_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        k = self.keys_data[idx]
        self.current_key      = k['key_data']
        self.current_key_id   = k['id']
        self.current_key_name = k['key_name']
        self.current_key_algo = k['algorithm']
        # Auto-select matching algorithm
        self.algo_var.set(k['algorithm'])
        self.lbl_key_status.config(
            text=f"✔  Using: {k['key_name']}  ({k['algorithm']})",
            fg=C_GREEN
        )

    def _create_key(self):
        name = simpledialog.askstring(
            "Key Name",
            "Enter a name for this key:",
            parent=self
        )
        if not name or not name.strip():
            return
        name = name.strip()
        algorithm = self.algo_var.get()
        enc = Encryptor(algorithm)
        key_bytes = enc.generate_key()
        key_id = db.save_key(self.user['id'], name, algorithm, key_bytes)
        self._refresh_keys()
        # Auto-select the new key
        self.current_key      = key_bytes
        self.current_key_id   = key_id
        self.current_key_name = name
        self.current_key_algo = algorithm
        self.lbl_key_status.config(
            text=f"✔  Using: {name}  ({algorithm})",
            fg=C_GREEN
        )
        # Highlight it in the listbox
        self.key_listbox.selection_clear(0, tk.END)
        self.key_listbox.selection_set(0)
        self._set_status(f"Key '{name}' created and saved to database.", C_GREEN)

    def _delete_key(self):
        sel = self.key_listbox.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a key to delete.", parent=self)
            return
        idx = sel[0]
        k   = self.keys_data[idx]
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Delete key '{k['key_name']}'?\nFiles encrypted with this key will no longer be decryptable.",
            parent=self
        ):
            return
        db.delete_key(k['id'], self.user['id'])
        if self.current_key_id == k['id']:
            self.current_key      = None
            self.current_key_id   = None
            self.current_key_name = None
            self.current_key_algo = None
            self.lbl_key_status.config(text="No key selected", fg=C_TEXT_DIM)
        self._refresh_keys()
        self._set_status(f"Key '{k['key_name']}' deleted.", C_YELLOW)

    # ================================================================
    # File Browsing
    # ================================================================

    def _browse_src(self):
        path = filedialog.askopenfilename(parent=self)
        if path:
            self.entry_src.delete(0, tk.END)
            self.entry_src.insert(0, path)

    def _browse_dst(self):
        init = os.path.abspath(self.user_dir)
        path = filedialog.asksaveasfilename(parent=self, initialdir=init)
        if path:
            self.entry_dst.delete(0, tk.END)
            self.entry_dst.insert(0, path)

    # ================================================================
    # Encrypt / Decrypt
    # ================================================================

    def _validate(self):
        if not self.current_key:
            messagebox.showerror("No Key", "Please select or create an encryption key first.", parent=self)
            return False
        if not self.entry_src.get().strip():
            messagebox.showerror("No Source", "Please select a source file.", parent=self)
            return False
        if not self.entry_dst.get().strip():
            messagebox.showerror("No Output", "Please specify an output file path.", parent=self)
            return False
        return True

    def _do_encrypt(self):
        if not self._validate():
            return
        algorithm   = self.current_key_algo
        self.algo_var.set(algorithm)
        src         = self.entry_src.get().strip()
        dst         = self.entry_dst.get().strip()
        status      = "success"
        try:
            Encryptor(algorithm).file_encrypt(self.current_key, src, dst)
            self._set_status(f"✔  File encrypted → {dst}", C_GREEN)
        except Exception as e:
            status = "failed"
            self._set_status(f"✘  Encryption failed: {e}", C_RED)
            messagebox.showerror("Encryption Error", str(e), parent=self)
        finally:
            db.log_activity(
                self.user['id'], 'encrypt', algorithm,
                self.current_key_id, src, dst, status
            )
            self._refresh_logs()

    def _do_decrypt(self):
        if not self._validate():
            return
        algorithm   = self.current_key_algo
        self.algo_var.set(algorithm)
        src         = self.entry_src.get().strip()
        dst         = self.entry_dst.get().strip()
        status      = "success"
        try:
            Encryptor(algorithm).file_decrypt(self.current_key, src, dst)
            self._set_status(f"✔  File decrypted → {dst}", C_GREEN)
        except Exception as e:
            status = "failed"
            self._set_status(f"✘  Decryption failed: {e}", C_RED)
            messagebox.showerror("Decryption Error", str(e), parent=self)
        finally:
            db.log_activity(
                self.user['id'], 'decrypt', algorithm,
                self.current_key_id, src, dst, status
            )
            self._refresh_logs()

    # ================================================================
    # Activity Log
    # ================================================================

    def _refresh_logs(self):
        for row in self.log_tree.get_children():
            self.log_tree.delete(row)
        logs = db.get_user_activity_logs(self.user['id'])
        for log in logs:
            tag = "ok" if log['status'] == 'success' else "fail"
            out = os.path.basename(log['output_file']) if log['output_file'] else ""
            ts  = str(log['timestamp'])[:19]
            self.log_tree.insert("", tk.END, values=(
                log['action'].upper(), log['algorithm'], out, log['status'], ts
            ), tags=(tag,))
        self.log_tree.tag_configure("ok",   foreground=C_GREEN)
        self.log_tree.tag_configure("fail", foreground=C_RED)

    # ================================================================
    # Logout
    # ================================================================

    def _do_logout(self):
        self.on_logout()
