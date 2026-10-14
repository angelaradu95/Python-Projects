"""A simple student tracking application using Tkinter and SQLite3.

Run: python student_tracking.py
The database (students.db) will be created beside this file automatically.
"""

import sqlite3
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


DATABASE_PATH = Path(__file__).resolve().with_name("students.db")


def create_database():
    """Create the students table if it does not already exist."""
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL,
                course TEXT NOT NULL
            )
            """
        )


class StudentTrackingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Tracking")
        self.root.geometry("920x550")
        self.root.minsize(760, 480)

        self.fields = {}
        self.build_interface()
        self.load_students()

    def build_interface(self):
        title = ttk.Label(
            self.root, text="Student Tracking", font=("Arial", 20, "bold")
        )
        title.pack(pady=(16, 12))

        form_frame = ttk.LabelFrame(self.root, text="Student Information", padding=12)
        form_frame.pack(fill="x", padx=16, pady=(0, 12))
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        labels = [
            ("First name", "first_name", 0, 0),
            ("Last name", "last_name", 0, 2),
            ("Phone number", "phone", 1, 0),
            ("Email", "email", 1, 2),
            ("Current course", "course", 2, 0),
        ]
        for label, key, row, column in labels:
            ttk.Label(form_frame, text=label + ":").grid(
                row=row, column=column, padx=(0, 8), pady=5, sticky="w"
            )
            entry = ttk.Entry(form_frame)
            entry.grid(
                row=row, column=column + 1, padx=(0, 16), pady=5, sticky="ew"
            )
            self.fields[key] = entry

        ttk.Button(form_frame, text="Submit Student", command=self.add_student).grid(
            row=3, column=0, columnspan=4, pady=(14, 4)
        )

        list_frame = ttk.LabelFrame(self.root, text="Student List", padding=10)
        list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        columns = ("first_name", "last_name", "phone", "email", "course")
        self.table = ttk.Treeview(
            list_frame, columns=columns, show="headings", selectmode="extended"
        )
        headings = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "phone": "Phone Number",
            "email": "Email",
            "course": "Current Course",
        }
        for column in columns:
            self.table.heading(column, text=headings[column])
            self.table.column(column, width=160, minwidth=100)

        vertical_scroll = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.table.yview
        )
        horizontal_scroll = ttk.Scrollbar(
            list_frame, orient="horizontal", command=self.table.xview
        )
        self.table.configure(
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set,
        )
        self.table.grid(row=0, column=0, sticky="nsew")
        vertical_scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll.grid(row=1, column=0, sticky="ew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        ttk.Button(
            self.root, text="Delete Selected Student(s)", command=self.delete_students
        ).pack(pady=(0, 16))

    def add_student(self):
        values = {key: entry.get().strip() for key, entry in self.fields.items()}
        if not all(values.values()):
            messagebox.showwarning("Missing information", "Please fill in all fields.")
            return

        try:
            with sqlite3.connect(DATABASE_PATH) as connection:
                connection.execute(
                    """
                    INSERT INTO students (first_name, last_name, phone, email, course)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        values["first_name"],
                        values["last_name"],
                        values["phone"],
                        values["email"],
                        values["course"],
                    ),
                )
        except sqlite3.Error as error:
            messagebox.showerror("Database error", str(error))
            return

        for entry in self.fields.values():
            entry.delete(0, tk.END)
        self.load_students()
        messagebox.showinfo("Success", "Student added successfully!")

    def load_students(self):
        for item in self.table.get_children():
            self.table.delete(item)

        try:
            with sqlite3.connect(DATABASE_PATH) as connection:
                students = connection.execute(
                    """
                    SELECT id, first_name, last_name, phone, email, course
                    FROM students ORDER BY id DESC
                    """
                ).fetchall()
        except sqlite3.Error as error:
            messagebox.showerror("Database error", str(error))
            return

        for student_id, *details in students:
            self.table.insert("", tk.END, iid=str(student_id), values=details)

    def delete_students(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select a student to delete.")
            return

        if not messagebox.askyesno(
            "Confirm deletion", "Delete the selected student(s)?"
        ):
            return

        try:
            with sqlite3.connect(DATABASE_PATH) as connection:
                connection.executemany(
                    "DELETE FROM students WHERE id = ?",
                    [(int(student_id),) for student_id in selected],
                )
        except sqlite3.Error as error:
            messagebox.showerror("Database error", str(error))
            return

        self.load_students()
        messagebox.showinfo("Deleted", "Selected student(s) deleted.")


def main():
    create_database()
    root = tk.Tk()
    StudentTrackingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
