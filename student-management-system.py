"""
=============================================================================
STUDENT MANAGEMENT SYSTEM (WITH PER-STUDENT HELPER & MONITORING)
=============================================================================
Main Menu: Student Management System (Add, Display, Search, Delete)
Inside "Display Students": Select any student to open their personal Student Helper
(Calculator, To-Do List, Short Notes, Timer, Marks Tracker & Graph, Timetable)
=============================================================================
"""

import time
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================
# 1. ADMIN LOGIN
# ==========================================
VALID_USERNAME = "admin"
VALID_PASSWORD = "MySQL8.0"

def login():
    print("=" * 45)
    print("      STUDENT MANAGEMENT SYSTEM LOGIN")
    print("=" * 45)
    while True:
        username = input("Enter Admin User ID: ").strip()
        password = input("Enter Admin Password: ").strip()
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            print("\nLogin successful!\n")
            return True
        else:
            print("\nIncorrect UserID or Password. Try again.")
            choice = input("Do you want to try again or exit? (try/exit): ").strip().lower()
            if choice == "exit":
                print("Exiting system...")
                return False

# ==========================================
# 2. DATABASE INITIALIZATION (MySQL / SQLite)
# ==========================================
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "put your password here"

USE_MYSQL = False
conn = None
cursor = None

try:
    import mysql.connector as mc
    conn = mc.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS Student_Helper")
    cursor.execute("USE Student_Helper")
    USE_MYSQL = True
    print("Database connected successfully (MySQL: Student_Helper)!")
except Exception:
    import sqlite3
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()
    USE_MYSQL = False
    print("Database connected in Local Mode (SQLite: student_helper.db)")

def db_execute(query, params=None):
    if params is None:
        params = ()
    if USE_MYSQL:
        cursor.execute(query, params)
    else:
        cursor.execute(query.replace("%s", "?"), params)

def db_commit():
    conn.commit()

# Table creation
auto_inc = "AUTO_INCREMENT" if USE_MYSQL else "AUTOINCREMENT"

db_execute("""
CREATE TABLE IF NOT EXISTS students (
    roll_no VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    course VARCHAR(100)
)
""")

db_execute(f"""
CREATE TABLE IF NOT EXISTS todo_list (
    Sno INTEGER PRIMARY KEY {auto_inc},
    roll_no VARCHAR(20),
    task VARCHAR(100),
    completion BOOL
)
""")

db_execute(f"""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY {auto_inc},
    roll_no VARCHAR(20),
    title VARCHAR(100),
    content TEXT
)
""")

db_execute(f"""
CREATE TABLE IF NOT EXISTS marks (
    id INTEGER PRIMARY KEY {auto_inc},
    roll_no VARCHAR(20),
    subject VARCHAR(100),
    marks FLOAT,
    max_marks FLOAT,
    grade VARCHAR(5)
)
""")

db_execute(f"""
CREATE TABLE IF NOT EXISTS schedule (
    id INTEGER PRIMARY KEY {auto_inc},
    roll_no VARCHAR(20),
    day VARCHAR(20),
    time_slot VARCHAR(50),
    activity VARCHAR(100),
    location VARCHAR(100)
)
""")
db_commit()

# ==========================================
# 3. STUDENT HELPER MODULES (CODE 1)
# ==========================================

# CALCULATOR
def calculator():
    print("\n--- Calculator ---")
    expr = input("Enter question: ")
    try:
        print("Result =", eval(expr, {"__builtins__": None}, {}))
    except Exception:
        print("Invalid expression!")

# TO-DO LIST (For Specific Student)
def add_task(roll_no, student_name):
    task = input("Enter Task: ").strip()
    if not task:
        print("Task cannot be empty!\n")
        return
    db_execute("INSERT INTO todo_list (roll_no, task, completion) VALUES (%s, %s, %s)", (roll_no, task, False))
    db_commit()
    print(f"Task added for {student_name}\n")

def view_tasks(roll_no, student_name):
    db_execute("SELECT Sno, task, completion FROM todo_list WHERE roll_no = %s", (roll_no,))
    rows = cursor.fetchall()
    if not rows:
        print(f"No tasks found for {student_name}.\n")
        return []
    else:
        print(f"\nTasks for {student_name}:")
        for r in rows:
            status = "Done" if r[2] else "Not Done"
            print(f"  {r[0]} - {r[1]} : {status}")
        print()
        return rows

def mark_done(roll_no, student_name):
    rows = view_tasks(roll_no, student_name)
    if not rows:
        return
    try:
        sno = int(input("Enter Task ID to mark as completed: "))
        db_execute("UPDATE todo_list SET completion = 1 WHERE Sno = %s AND roll_no = %s", (sno, roll_no))
        db_commit()
        print("Task marked as done\n")
    except ValueError:
        print("Invalid Task ID!\n")

def delete_task(roll_no, student_name):
    rows = view_tasks(roll_no, student_name)
    if not rows:
        return
    try:
        sno = int(input("Enter Task ID to delete: "))
        db_execute("DELETE FROM todo_list WHERE Sno = %s AND roll_no = %s", (sno, roll_no))
        db_commit()
        print("Task deleted\n")
    except ValueError:
        print("Invalid Task ID!\n")

# SHORT NOTES (For Specific Student)
def add_note(roll_no, student_name):
    title = input("Note Title: ").strip()
    content = input("Note Content: ").strip()
    db_execute("INSERT INTO notes (roll_no, title, content) VALUES (%s, %s, %s)", (roll_no, title, content))
    db_commit()
    print(f"Note saved for {student_name}\n")

def view_notes(roll_no, student_name):
    db_execute("SELECT id, title, content FROM notes WHERE roll_no = %s", (roll_no,))
    rows = cursor.fetchall()
    if not rows:
        print(f"No notes saved for {student_name}.\n")
        return []
    else:
        print(f"\nNotes for {student_name}:")
        for r in rows:
            print(f"  {r[0]} . {r[1]} : {r[2]}")
        print()
        return rows

def delete_note(roll_no, student_name):
    rows = view_notes(roll_no, student_name)
    if not rows:
        return
    try:
        note_id = int(input("Enter Note ID to delete: "))
        db_execute("DELETE FROM notes WHERE id = %s AND roll_no = %s", (note_id, roll_no))
        db_commit()
        print("Note deleted\n")
    except ValueError:
        print("Invalid Note ID!\n")

# TIMER
def timer():
    print("\n--- Timer ---")
    try:
        seconds = int(input("Enter time in seconds: "))
        print("Timer started...")
        time.sleep(seconds)
        print("\n●•´`• Time's Up! •´`•●\n")
    except ValueError:
        print("Invalid number of seconds!\n")

# MARKS TRACKER (For Specific Student)
def calculate_grade(marks, max_marks):
    if max_marks <= 0:
        return "F"
    percentage = (marks / max_marks) * 100
    if percentage >= 91: return "A1"
    elif percentage >= 81: return "A2"
    elif percentage >= 71: return "B1"
    elif percentage >= 61: return "C1"
    elif percentage >= 51: return "D"
    else: return "F"

def add_marks(roll_no, student_name):
    subject = input("Enter Subject Name: ").strip()
    try:
        marks = float(input("Marks obtained: "))
        max_marks = float(input("Maximum Marks: "))
    except ValueError:
        print("Invalid input for marks!\n")
        return
    grade = calculate_grade(marks, max_marks)
    db_execute(
        "INSERT INTO marks (roll_no, subject, marks, max_marks, grade) VALUES (%s, %s, %s, %s, %s)",
        (roll_no, subject, marks, max_marks, grade)
    )
    db_commit()
    print(f"Marks added for {student_name}!\n")

def view_marks(roll_no, student_name):
    db_execute("SELECT subject, marks, max_marks, grade FROM marks WHERE roll_no = %s", (roll_no,))
    rows = cursor.fetchall()
    if not rows:
        print(f"No marks recorded for {student_name}.\n")
    else:
        df = pd.DataFrame(rows, columns=["Subject", "Marks", "Max Marks", "Grade"])
        print(f"\n--- Marks for {student_name} (Roll: {roll_no}) ---")
        print(df.to_string(index=False))
        total_max = df["Max Marks"].sum()
        if total_max > 0:
            avg = df["Marks"].sum() / total_max * 100
            print(f"\nOverall Percentage: {avg:.2f}%\n")

def show_marks_graph(roll_no, student_name):
    db_execute("SELECT subject, marks, max_marks FROM marks WHERE roll_no = %s", (roll_no,))
    rows = cursor.fetchall()
    if not rows:
        print(f"No marks available to generate graph for {student_name}.\n")
        return
    df = pd.DataFrame(rows, columns=["Subject", "Marks", "Max Marks"])
    plt.figure(figsize=(8, 5))
    bars = plt.bar(df["Subject"], df["Marks"], color="skyblue", edgecolor="black")
    plt.xlabel("Subjects")
    plt.ylabel("Marks")
    plt.title(f"Marks Bar Graph - {student_name} (Roll No: {roll_no})")
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.5, f"{yval:.1f}", ha='center', va='bottom')

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

# SCHEDULE / TIMETABLE (For Specific Student)
def add_schedule(roll_no, student_name):
    day = input("Enter Day: ").strip()
    time_slot = input("Enter Time (e.g., 9-10am): ").strip()
    activity = input("Enter Subject/Activity: ").strip()
    location = input("Enter Location: ").strip()

    db_execute(
        "INSERT INTO schedule (roll_no, day, time_slot, activity, location) VALUES (%s, %s, %s, %s, %s)",
        (roll_no, day, time_slot, activity, location)
    )
    db_commit()
    print(f"Schedule entry added for {student_name}!\n")

def view_schedule(roll_no, student_name):
    db_execute("SELECT day, time_slot, activity, location FROM schedule WHERE roll_no = %s", (roll_no,))
    rows = cursor.fetchall()
    if not rows:
        print(f"No schedule recorded for {student_name}.\n")
    else:
        df = pd.DataFrame(rows, columns=["Day", "Time", "Subject/Activity", "Location"])
        print(f"\n--- Schedule for {student_name} (Roll: {roll_no}) ---")
        print(df.to_string(index=False))
        print()

# ==========================================
# 4. STUDENT HELPER DASHBOARD (CODE 1)
# ==========================================
def open_student_helper(student):
    roll_no = student[0]
    name = student[1]

    while True:
        print(f"\n==========================================")
        print(f"  STUDENT HELPER APP: {name} ({roll_no})")
        print(f"==========================================")
        print("1. Calculator")
        print("2. To-Do List")
        print("3. Short Notes")
        print("4. Timer")
        print("5. Marks Tracker")
        print("6. Schedule / Timetable")
        print("7. Back to Student Management System")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            calculator()

        elif choice == "2":
            print("\n 1. Add Task\n 2. View Tasks\n 3. Mark as Done\n 4. Delete Task")
            choice_2 = input("Enter choice: ").strip()
            if choice_2 == "1": add_task(roll_no, name)
            elif choice_2 == "2": view_tasks(roll_no, name)
            elif choice_2 == "3": mark_done(roll_no, name)
            elif choice_2 == "4": delete_task(roll_no, name)
            else: print("Invalid choice\n")

        elif choice == "3":
            print("\n 1. Add Note\n 2. View Notes\n 3. Delete Note")
            choice_3 = input("Enter choice: ").strip()
            if choice_3 == "1": add_note(roll_no, name)
            elif choice_3 == "2": view_notes(roll_no, name)
            elif choice_3 == "3": delete_note(roll_no, name)
            else: print("Invalid choice\n")

        elif choice == "4":
            timer()

        elif choice == "5":
            print("\n 1. Add Marks\n 2. View Marks\n 3. Show Graph")
            c = input("Enter choice: ").strip()
            if c == "1": add_marks(roll_no, name)
            elif c == "2": view_marks(roll_no, name)
            elif c == "3": show_marks_graph(roll_no, name)
            else: print("Invalid choice\n")

        elif choice == "6":
            print("\n 1. Add Schedule Entry\n 2. View Schedule")
            c = input("Enter choice: ").strip()
            if c == "1": add_schedule(roll_no, name)
            elif c == "2": view_schedule(roll_no, name)
            else: print("Invalid choice\n")

        elif choice == "7":
            print(f"Exiting Student Helper for {name}...\n")
            break

        else:
            print("Invalid choice\n")

# ==========================================
# 5. STUDENT MANAGEMENT SYSTEM (CODE 2)
# ==========================================
def add_student():
    roll_no = input("Enter Roll Number: ").strip()
    if not roll_no:
        print("Roll number cannot be empty!\n")
        return
    db_execute("SELECT roll_no FROM students WHERE roll_no = %s", (roll_no,))
    if cursor.fetchone():
        print(f"Student with Roll Number '{roll_no}' already exists!\n")
        return

    name = input("Enter Student Name: ").strip()
    age = input("Enter Age: ").strip()
    course = input("Enter Course: ").strip()

    db_execute(
        "INSERT INTO students (roll_no, name, age, course) VALUES (%s, %s, %s, %s)",
        (roll_no, name, age, course)
    )
    db_commit()
    print("Student added successfully!\n")

def display_students():
    db_execute("SELECT roll_no, name, age, course FROM students ORDER BY roll_no")
    students = cursor.fetchall()
    if len(students) == 0:
        print("No student records found.\n")
        return

    print("\n--- Student Records ---")
    for student in students:
        print("Roll No:", student[0])
        print("Name   :", student[1])
        print("Age    :", student[2])
        print("Course :", student[3])
        print("-----------------------")

    # Enter Student Helper for monitoring!
    selected_roll = input("\nEnter Roll Number to open their Student Helper (or press Enter to return): ").strip()
    if not selected_roll:
        return

    db_execute("SELECT roll_no, name, age, course FROM students WHERE roll_no = %s", (selected_roll,))
    target = cursor.fetchone()
    if target:
        open_student_helper(target)
    else:
        print(f"Student with Roll Number '{selected_roll}' not found.\n")

def search_student():
    roll_no = input("Enter Roll Number to search: ").strip()
    db_execute("SELECT roll_no, name, age, course FROM students WHERE roll_no = %s", (roll_no,))
    student = cursor.fetchone()

    if student:
        print("\nStudent Found!")
        print("Roll No:", student[0])
        print("Name   :", student[1])
        print("Age    :", student[2])
        print("Course :", student[3])

        choice = input("\nDo you want to open their Student Helper to monitor work? (y/n): ").strip().lower()
        if choice == 'y':
            open_student_helper(student)
    else:
        print("Student not found.\n")

def delete_student():
    roll_no = input("Enter Roll Number to delete: ").strip()
    db_execute("SELECT roll_no, name FROM students WHERE roll_no = %s", (roll_no,))
    student = cursor.fetchone()

    if student:
        db_execute("DELETE FROM students WHERE roll_no = %s", (roll_no,))
        db_execute("DELETE FROM todo_list WHERE roll_no = %s", (roll_no,))
        db_execute("DELETE FROM notes WHERE roll_no = %s", (roll_no,))
        db_execute("DELETE FROM marks WHERE roll_no = %s", (roll_no,))
        db_execute("DELETE FROM schedule WHERE roll_no = %s", (roll_no,))
        db_commit()
        print(f"Student {student[1]} (Roll: {roll_no}) deleted successfully.\n")
    else:
        print("Student not found.\n")

# ==========================================
# 6. MAIN APPLICATION MENU
# ==========================================
def main():
    if not login():
        return

    while True:
        print("\n===== STUDENT MANAGEMENT SYSTEM =====")
        print("1. Add Student")
        print("2. Display Students")
        print("3. Search Student")
        print("4. Delete Student")
        print("5. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_student()
        elif choice == "2":
            display_students()
        elif choice == "3":
            search_student()
        elif choice == "4":
            delete_student()
        elif choice == "5":
            print("Thank you!")
            break
        else:
            print("Invalid choice. Please try again.")

    if conn:
        conn.close()

if __name__ == "__main__":
    main()
