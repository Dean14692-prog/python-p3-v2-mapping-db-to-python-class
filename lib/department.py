import sqlite3

DB_NAME = 'company.db'

class Department:
    all = {}

    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name
        self.location = location

    @classmethod
    def get_connection(cls):
        return sqlite3.connect(DB_NAME)

    @classmethod
    def create_table(cls):
        with cls.get_connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                location TEXT
            )
            """)

    @classmethod
    def drop_table(cls):
        with cls.get_connection() as conn:
            conn.execute("DROP TABLE IF EXISTS departments")

    def save(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if self.id is None:
                cursor.execute(
                    "INSERT INTO departments (name, location) VALUES (?, ?)",
                    (self.name, self.location)
                )
                self.id = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE departments SET name = ?, location = ? WHERE id = ?",
                    (self.name, self.location, self.id)
                )
            conn.commit()
            Department.all[self.id] = self
        return self

    @classmethod
    def create(cls, name, location):
        department = cls(name, location)
        department.save()
        return department

    def update(self):
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE departments SET name = ?, location = ? WHERE id = ?",
                (self.name, self.location, self.id)
            )
            conn.commit()
        Department.all[self.id] = self

    def delete(self):
        if self.id is None:
            return
        with self.get_connection() as conn:
            conn.execute("DELETE FROM departments WHERE id = ?", (self.id,))
            conn.commit()
        Department.all.pop(self.id, None)
        self.id = None

    @classmethod
    def instance_from_db(cls, row):
        id, name, location = row
        dept = cls(name, location, id)
        cls.all[id] = dept
        return dept

    @classmethod
    def get_all(cls):
        with cls.get_connection() as conn:
            cursor = conn.execute("SELECT id, name, location FROM departments")
            rows = cursor.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        if id in cls.all:
            return cls.all[id]
        with cls.get_connection() as conn:
            cursor = conn.execute("SELECT id, name, location FROM departments WHERE id = ?", (id,))
            row = cursor.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    @classmethod
    def find_by_name(cls, name):
        with cls.get_connection() as conn:
            cursor = conn.execute("SELECT id, name, location FROM departments WHERE name = ?", (name,))
            row = cursor.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None
