import sqlite3
import sys
import random
import string
from datetime import datetime
from time import time

DB_NAME = "employees.db"

class EmployeeManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                birth_date TEXT NOT NULL,
                gender TEXT NOT NULL
            )
        """)
        self.conn.commit()
        print("Table created.")

    def add_employee(self, full_name, birth_date, gender):
        employee = Employee(full_name, birth_date, gender)
        self.cursor.execute(
            "INSERT INTO employees (full_name, birth_date, gender) VALUES (?, ?, ?)",
            (employee.full_name, employee.birth_date.strftime("%Y-%m-%d"), employee.gender)
        )
        self.conn.commit()
        print(f"Employee {full_name} added.")

    def list_employees(self):
        self.cursor.execute("""
            SELECT full_name, birth_date, gender FROM employees
            ORDER BY full_name
        """)
        rows = self.cursor.fetchall()
        for row in rows:
            name, birth_date, gender = row
            age = Employee(name, birth_date, gender).age()
            print(f"{name}, {birth_date}, {gender}, {age} years old")

    def fill_employees(self):
        genders = ["Male", "Female"]

        def random_name():
            return "".join(random.choices(string.ascii_uppercase, k=6))

        employees = [
            Employee(
                f"{random_name()} {random_name()} {random_name()}",
                f"{random.randint(1950, 2010)}-{random.randint(1, 12):02}-{random.randint(1, 28):02}",
                random.choice(genders)
            )
            for _ in range(999900)
        ]

        employees += [
            Employee(
                f"F{random_name()} {random_name()} {random_name()}",
                f"{random.randint(1950, 2010)}-{random.randint(1, 12):02}-{random.randint(1, 28):02}",
                "Male"
            )
            for _ in range(100)
        ]

        self.batch_insert(employees)
        print("1,000,000 employees added.")

    def batch_insert(self, employees):
        self.cursor.executemany(
            "INSERT INTO employees (full_name, birth_date, gender) VALUES (?, ?, ?)",
            [(e.full_name, e.birth_date.strftime("%Y-%m-%d"), e.gender) for e in employees]
        )
        self.conn.commit()

    def find_male_f(self):
        start_time = time()
        self.cursor.execute("""
            SELECT full_name, birth_date, gender FROM employees
            WHERE gender = 'Male' AND full_name LIKE 'F%'
        """)
        rows = self.cursor.fetchall()
        end_time = time()

        for row in rows:
            print(row)
        print(f"Query executed in {end_time - start_time:.4f} seconds.")

    def optimize(self):
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_gender_name ON employees (gender, full_name)")
        self.conn.commit()
        print("Optimization complete.")

    def close(self):
        self.conn.close()

class Employee:
    def __init__(self, full_name, birth_date, gender):
        self.full_name = full_name
        self.birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
        self.gender = gender

    def age(self):
        today = datetime.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

def main():
    if len(sys.argv) < 2:
        print("Usage: myApp.py <mode> [params]")
        return

    manager = EmployeeManager()
    mode = int(sys.argv[1])

    if mode == 1:
        manager.create_table()
    elif mode == 2:
        if len(sys.argv) != 5:
            print("Usage: myApp.py 2 <Full Name> <Birth Date> <Gender>")
            return
        manager.add_employee(sys.argv[2], sys.argv[3], sys.argv[4])
    elif mode == 3:
        manager.list_employees()
    elif mode == 4:
        manager.fill_employees()
    elif mode == 5:
        manager.find_male_f()
    elif mode == 6:
        manager.optimize()
    else:
        print("Invalid mode.")

    manager.close()

if __name__ == "__main__":
    main()
