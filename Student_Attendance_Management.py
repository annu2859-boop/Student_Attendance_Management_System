#!/usr/bin/env python
# coding: utf-8

# In[1]:


import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import date, datetime,timedelta
import calendar


#================ DATABASE CONNECTION =================

con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="YOUR_MYSQL_PASSWORD",
    database="projects"
)

cur = con.cursor()


#================ MAIN WINDOW =========================

root = tk.Tk()
root.title("Student Attendance Management System")
root.geometry("1150x720")
root.minsize(950, 600)
root.configure(bg="#f3f5f9")


#================ COLORS ==============================

BLUE = "#244b83"
DARK = "#172b4d"
BG = "#f3f5f9"
WHITE = "#ffffff"
GREEN = "#198754"
RED = "#dc3545"


#================ COMMON FUNCTIONS ====================

def clear_screen():
    for widget in content.winfo_children():
        widget.destroy()


def heading(title):
    clear_screen()

    tk.Label(
        content,
        text=title,
        font=("Arial", 22, "bold"),
        bg=BG,
        fg=DARK
    ).pack(anchor="w", pady=(5, 20))


def make_entry(parent, label, default=""):
    tk.Label(
        parent,
        text=label,
        font=("Arial", 11),
        bg=WHITE,
        fg=DARK
    ).pack(anchor="w", padx=15, pady=(10, 3))

    entry = tk.Entry(
        parent,
        font=("Arial", 12),
        width=35,
        relief="solid",
        bd=1
    )
    entry.pack(anchor="w", padx=15, pady=3)

    if default:
        entry.insert(0, default)

    return entry


def make_table(parent, columns, headings):
    frame = tk.Frame(parent, bg=WHITE)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    table = ttk.Treeview(
        frame,
        columns=columns,
        show="headings"
    )

    for col, title in zip(columns, headings):
        table.heading(col, text=title)
        table.column(col, width=125, anchor="center")

    scrollbar = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=table.yview
    )

    table.configure(yscrollcommand=scrollbar.set)

    table.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return table


def show_data(table, rows):
    table.delete(*table.get_children())

    for row in rows:
        table.insert("", "end", values=row)


def get_student(student_id):
    cur.execute("""
        SELECT s.student_id, s.student_name, s.phone,
               s.batch_id, b.batch_name,
               s.parent_name, s.parent_phone
        FROM students s
        JOIN batches b ON s.batch_id = b.batch_id
        WHERE s.student_id = %s
    """, (student_id,))

    return cur.fetchone()


def valid_phone(phone):
    return phone.isdigit() and len(phone) == 10


def valid_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def card(parent, title, value, color):
    box = tk.Frame(parent, bg=WHITE, padx=20, pady=15)
    box.pack(side="left", fill="both", expand=True, padx=7)

    tk.Label(
        box,
        text=title,
        bg=WHITE,
        fg="#65758b",
        font=("Arial", 11)
    ).pack(anchor="w")

    tk.Label(
        box,
        text=str(value),
        bg=WHITE,
        fg=color,
        font=("Arial", 23, "bold")
    ).pack(anchor="w", pady=5)


def get_batches():
    cur.execute("SELECT batch_id, batch_name FROM batches ORDER BY batch_id")
    return cur.fetchall()


#================ DASHBOARD ===========================

def dashboard():

    heading("Dashboard")

    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM attendance
        WHERE DATE(attendance_date) = CURDATE()
    """)
    today_count = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM attendance
        WHERE DATE(attendance_date) = CURDATE()
        AND status = 'P'
    """)
    present = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM attendance
        WHERE DATE(attendance_date) = CURDATE()
        AND status = 'A'
    """)
    absent = cur.fetchone()[0]

    cards = tk.Frame(content, bg=BG)
    cards.pack(fill="x", pady=10)

    card(cards, "Total Students", total_students, BLUE)
    card(cards, "Today's Records", today_count, "#6f42c1")
    card(cards, "Present Today", present, GREEN)
    card(cards, "Absent Today", absent, RED)

    tk.Label(
        content,
        text="Welcome to Student Attendance Management System",
        font=("Arial", 17, "bold"),
        bg=BG,
        fg=DARK
    ).pack(anchor="w", padx=15, pady=30)

    tk.Label(
        content,
        text="Select any option from the left menu to manage students and attendance.",
        font=("Arial", 12),
        bg=BG,
        fg="#65758b"
    ).pack(anchor="w", padx=15)


#================ ADD STUDENT =========================

def add_student():

    heading("Add New Student")

    form = tk.Frame(content, bg=WHITE, padx=20, pady=15)
    form.pack(anchor="nw", fill="x", padx=10)

    name = make_entry(form, "Student Name")
    phone = make_entry(form, "Student Phone")

    tk.Label(
        form, text="Select Batch",
        bg=WHITE, font=("Arial", 11)
    ).pack(anchor="w", padx=15, pady=(10, 3))

    batches = get_batches()
    batch_names = [b[1] for b in batches]

    batch = ttk.Combobox(
        form,
        values=batch_names,
        state="readonly",
        width=32,
        font=("Arial", 11)
    )
    batch.pack(anchor="w", padx=15)

    def save():

        student_name = name.get().strip()
        student_phone = phone.get().strip()

        if not student_name:
            messagebox.showerror("Error", "Enter student name!")
            return

        if not valid_phone(student_phone):
            messagebox.showerror("Error", "Enter valid 10 digit phone!")
            return

        if not batch.get():
            messagebox.showerror("Error", "Select a batch!")
            return

        batch_id = batches[batch_names.index(batch.get())][0]

        try:
            cur.execute("""
                INSERT INTO students
                (student_name, phone, batch_id)
                VALUES (%s, %s, %s)
            """, (student_name, student_phone, batch_id))

            con.commit()

            messagebox.showinfo(
                "Success",
                "Student added successfully!\nStudent ID: " + str(cur.lastrowid)
            )

            name.delete(0, tk.END)
            phone.delete(0, tk.END)
            batch.set("")

        except mysql.connector.Error as e:
            con.rollback()
            messagebox.showerror("Database Error", str(e))

    tk.Button(
        form,
        text="Add Student",
        command=save,
        bg=BLUE,
        fg=WHITE,
        font=("Arial", 11, "bold"),
        padx=20,
        pady=8
    ).pack(anchor="w", padx=15, pady=20)


#================ SEARCH STUDENT ======================

def search_student():

    heading("Student Complete Details")

    # ---------- SEARCH FORM ----------

    form = tk.Frame(content, bg=WHITE, padx=15, pady=15)
    form.pack(fill="x", padx=10)

    student_id = make_entry(form, "Enter Student ID")

    tk.Label(
        form,
        text="Select Batch",
        font=("Arial", 11),
        bg=WHITE,
        fg=DARK
    ).pack(anchor="w", padx=15, pady=(10, 3))

    batches = get_batches()
    batch_names = [b[1] for b in batches]

    batch_combo = ttk.Combobox(
        form,
        values=batch_names,
        state="readonly",
        width=32,
        font=("Arial", 11)
    )
    batch_combo.pack(anchor="w", padx=15, pady=5)

    # ---------- RESULT AREA ----------

    result_area = tk.Frame(content, bg=BG)
    result_area.pack(fill="both", expand=True)

    left_frame = tk.Frame(result_area, bg=BG)
    left_frame.pack(
        side="left",
        fill="both",
        expand=True,
        padx=5
    )

    right_frame = tk.Frame(result_area, bg=BG)
    right_frame.pack(
        side="left",
        fill="both",
        expand=True,
        padx=5
    )

    # ---------- STUDENT DETAILS ----------

    details = tk.Frame(left_frame, bg=WHITE)
    details.pack(fill="x", padx=5, pady=5)

    # ---------- ATTENDANCE HISTORY ----------

    tk.Label(
        left_frame,
        text="ATTENDANCE HISTORY",
        font=("Arial", 13, "bold"),
        bg=BG,
        fg=DARK
    ).pack(anchor="w", padx=10, pady=5)

    history_table = make_table(
        left_frame,
        ("date", "status"),
        ("Attendance Date", "Status")
    )

    # ---------- BATCH STUDENT COUNT ----------

    batch_count_label = tk.Label(
        right_frame,
        text="Total Students: 0",
        font=("Arial", 13, "bold"),
        bg=BG,
        fg=BLUE
    )
    batch_count_label.pack(anchor="w", padx=10, pady=10)

    # ---------- BATCH STUDENT TABLE ----------

    tk.Label(
        right_frame,
        text="BATCH STUDENT DETAILS",
        font=("Arial", 13, "bold"),
        bg=BG,
        fg=DARK
    ).pack(anchor="w", padx=10, pady=5)

    batch_table = make_table(
        right_frame,
        ("id", "name", "phone", "batch", "parent", "parent_phone"),
        ("ID", "Student Name", "Phone",
         "Batch", "Parent Name", "Parent Phone")
    )

    # ---------- SEARCH BY STUDENT ID ----------

    def search():

        sid = student_id.get().strip()

        if not sid.isdigit() or int(sid) <= 0:
            messagebox.showerror(
                "Error",
                "Enter valid student ID!"
            )
            return

        data = get_student(int(sid))

        if not data:
            messagebox.showerror(
                "Error",
                "Student not found!"
            )
            return

        for widget in details.winfo_children():
            widget.destroy()

        tk.Label(
            details,
            text="STUDENT INFORMATION",
            font=("Arial", 14, "bold"),
            bg=WHITE,
            fg=BLUE
        ).pack(anchor="w", padx=15, pady=10)

        info = [
            ("Student ID", data[0]),
            ("Student Name", data[1]),
            ("Student Phone", data[2]),
            ("Batch", data[4]),
            ("Parent Name", data[5] or "Not Added"),
            ("Parent Phone", data[6] or "Not Added")
        ]

        for label, value in info:
            tk.Label(
                details,
                text=f"{label}:  {value}",
                font=("Arial", 10),
                bg=WHITE
            ).pack(anchor="w", padx=15, pady=3)

        # Attendance Summary

        cur.execute("""
            SELECT
                COUNT(attendance_id),
                COALESCE(SUM(status = 'P'), 0),
                COALESCE(SUM(status = 'A'), 0),
                COALESCE(SUM(status = 'L'), 0)
            FROM attendance
            WHERE student_id = %s
        """, (sid,))

        total, present, absent, late = cur.fetchone()

        percentage = round(
            present * 100 / total, 2
        ) if total else 0

        tk.Label(
            details,
            text="ATTENDANCE SUMMARY",
            font=("Arial", 13, "bold"),
            bg=WHITE,
            fg=BLUE
        ).pack(anchor="w", padx=15, pady=10)

        tk.Label(
            details,
            text=f"Total Days: {total}   Present: {present}\n"
                 f"Absent: {absent}   Late: {late}\n"
                 f"Percentage: {percentage}%",
            font=("Arial", 10, "bold"),
            bg=WHITE,
            justify="left"
        ).pack(anchor="w", padx=15, pady=5)

        # Attendance History

        cur.execute("""
            SELECT attendance_date, status
            FROM attendance
            WHERE student_id = %s
            ORDER BY attendance_date DESC
        """, (sid,))

        history = cur.fetchall()

        show_data(history_table, history)

    # ---------- SEARCH BY BATCH ----------

    def search_batch():

        selected_batch = batch_combo.get()

        if not selected_batch:
            messagebox.showerror(
                "Error",
                "Please select a batch!"
            )
            return

        try:
            cur.execute("""
                SELECT
                    s.student_id,
                    s.student_name,
                    s.phone,
                    b.batch_name,
                    s.parent_name,
                    s.parent_phone
                FROM students s
                JOIN batches b
                ON s.batch_id = b.batch_id
                WHERE b.batch_name = %s
                ORDER BY s.student_id
            """, (selected_batch,))

            rows = cur.fetchall()

            show_data(batch_table, rows)

            batch_count_label.config(
                text=f"{selected_batch} Batch - Total Students: {len(rows)}"
            )

            if not rows:
                messagebox.showinfo(
                    "Information",
                    "No students found in this batch!"
                )

        except mysql.connector.Error as e:
            messagebox.showerror(
                "Database Error",
                str(e)
            )

    # ---------- BOTH BUTTONS ----------

    button_frame = tk.Frame(form, bg=WHITE)
    button_frame.pack(anchor="w", padx=10, pady=12)

    tk.Button(
        button_frame,
        text="Search Student",
        command=search,
        bg=BLUE,
        fg=WHITE,
        padx=15,
        pady=7
    ).pack(side="left", padx=5)

    tk.Button(
        button_frame,
        text="Search Batch",
        command=search_batch,
        bg=GREEN,
        fg=WHITE,
        padx=15,
        pady=7
    ).pack(side="left", padx=5)


#================ UPDATE STUDENT ======================

def update_student():

    heading("Update Student")

    form = tk.Frame(content, bg=WHITE, padx=20, pady=15)
    form.pack(fill="x", padx=10)

    sid = make_entry(form, "Student ID")

    name = make_entry(form, "New Student Name")
    phone = make_entry(form, "New Phone Number")

    def update():

        if not sid.get().isdigit() or int(sid.get()) <= 0:
            messagebox.showerror("Error", "Enter valid student ID!")
            return

        if not name.get().strip():
            messagebox.showerror("Error", "Enter student name!")
            return

        if not valid_phone(phone.get().strip()):
            messagebox.showerror("Error", "Enter valid 10 digit phone!")
            return

        if not get_student(int(sid.get())):
            messagebox.showerror("Error", "Student not found!")
            return

        cur.execute("""
            UPDATE students
            SET student_name = %s, phone = %s
            WHERE student_id = %s
        """, (name.get().strip(), phone.get().strip(), sid.get()))

        con.commit()
        messagebox.showinfo("Success", "Student updated successfully!")

    tk.Button(
        form, text="Update Student",
        command=update, bg=BLUE, fg=WHITE,
        padx=15, pady=8
    ).pack(anchor="w", padx=15, pady=20)


#================ DELETE STUDENT ======================

def delete_student():

    heading("Delete Student")

    form = tk.Frame(content, bg=WHITE, padx=20, pady=15)
    form.pack(fill="x", padx=10)

    sid = make_entry(form, "Student ID")

    def delete():

        if not sid.get().isdigit() or int(sid.get()) <= 0:
            messagebox.showerror("Error", "Enter valid student ID!")
            return

        data = get_student(int(sid.get()))

        if not data:
            messagebox.showerror("Error", "Student not found!")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete {data[1]} and all attendance records?"
        )

        if confirm:

            cur.execute(
                "DELETE FROM attendance WHERE student_id = %s",
                (sid.get(),)
            )

            cur.execute(
                "DELETE FROM students WHERE student_id = %s",
                (sid.get(),)
            )

            con.commit()

            messagebox.showinfo("Success", "Student deleted successfully!")


    tk.Button(
        form, text="Delete Student",
        command=delete, bg=RED, fg=WHITE,
        padx=15, pady=8
    ).pack(anchor="w", padx=15, pady=20)


#================ MARK ATTENDANCE =====================


def mark_attendance():

    heading("Mark Attendance")

    form = tk.Frame(content, bg=WHITE, padx=20, pady=15)
    form.pack(fill="x", padx=10)

    sid = make_entry(form, "Student ID")

    tk.Label(
        form, text="Attendance Status",
        bg=WHITE, font=("Arial", 11)
    ).pack(anchor="w", padx=15, pady=(10, 3))

    status = ttk.Combobox(
        form, values=["P", "A", "L"],
        state="readonly", width=32,
        font=("Arial", 11)
    )
    status.pack(anchor="w", padx=15)
    status.set("P")

    student_label = tk.Label(
        form, text="Student details will appear here",
        bg=WHITE, fg=BLUE, font=("Arial", 11)
    )
    student_label.pack(anchor="w", padx=15, pady=12)

    def check_student(*args):

        if sid.get().isdigit() and int(sid.get()) > 0:
            data = get_student(int(sid.get()))

            if data:
                student_label.config(
                    text=f"Name: {data[1]} | Batch: {data[4]}"
                )
            else:
                student_label.config(text="Student not found!")
        else:
            student_label.config(text="Enter Student ID")

    sid.bind("<KeyRelease>", check_student)

    # Past date dropdown
    tk.Label(
        form, text="Select Missed Attendance Date",
        bg=WHITE, font=("Arial", 11)
    ).pack(anchor="w", padx=15, pady=(10, 3))

    past_dates = [
        (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(1, 31)
    ]

    past_date = ttk.Combobox(
        form,
        values=past_dates,
        state="readonly",
        width=32,
        font=("Arial", 11)
    )
    past_date.pack(anchor="w", padx=15)
    past_date.set("Select Past Date")

    def save_attendance(selected_date):

        if not sid.get().isdigit() or int(sid.get()) <= 0:
            messagebox.showerror("Error", "Enter valid Student ID!")
            return

        data = get_student(int(sid.get()))

        if not data:
            messagebox.showerror("Error", "Student not found!")
            return

        if status.get() not in ("P", "A", "L"):
            messagebox.showerror("Error", "Select P, A or L!")
            return

        try:
            cur.execute("""
                SELECT attendance_id
                FROM attendance
                WHERE student_id = %s
                AND DATE(attendance_date) = %s
            """, (sid.get(), selected_date))

            if cur.fetchone():
                messagebox.showwarning(
                    "Already Marked",
                    "Attendance already exists for this date!"
                )
                return

            cur.execute("""
                INSERT INTO attendance
                (student_id, batch_id, status, attendance_date)
                VALUES (%s, %s, %s, %s)
            """, (
                sid.get(), data[3],
                status.get(), selected_date
            ))

            con.commit()

            messagebox.showinfo(
                "Success",
                f"Attendance saved for {selected_date}!"
            )

        except mysql.connector.Error as e:
            con.rollback()
            messagebox.showerror("Database Error", str(e))

    def save_today():
        save_attendance(date.today())

    def save_past():

        if past_date.get() not in past_dates:
            messagebox.showerror(
                "Error", "Please select a past date!"
            )
            return

        selected = valid_date(past_date.get())
        save_attendance(selected)

    tk.Button(
        form, text="Save Today's Attendance",
        command=save_today,
        bg=GREEN, fg=WHITE,
        padx=15, pady=8
    ).pack(anchor="w", padx=15, pady=12)

    tk.Button(
        form, text="Save Past Attendance",
        command=save_past,
        bg=BLUE, fg=WHITE,
        padx=15, pady=8
    ).pack(anchor="w", padx=15, pady=8)



#================ TODAY'S ATTENDANCE ==================

def today_attendance():

    heading("Today's Attendance")

    cur.execute("""
        SELECT s.student_id, s.student_name,
               b.batch_name, a.status, a.attendance_date
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        JOIN batches b ON a.batch_id = b.batch_id
        WHERE DATE(a.attendance_date) = CURDATE()
        ORDER BY s.student_id
    """)

    data = cur.fetchall()

    table = make_table(
        content,
        ("id", "name", "batch", "status", "date"),
        ("Student ID", "Student Name", "Batch", "Status", "Date")
    )

    show_data(table, data)


#================ MONTHLY REPORT ======================

def monthly_report():

    heading("Monthly Attendance Report")

    form = tk.Frame(content, bg=WHITE, padx=15, pady=15)
    form.pack(fill="x", padx=10)

    month = make_entry(form, "Month (1-12)", str(date.today().month))
    year = make_entry(form, "Year", str(date.today().year))

    table = make_table(
        content,
        ("id", "name", "batch", "present", "absent", "late"),
        ("ID", "Name", "Batch", "Present", "Absent", "Late")
    )

    def search():

        try:
            m = int(month.get())
            y = int(year.get())

            if not 1 <= m <= 12 or not 2000 <= y <= 2100:
                raise ValueError

        except ValueError:
            messagebox.showerror("Error", "Enter valid month and year!")
            return

        cur.execute("""
            SELECT s.student_id, s.student_name, b.batch_name,
                   COALESCE(SUM(a.status = 'P'), 0),
                   COALESCE(SUM(a.status = 'A'), 0),
                   COALESCE(SUM(a.status = 'L'), 0)
            FROM students s
            JOIN batches b ON s.batch_id = b.batch_id
            LEFT JOIN attendance a
            ON s.student_id = a.student_id
            AND MONTH(a.attendance_date) = %s
            AND YEAR(a.attendance_date) = %s
            GROUP BY s.student_id, s.student_name, b.batch_name
            ORDER BY s.student_id
        """, (m, y))

        show_data(table, cur.fetchall())

    tk.Button(
        form, text="Generate Report",
        command=search, bg=BLUE, fg=WHITE,
        padx=15, pady=7
    ).pack(anchor="w", padx=15, pady=15)


#================ BATCH WISE REPORT ===================

def batch_report():

    heading("Batch Wise Attendance Report")

    form = tk.Frame(content, bg=WHITE, padx=15, pady=15)
    form.pack(fill="x", padx=10)

    month = make_entry(form, "Month", str(date.today().month))
    year = make_entry(form, "Year", str(date.today().year))

    table = make_table(
        content,
        ("batch", "total", "present", "absent", "late"),
        ("Batch", "Students", "Present", "Absent", "Late")
    )

    def search():

        try:
            m = int(month.get())
            y = int(year.get())

            if not 1 <= m <= 12 or not 2000 <= y <= 2100:
                raise ValueError

        except ValueError:
            messagebox.showerror("Error", "Enter valid month and year!")
            return

        cur.execute("""
            SELECT b.batch_name,
                   COUNT(DISTINCT s.student_id),
                   COALESCE(SUM(a.status = 'P'), 0),
                   COALESCE(SUM(a.status = 'A'), 0),
                   COALESCE(SUM(a.status = 'L'), 0)
            FROM batches b
            LEFT JOIN students s ON b.batch_id = s.batch_id
            LEFT JOIN attendance a
            ON s.student_id = a.student_id
            AND MONTH(a.attendance_date) = %s
            AND YEAR(a.attendance_date) = %s
            GROUP BY b.batch_id, b.batch_name
            ORDER BY b.batch_id
        """, (m, y))

        show_data(table, cur.fetchall())

    tk.Button(
        form, text="Generate Report",
        command=search, bg=BLUE, fg=WHITE,
        padx=15, pady=7
    ).pack(anchor="w", padx=15, pady=15)


#================ STUDENT PERCENTAGE ==================

def student_percentage():

    heading("Student Attendance Percentage")

    form = tk.Frame(content, bg=WHITE, padx=15, pady=15)
    form.pack(fill="x", padx=10)

    month = make_entry(form, "Month", str(date.today().month))
    year = make_entry(form, "Year", str(date.today().year))

    table = make_table(
        content,
        ("id", "name", "batch", "total", "present",
         "absent", "late", "percentage"),
        ("ID", "Name", "Batch", "Total Days",
         "Present", "Absent", "Late", "Percentage")
    )

    def search():

        try:
            m = int(month.get())
            y = int(year.get())

            if not 1 <= m <= 12 or not 2000 <= y <= 2100:
                raise ValueError

        except ValueError:
            messagebox.showerror("Error", "Enter valid month and year!")
            return

        cur.execute("""
            SELECT s.student_id, s.student_name, b.batch_name,
                   COUNT(a.attendance_id),
                   COALESCE(SUM(a.status = 'P'), 0),
                   COALESCE(SUM(a.status = 'A'), 0),
                   COALESCE(SUM(a.status = 'L'), 0),
                   ROUND(
                       COALESCE(
                           SUM(a.status = 'P') * 100.0 /
                           NULLIF(COUNT(a.attendance_id), 0), 0
                       ), 2
                   )
            FROM students s
            JOIN batches b ON s.batch_id = b.batch_id
            LEFT JOIN attendance a
            ON s.student_id = a.student_id
            AND MONTH(a.attendance_date) = %s
            AND YEAR(a.attendance_date) = %s
            GROUP BY s.student_id, s.student_name, b.batch_name
            ORDER BY s.student_id
        """, (m, y))

        show_data(table, cur.fetchall())

    tk.Button(
        form, text="Generate Report",
        command=search, bg=BLUE, fg=WHITE,
        padx=15, pady=7
    ).pack(anchor="w", padx=15, pady=15)


#================ UPDATE PARENT DETAILS ===============

def update_parent():

    heading("Update Parent Details")

    form = tk.Frame(content, bg=WHITE, padx=20, pady=15)
    form.pack(fill="x", padx=10)

    sid = make_entry(form, "Student ID")
    parent_name = make_entry(form, "Parent Name")
    parent_phone = make_entry(form, "Parent Phone")

    def update():

        if not sid.get().isdigit() or int(sid.get()) <= 0:
            messagebox.showerror("Error", "Enter valid student ID!")
            return

        if not get_student(int(sid.get())):
            messagebox.showerror("Error", "Student not found!")
            return

        if not parent_name.get().strip():
            messagebox.showerror("Error", "Enter parent name!")
            return

        if not valid_phone(parent_phone.get().strip()):
            messagebox.showerror("Error", "Enter valid 10 digit phone!")
            return

        cur.execute("""
            UPDATE students
            SET parent_name = %s, parent_phone = %s
            WHERE student_id = %s
        """, (
            parent_name.get().strip(),
            parent_phone.get().strip(),
            sid.get()
        ))

        con.commit()

        messagebox.showinfo(
            "Success", "Parent details updated successfully!"
        )

    tk.Button(
        form, text="Update Parent",
        command=update, bg=BLUE, fg=WHITE,
        padx=15, pady=8
    ).pack(anchor="w", padx=15, pady=20)


#================ ALL STUDENT DETAILS =================

def all_students():

    heading("All Student + Parent Details")

    cur.execute("""
        SELECT s.student_id, s.student_name, s.phone,
               b.batch_name, s.parent_name, s.parent_phone
        FROM students s
        JOIN batches b ON s.batch_id = b.batch_id
        ORDER BY s.student_id
    """)

    data = cur.fetchall()

    table = make_table(
        content,
        ("id", "name", "phone", "batch", "parent", "parent_phone"),
        ("ID", "Student Name", "Phone", "Batch",
         "Parent Name", "Parent Phone")
    )

    show_data(table, data)


#================ BATCH WISE STUDENT DETAILS =================

def batch_wise_students():

    heading("Batch Wise Student Details")

    form = tk.Frame(content, bg=WHITE, padx=15, pady=12)
    form.pack(fill="x", padx=10, pady=5)

    tk.Label(
        form,
        text="Select Batch:",
        font=("Arial", 11, "bold"),
        bg=WHITE,
        fg=DARK
    ).pack(side="left", padx=10)

    batch_var = tk.StringVar()

    batches = get_batches()
    batch_names = [b[1] for b in batches]

    batch_box = ttk.Combobox(
        form,
        textvariable=batch_var,
        values=batch_names,
        state="readonly",
        width=25,
        font=("Arial", 11)
    )
    batch_box.pack(side="left", padx=5)

    # Student details table

    table_frame = tk.Frame(content, bg=WHITE)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    columns = (
        "id", "name", "phone", "batch", "parent", "parent_phone",
        "total", "present", "absent", "late", "percentage"
    )

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )

    headings = (
        "Student ID", "Student Name", "Phone", "Batch",
        "Parent Name", "Parent Phone", "Total Days",
        "Present", "Absent", "Late", "Percentage"
    )

    widths = (75, 140, 110, 90, 120, 110, 80, 75, 75, 65, 95)

    for col, title, width in zip(columns, headings, widths):
        table.heading(col, text=title)
        table.column(col, width=width, minwidth=60, anchor="center")

    y_scroll = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=table.yview
    )

    x_scroll = ttk.Scrollbar(
        table_frame,
        orient="horizontal",
        command=table.xview
    )

    table.configure(
        yscrollcommand=y_scroll.set,
        xscrollcommand=x_scroll.set
    )

    table.grid(row=0, column=0, sticky="nsew")
    y_scroll.grid(row=0, column=1, sticky="ns")
    x_scroll.grid(row=1, column=0, sticky="ew")

    table_frame.rowconfigure(0, weight=1)
    table_frame.columnconfigure(0, weight=1)

    result_label = tk.Label(
        content,
        text="Select a batch and click Show Students.",
        font=("Arial", 11, "bold"),
        bg=BG,
        fg=BLUE
    )
    result_label.pack(anchor="w", padx=15, pady=5)

    def show_students():

        selected_batch = batch_var.get().strip()

        if not selected_batch:
            messagebox.showwarning("Warning", "Please select a batch!")
            return

        query = """
            SELECT
                s.student_id,
                s.student_name,
                s.phone,
                b.batch_name,
                s.parent_name,
                s.parent_phone,
                COUNT(a.attendance_id),
                COALESCE(SUM(a.status = 'P'), 0),
                COALESCE(SUM(a.status = 'A'), 0),
                COALESCE(SUM(a.status = 'L'), 0),
                CASE
                    WHEN COUNT(a.attendance_id) = 0 THEN 0
                    ELSE ROUND(
                        SUM(a.status = 'P') * 100.0 /
                        COUNT(a.attendance_id), 2
                    )
                END
            FROM students s
            JOIN batches b ON s.batch_id = b.batch_id
            LEFT JOIN attendance a ON s.student_id = a.student_id
            WHERE b.batch_name = %s
            GROUP BY
                s.student_id,
                s.student_name,
                s.phone,
                b.batch_name,
                s.parent_name,
                s.parent_phone
            ORDER BY s.student_id
        """

        try:
            cur.execute(query, (selected_batch,))
            rows = cur.fetchall()

            show_data(table, rows)

            result_label.config(
                text=f"Batch: {selected_batch} | Total Students: {len(rows)}"
            )

            if not rows:
                messagebox.showinfo(
                    "Information",
                    "No students found in this batch."
                )

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))

    tk.Button(
        form,
        text="Show Students",
        command=show_students,
        bg=BLUE,
        fg=WHITE,
        font=("Arial", 10, "bold"),
        padx=15,
        pady=7,
        cursor="hand2"
    ).pack(side="left", padx=10)


#================ TOP HEADER ==========================

header = tk.Frame(root, bg=DARK, height=65)
header.pack(fill="x")
header.pack_propagate(False)

tk.Label(
    header,
    text="STUDENT ATTENDANCE MANAGEMENT SYSTEM",
    font=("Arial", 19, "bold"),
    bg=DARK,
    fg=WHITE
).pack(side="left", padx=25, pady=15)


#================ SIDEBAR =============================

main = tk.Frame(root, bg=BG)
main.pack(fill="both", expand=True)

sidebar = tk.Frame(main, bg=BLUE, width=225)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

tk.Label(
    sidebar,
    text="MAIN MENU",
    font=("Arial", 14, "bold"),
    bg=BLUE,
    fg=WHITE
).pack(pady=20)


#================ CONTENT AREA ========================

content = tk.Frame(main, bg=BG)
content.pack(side="left", fill="both", expand=True, padx=20, pady=20)


#================ MENU BUTTONS ========================

menu_items = [
    ("Dashboard", dashboard),
    ("Add New Student", add_student),
    ("Search Student Details", search_student),
    ("Update Student", update_student),
    ("Delete Student", delete_student),
    ("Mark Attendance", mark_attendance),
    ("Today's Attendance", today_attendance),
    ("Monthly Report", monthly_report),
    ("Batch Wise Report", batch_report),
    ("Attendance Percentage", student_percentage),
    ("Update Parent Details", update_parent),
    ("All Student Details", all_students),
    ("Batch Wise Student Details", batch_wise_students)
]


for title, function in menu_items:

    tk.Button(
        sidebar,
        text=title,
        command=function,
        font=("Arial", 10, "bold"),
        bg=BLUE,
        fg=WHITE,
        activebackground="#3b629a",
        activeforeground=WHITE,
        relief="flat",
        anchor="w",
        padx=20,
        pady=11,
        cursor="hand2"
    ).pack(fill="x", padx=7, pady=2)


def close_app():

    if messagebox.askyesno("Exit", "Do you want to exit?"):
        cur.close()
        con.close()
        root.destroy()


tk.Button(
    sidebar,
    text="Exit",
    command=close_app,
    font=("Arial", 11, "bold"),
    bg=RED,
    fg=WHITE,
    relief="flat",
    pady=10
).pack(side="bottom", fill="x", padx=10, pady=15)


#================ START APPLICATION ===================

dashboard()

root.protocol("WM_DELETE_WINDOW", close_app)

root.mainloop()

