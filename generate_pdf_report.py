# ============================================================
#  generate_pdf_report.py — Python PDF Report Generator
#  Run this script to compile the PDF report.
# ============================================================

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to draw header, footer, and 'Page X of Y' page numbering.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Colors
        c_slate = colors.HexColor("#475569")
        c_border = colors.HexColor("#E2E8F0")
        
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(c_slate)
        
        # Header (Only on pages > 1 for clean look, or on all pages)
        self.drawString(54, 752, "SECUREVAULT — PROJECT TECHNICAL REPORT")
        self.setFont("Helvetica", 8)
        self.drawRightString(612 - 54, 752, "ACADEMIC COURSEWORK")
        
        # Header Line
        self.setStrokeColor(c_border)
        self.setLineWidth(0.75)
        self.line(54, 744, 612 - 54, 744)
        
        # Footer Line
        self.line(54, 52, 612 - 54, 52)
        
        # Footer
        self.drawString(54, 38, "Confidential — Information Security Laboratory")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 38, page_text)
        
        self.restoreState()


def build_pdf(filename="securevault_project_report.pdf"):
    # Target file path
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#0F172A") # Deep Slate Navy
    c_secondary = colors.HexColor("#0F766E") # Dark Teal
    c_text = colors.HexColor("#334155") # Charcoal
    c_bg_light = colors.HexColor("#F8FAFC") # Off-white/slate
    
    # Custom Paragraph Styles
    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_primary,
        spaceAfter=6
    )
    
    style_subtitle = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceAfter=24
    )
    
    style_h1 = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    style_body = ParagraphStyle(
        'BodyCharcoal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=c_text,
        spaceAfter=10
    )
    
    style_bullet = ParagraphStyle(
        'BulletCharcoal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_text,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=6
    )

    style_table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=c_text
    )

    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    story = []

    # Title & Subtitle
    story.append(Spacer(1, 15))
    story.append(Paragraph("SecureVault: Technical Report", style_title))
    story.append(Paragraph("A Multi-User File Encryption & Decryption System", style_subtitle))
    story.append(Spacer(1, 10))

    # 1. Introduction
    story.append(Paragraph("1. Introduction", style_h1))
    intro_p1 = (
        "In the contemporary digital landscape, securing files against unauthorized access is paramount. "
        "SecureVault is an advanced, multi-user desktop application designed to encrypt and decrypt sensitive files "
        "using a suite of industry-standard symmetric cryptographic algorithms. By wrapping raw cryptographic primitives "
        "inside a structured user-access control layer and backing it with a centralized relational database, "
        "SecureVault delivers a secure, isolated workspace environment for individuals and organizations to manage "
        "data confidentiality and integrity."
    )
    story.append(Paragraph(intro_p1, style_body))

    # 2. System Solution
    story.append(Paragraph("2. System Solution", style_h1))
    sol_p1 = (
        "The system replaces vulnerable local file key management with a secure, centralized model. "
        "By integrating a PostgreSQL database, SecureVault introduces strict role-based authorization, "
        "verifiable administrative signup workflows, and isolated user data directory spaces. Key data is saved "
        "securely within the database's binary byte arrays, ensuring keys are protected against local file system loss "
        "and theft. All cryptographic operations are dynamically synchronized to the database to preserve full system audit logs."
    )
    story.append(Paragraph(sol_p1, style_body))

    # 3. Technologies Used
    story.append(Paragraph("3. Technologies Used", style_h1))
    tech_intro = "The SecureVault stack combines modern Python GUI frameworks, industry-standard cryptographic modules, and relational database management systems:"
    story.append(Paragraph(tech_intro, style_body))
    
    story.append(Paragraph("• <b>User Interface (GUI):</b> Python Tkinter styled with a premium dark-themed color palette for visual appeal and accessibility.", style_bullet))
    story.append(Paragraph("• <b>Database (RDBMS):</b> PostgreSQL database running locally on port 5432, maintaining referential integrity and data constraints.", style_bullet))
    story.append(Paragraph("• <b>Database Driver:</b> Psycopg2-binary, facilitating thread-safe connection pooling and parameterized SQL queries to prevent injection attacks.", style_bullet))
    story.append(Paragraph("• <b>Authentication Security:</b> Bcrypt library for password hashing, using unique salts to guard accounts against rainbow table attacks.", style_bullet))
    story.append(Paragraph("• <b>Cryptographic Core:</b> PyCryptodome library, driving robust implementations of AES, DES, 3DES, Blowfish, ChaCha20, RC4, and CAST.", style_bullet))

    story.append(Spacer(1, 10))

    # 4. What Our System Performs (Capabilities)
    story.append(Paragraph("4. What Our System Performs", style_h1))
    story.append(Paragraph("The system is designed with specialized functional modes and security features:", style_body))
    
    story.append(Paragraph("• <b>Secure Account Signup & Login:</b> Enforces strict input validation (e.g. minimum character lengths) and hashes passwords before writing them to the database.", style_bullet))
    story.append(Paragraph("• <b>Admin Registration Controls:</b> New accounts are stored as 'pending' and blocked from logging in. Admins review registrations and selectively approve or reject them. Once resolved, the system dynamically restricts option sets to show only deletion controls.", style_bullet))
    story.append(Paragraph("• <b>Centralized Encryption Key Manager:</b> Allows users to generate, view, and delete encryption keys directly inside the GUI, storing them as BYTEA elements in the DB rather than physical files.", style_bullet))
    story.append(Paragraph("• <b>Key-Algorithm Safeguard:</b> Automatically locks and enforces the correct cryptographic algorithm associated with a chosen key during encryption/decryption, avoiding runtime MAC-check errors.", style_bullet))
    story.append(Paragraph("• <b>Real-time Activity Auditing:</b> Automatically logs every encryption and decryption task, tracking file paths, algorithm selection, timestamps, and exit status (success/failure).", style_bullet))

    story.append(PageBreak()) # Clean break to keep diagrams on page 2

    # 5. System Diagrams (Architecture and Database Table Structure)
    story.append(Paragraph("5. System Diagrams & Structure", style_h1))
    story.append(Paragraph("The following structural tables show the system architecture design and relational PostgreSQL layout:", style_body))

    # Diagram Table 1: Architecture Layers
    story.append(Paragraph("<b>System Architectural Layers:</b>", style_body))
    arch_data = [
        [Paragraph("<b>Layer</b>", style_table_header), Paragraph("<b>Components & Files</b>", style_table_header), Paragraph("<b>Core Responsibilities</b>", style_table_header)],
        [
            Paragraph("Presentation (UI)", style_table_cell),
            Paragraph("main.py, gui_login.py,<br/>gui_main.py, gui_admin.py", style_table_cell),
            Paragraph("Renders dark-themed Tkinter screens; handles frame transitions, file browsing, and user actions.", style_table_cell)
        ],
        [
            Paragraph("Logic & Security", style_table_cell),
            Paragraph("auth.py, encryptor.py", style_table_cell),
            Paragraph("Executes Bcrypt hashing; generates random keys, pads blocks, and processes file encryption/decryption.", style_table_cell)
        ],
        [
            Paragraph("Database Connection", style_table_cell),
            Paragraph("db.py, db_config.py", style_table_cell),
            Paragraph("Manages PostgreSQL connection pooling, parameters, queries, user statuses, and activity log inserts.", style_table_cell)
        ],
        [
            Paragraph("Storage & Backend", style_table_cell),
            Paragraph("PostgreSQL Database,<br/>Local user_files/ directory", style_table_cell),
            Paragraph("Physically saves relational data (users, keys, logs) and isolates user files into private subdirectories.", style_table_cell)
        ]
    ]
    
    t_arch = Table(arch_data, colWidths=[1.1*inch, 2.1*inch, 3.8*inch])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,1), c_bg_light),
        ('BACKGROUND', (0,3), (-1,3), c_bg_light),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 15))

    # Diagram Table 2: Database Schema
    story.append(Paragraph("<b>PostgreSQL Relational Schema:</b>", style_body))
    db_data = [
        [Paragraph("<b>Table</b>", style_table_header), Paragraph("<b>Attributes</b>", style_table_header), Paragraph("<b>Relational Rules & Constraints</b>", style_table_header)],
        [
            Paragraph("users", style_table_cell),
            Paragraph("id (PK), username (Unique), password, role, status, created_at", style_table_cell),
            Paragraph("Stores Bcrypt-hashed user credentials. Account status defaults to 'pending' upon registration.", style_table_cell)
        ],
        [
            Paragraph("encryption_keys", style_table_cell),
            Paragraph("id (PK), user_id (FK), key_name, algorithm, key_data (BYTEA), created_at", style_table_cell),
            Paragraph("Links keys to a specific user. Cascade-delete removes keys if the owner account is deleted.", style_table_cell)
        ],
        [
            Paragraph("activity_logs", style_table_cell),
            Paragraph("id (PK), user_id (FK), action, algorithm, key_id (FK), source_file, output_file, status, timestamp", style_table_cell),
            Paragraph("Saves activity events. Foreign key rules automatically nullify keys or delete log chains on user purges.", style_table_cell)
        ]
    ]

    t_db = Table(db_data, colWidths=[1.3*inch, 2.2*inch, 3.5*inch])
    t_db.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,1), c_bg_light),
        ('BACKGROUND', (0,3), (-1,3), c_bg_light),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_db)
    story.append(Spacer(1, 15))

    # 6. Conclusion
    story.append(Paragraph("6. Conclusion", style_h1))
    conclusion_text = (
        "SecureVault represents a significant enhancement over single-user cryptographic tools. "
        "By wrapping industry-standard symmetric encryption algorithms inside a structured database access management "
        "layer, it provides robust confidentiality, user isolation, and auditability. The system provides a highly secure "
        "and reliable tool for safe file management, perfectly suited for academic and practical deployment."
    )
    story.append(Paragraph(conclusion_text, style_body))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] PDF Report successfully built as: {filename}")


if __name__ == "__main__":
    build_pdf()
