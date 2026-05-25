# ============================================================
#  gui_admin.py — Admin Monitoring Dashboard
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
import db

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
C_PURPLE   = "#bc8cff"


class AdminFrame(tk.Frame):
    """Admin dashboard — shows all users and all activity logs."""

    def __init__(self, master, user: dict, on_logout):
        super().__init__(master, bg=C_BG)
        self.master    = master
        self.user      = user
        self.on_logout = on_logout
        self._all_logs = []

        self._apply_styles()
        self._build_ui()
        self._refresh_all()

    # ================================================================
    # Styles
    # ================================================================

    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=C_SURFACE,
                        fieldbackground=C_SURFACE,
                        foreground=C_TEXT,
                        rowheight=26,
                        font=("Segoe UI", 9))
        style.configure("Treeview.Heading",
                        background=C_SURFACE2,
                        foreground=C_TEXT_DIM,
                        font=("Segoe UI", 9, "bold"),
                        relief="flat")
        style.map("Treeview",
                  background=[("selected", C_ACCENT)],
                  foreground=[("selected", "#0d1117")])

    # ================================================================
    # UI Build
    # ================================================================

    def _build_ui(self):
        self._build_topbar()

        # ── body ──────────────────────────────────────────────────
        body = tk.Frame(self, bg=C_BG)
        body.pack(fill="both", expand=True, padx=16, pady=(8, 16))
        body.columnconfigure(0, weight=1, minsize=220)
        body.columnconfigure(1, weight=4)
        body.rowconfigure(0, weight=1)

        left  = tk.Frame(body, bg=C_BG)
        right = tk.Frame(body, bg=C_BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right.grid(row=0, column=1, sticky="nsew")

        self._build_left(left)
        self._build_right(right)

    # ── Top bar ───────────────────────────────────────────────────
    def _build_topbar(self):
        bar = tk.Frame(self, bg="#010409", pady=10)
        bar.pack(fill="x")

        tk.Label(bar, text="🛡️  SecureVault — Admin Dashboard",
                 font=("Segoe UI", 14, "bold"),
                 bg="#010409", fg=C_PURPLE).pack(side="left", padx=16)

        right_bar = tk.Frame(bar, bg="#010409")
        right_bar.pack(side="right", padx=16)

        tk.Button(right_bar, text="⟳  Refresh All",
                  font=("Segoe UI", 9),
                  bg=C_SURFACE, fg=C_ACCENT,
                  activebackground=C_BORDER, activeforeground=C_TEXT,
                  relief="flat", cursor="hand2", padx=12, pady=4,
                  command=self._refresh_all).pack(side="left", padx=(0, 10))

        tk.Label(right_bar,
                 text=f"🔑  {self.user['username']}  [Admin]",
                 font=("Segoe UI", 10, "bold"),
                 bg="#010409", fg=C_PURPLE).pack(side="left", padx=(0, 14))

        tk.Button(right_bar, text="Logout",
                  font=("Segoe UI", 9),
                  bg=C_SURFACE, fg=C_TEXT_DIM,
                  activebackground=C_RED, activeforeground=C_TEXT,
                  relief="flat", cursor="hand2", padx=12, pady=4,
                  command=self.on_logout).pack(side="left")

    # ── Left: Registered Users ────────────────────────────────────
    def _build_left(self, parent):
        # Title
        hdr = tk.Frame(parent, bg=C_BG)
        hdr.pack(fill="x", pady=(0, 6))
        tk.Label(hdr, text="👥  Registered Users",
                 font=("Segoe UI", 10, "bold"),
                 bg=C_BG, fg=C_TEXT).pack(side="left")

        # Stats label
        self.lbl_user_count = tk.Label(
            hdr, text="",
            font=("Segoe UI", 9),
            bg=C_BG, fg=C_TEXT_DIM
        )
        self.lbl_user_count.pack(side="right")

        # Users treeview
        card = tk.Frame(parent, bg=C_SURFACE,
                        highlightbackground=C_BORDER,
                        highlightthickness=1)
        card.pack(fill="both", expand=True)

        cols = ("Username", "Role", "Status", "Joined")
        self.user_tree = ttk.Treeview(card, columns=cols, show="headings")
        self.user_tree.heading("Username", text="Username")
        self.user_tree.heading("Role",     text="Role")
        self.user_tree.heading("Status",   text="Status")
        self.user_tree.heading("Joined",   text="Joined")
        self.user_tree.column("Username", width=95,  anchor="w")
        self.user_tree.column("Role",     width=50,  anchor="center")
        self.user_tree.column("Status",   width=70,  anchor="center")
        self.user_tree.column("Joined",   width=85,  anchor="center")

        vsb = ttk.Scrollbar(card, orient="vertical", command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=vsb.set)
        self.user_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.user_tree.bind("<<TreeviewSelect>>", self._on_user_select)

        # Style tag colors for statuses
        self.user_tree.tag_configure("pending",  foreground=C_YELLOW)
        self.user_tree.tag_configure("approved", foreground=C_GREEN)
        self.user_tree.tag_configure("rejected", foreground=C_RED)

        # Filter hint
        tk.Label(parent,
                 text="Click a user to filter logs",
                 font=("Segoe UI", 8, "italic"),
                 bg=C_BG, fg=C_TEXT_DIM).pack(anchor="w", pady=(6, 0))

        # Bottom actions row 1 (Logs / Delete)
        actions_row1 = tk.Frame(parent, bg=C_BG)
        actions_row1.pack(fill="x", pady=(4, 0))

        tk.Button(actions_row1, text="Show All Logs",
                  font=("Segoe UI", 9),
                  bg=C_SURFACE, fg=C_TEXT_DIM,
                  activebackground=C_BORDER, activeforeground=C_TEXT,
                  relief="flat", cursor="hand2", padx=8, pady=4,
                  command=self._show_all_logs).pack(side="left", padx=(0, 6))

        tk.Button(actions_row1, text="✕  Delete User",
                  font=("Segoe UI", 9, "bold"),
                  bg=C_RED, fg=C_TEXT,
                  activebackground=C_BORDER, activeforeground=C_TEXT,
                  relief="flat", cursor="hand2", padx=8, pady=4,
                  command=self._delete_user).pack(side="left")

        # Bottom actions row 2 (Approve / Reject)
        self.actions_row2 = tk.Frame(parent, bg=C_BG)
        self.actions_row2.pack(fill="x", pady=(6, 0))

        tk.Button(self.actions_row2, text="✔  Approve User",
                  font=("Segoe UI", 9, "bold"),
                  bg=C_GREEN, fg="#0d1117",
                  activebackground=C_BORDER, activeforeground=C_TEXT,
                  relief="flat", cursor="hand2", padx=8, pady=4,
                  command=self._approve_user).pack(side="left", padx=(0, 6))

        tk.Button(self.actions_row2, text="✕  Reject User",
                  font=("Segoe UI", 9, "bold"),
                  bg=C_YELLOW, fg="#0d1117",
                  activebackground=C_BORDER, activeforeground=C_TEXT,
                  relief="flat", cursor="hand2", padx=8, pady=4,
                  command=self._reject_user).pack(side="left")

    # ── Right: Activity Logs ───────────────────────────────────────
    def _build_right(self, parent):
        # Title + filter bar
        hdr = tk.Frame(parent, bg=C_BG)
        hdr.pack(fill="x", pady=(0, 6))
        tk.Label(hdr, text="📋  Activity Logs",
                 font=("Segoe UI", 10, "bold"),
                 bg=C_BG, fg=C_TEXT).pack(side="left")

        self.lbl_log_count = tk.Label(
            hdr, text="",
            font=("Segoe UI", 9),
            bg=C_BG, fg=C_TEXT_DIM
        )
        self.lbl_log_count.pack(side="left", padx=10)

        # Action filter
        filter_frame = tk.Frame(parent, bg=C_BG)
        filter_frame.pack(fill="x", pady=(0, 6))

        tk.Label(filter_frame, text="Filter by action:",
                 font=("Segoe UI", 9),
                 bg=C_BG, fg=C_TEXT_DIM).pack(side="left", padx=(0, 8))

        self.filter_var = tk.StringVar(value="All")
        for val in ("All", "ENCRYPT", "DECRYPT"):
            tk.Radiobutton(
                filter_frame, text=val,
                variable=self.filter_var, value=val,
                bg=C_BG, fg=C_TEXT,
                selectcolor=C_BG,
                activebackground=C_BG,
                activeforeground=C_ACCENT,
                font=("Segoe UI", 9),
                cursor="hand2",
                command=self._apply_filter
            ).pack(side="left", padx=6)

        tk.Label(filter_frame, text="  Search:",
                 font=("Segoe UI", 9),
                 bg=C_BG, fg=C_TEXT_DIM).pack(side="left")

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            filter_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 9),
            bg=C_SURFACE, fg=C_TEXT,
            insertbackground=C_TEXT,
            relief="flat",
            highlightbackground=C_BORDER,
            highlightcolor=C_ACCENT,
            highlightthickness=1,
            width=20
        )
        search_entry.pack(side="left", padx=6, ipady=4)
        self.search_var.trace_add("write", lambda *_: self._apply_filter())

        # Logs treeview
        card = tk.Frame(parent, bg=C_SURFACE,
                        highlightbackground=C_BORDER,
                        highlightthickness=1)
        card.pack(fill="both", expand=True)

        cols = ("ID", "User", "Action", "Algorithm", "Source File", "Output File", "Status", "Timestamp")
        self.log_tree = ttk.Treeview(card, columns=cols, show="headings")

        widths = {"ID": 45, "User": 110, "Action": 80, "Algorithm": 90,
                  "Source File": 180, "Output File": 180, "Status": 75, "Timestamp": 145}
        anchors = {"ID": "center", "Action": "center", "Algorithm": "center",
                   "Status": "center", "Timestamp": "center"}

        for c in cols:
            self.log_tree.heading(c, text=c,
                                  command=lambda col=c: self._sort_by(col))
            self.log_tree.column(c,
                                 width=widths.get(c, 100),
                                 anchor=anchors.get(c, "w"))

        vsb = ttk.Scrollbar(card, orient="vertical",   command=self.log_tree.yview)
        hsb = ttk.Scrollbar(card, orient="horizontal", command=self.log_tree.xview)
        self.log_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.log_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right",  fill="y")
        hsb.pack(side="bottom", fill="x")

        # Tag colours
        self.log_tree.tag_configure("encrypt", foreground=C_ACCENT)
        self.log_tree.tag_configure("decrypt", foreground=C_GREEN)
        self.log_tree.tag_configure("failed",  foreground=C_RED)

        # Stats bar
        self.lbl_stats = tk.Label(
            parent, text="",
            font=("Segoe UI", 9),
            bg=C_BG, fg=C_TEXT_DIM
        )
        self.lbl_stats.pack(anchor="w", pady=(6, 0))

    # ================================================================
    # Data Loading
    # ================================================================

    def _refresh_all(self):
        # Save selection
        sel = self.user_tree.selection()
        selected_id = sel[0] if sel else None

        self._refresh_users(selected_id)
        self._all_logs = db.get_all_activity_logs()

        if selected_id and self.user_tree.exists(selected_id):
            self._on_user_select()
        else:
            self._render_logs(self._all_logs)
            self.actions_row2.pack_forget()

    def _refresh_users(self, selected_id=None):
        for row in self.user_tree.get_children():
            self.user_tree.delete(row)
        users = db.get_all_users()
        for u in users:
            joined = str(u['created_at'])[:10]
            self.user_tree.insert("", tk.END, iid=str(u['id']),
                                  values=(u['username'], u['role'], u['status'], joined),
                                  tags=(u['status'],))
        self.lbl_user_count.config(text=f"({len(users)} users)")

        if selected_id and self.user_tree.exists(selected_id):
            self.user_tree.selection_set(selected_id)
            self.user_tree.focus(selected_id)

    # ================================================================
    # Log Rendering
    # ================================================================

    def _render_logs(self, logs):
        for row in self.log_tree.get_children():
            self.log_tree.delete(row)

        encrypt_count = decrypt_count = fail_count = 0

        for log in logs:
            action = log['action'].upper()
            status = log['status']
            ts     = str(log['timestamp'])[:19]

            if status == "failed":
                tag = "failed"
                fail_count += 1
            elif action == "ENCRYPT":
                tag = "encrypt"
                encrypt_count += 1
            else:
                tag = "decrypt"
                decrypt_count += 1

            self.log_tree.insert("", tk.END, values=(
                log['id'],
                log['username'],
                action,
                log['algorithm'],
                log['source_file'] or "",
                log['output_file'] or "",
                status,
                ts
            ), tags=(tag,))

        total = len(logs)
        self.lbl_log_count.config(text=f"({total} entries)")
        self.lbl_stats.config(
            text=(f"Total: {total}  |  "
                  f"Encryptions: {encrypt_count}  |  "
                  f"Decryptions: {decrypt_count}  |  "
                  f"Failed: {fail_count}")
        )

    # ================================================================
    # Filtering / Sorting
    # ================================================================

    def _apply_filter(self, *_):
        action_filter = self.filter_var.get()
        search_term   = self.search_var.get().lower().strip()

        filtered = []
        for log in self._all_logs:
            action = log['action'].upper()
            # Action filter
            if action_filter != "All" and action != action_filter:
                continue
            # Search filter (username, algorithm, file paths)
            if search_term:
                haystack = (
                    f"{log['username']} {log['algorithm']} "
                    f"{log['source_file'] or ''} {log['output_file'] or ''}"
                ).lower()
                if search_term not in haystack:
                    continue
            filtered.append(log)

        self._render_logs(filtered)

    def _on_user_select(self, _event=None):
        sel = self.user_tree.selection()
        if not sel:
            self.actions_row2.pack_forget()
            return
        user_id  = int(sel[0])
        username = self.user_tree.item(sel[0], "values")[0]
        status   = self.user_tree.item(sel[0], "values")[2]

        # Hide approve/reject controls unless user is pending
        if status == 'pending':
            self.actions_row2.pack(fill="x", pady=(6, 0))
        else:
            self.actions_row2.pack_forget()

        # Filter global log list by this user
        user_logs = [lg for lg in self._all_logs if lg['username'] == username]
        self._render_logs(user_logs)
        self.filter_var.set("All")
        self.search_var.set("")
        self.lbl_log_count.config(text=f"(filtered: {username})")

    def _show_all_logs(self):
        self.user_tree.selection_remove(self.user_tree.selection())
        self.filter_var.set("All")
        self.search_var.set("")
        self._render_logs(self._all_logs)
        self.actions_row2.pack_forget()

    def _delete_user(self):
        sel = self.user_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a user to delete.", parent=self)
            return
        user_id = int(sel[0])
        username = self.user_tree.item(sel[0], "values")[0]

        if not messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to permanently delete the user '{username}'?\n\n"
            f"This will delete their account, all saved keys, and all their activity logs. "
            f"This action cannot be undone.",
            parent=self
        ):
            return

        try:
            db.delete_user(user_id)
            messagebox.showinfo("Success", f"User '{username}' was deleted successfully.", parent=self)
            self._refresh_all()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete user: {e}", parent=self)

    def _approve_user(self):
        sel = self.user_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a user to approve.", parent=self)
            return
        user_id = int(sel[0])
        username = self.user_tree.item(sel[0], "values")[0]
        status = self.user_tree.item(sel[0], "values")[2]

        if status == 'approved':
            messagebox.showinfo("Already Approved", f"User '{username}' is already approved.", parent=self)
            return

        try:
            db.approve_user(user_id)
            messagebox.showinfo("Success", f"User '{username}' has been approved.", parent=self)
            self._refresh_all()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to approve user: {e}", parent=self)

    def _reject_user(self):
        sel = self.user_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a user to reject.", parent=self)
            return
        user_id = int(sel[0])
        username = self.user_tree.item(sel[0], "values")[0]
        status = self.user_tree.item(sel[0], "values")[2]

        if status == 'rejected':
            messagebox.showinfo("Already Rejected", f"User '{username}' is already rejected.", parent=self)
            return

        if not messagebox.askyesno(
            "Confirm Reject",
            f"Are you sure you want to reject user '{username}'?\n"
            f"They will no longer be able to log in to the system.",
            parent=self
        ):
            return

        try:
            db.reject_user(user_id)
            messagebox.showinfo("Success", f"User '{username}' has been rejected.", parent=self)
            self._refresh_all()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reject user: {e}", parent=self)

    def _sort_by(self, col):
        """Toggle sort on column header click."""
        items = [(self.log_tree.set(child, col), child)
                 for child in self.log_tree.get_children("")]
        reverse = getattr(self, f"_sort_rev_{col}", False)
        items.sort(reverse=reverse)
        for idx, (_, child) in enumerate(items):
            self.log_tree.move(child, "", idx)
        setattr(self, f"_sort_rev_{col}", not reverse)
