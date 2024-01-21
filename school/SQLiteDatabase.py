# import sqlite3 module
import sqlite3

# connect to the database (this will create a new file if it doesn't exist)
conn = sqlite3.connect('school.db')

# create a cursor object to execute SQL commands
cursor = conn.cursor()

# create the students table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        student_number INTEGER PRIMARY KEY,
        name TEXT,
        nickname TEXT,
        age INTEGER,
        grade TEXT,
        registration_date TEXT
    )
''')

# create the lessons table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS lessons (
        student_number INTEGER,
        lesson_name TEXT,
        FOREIGN KEY (student_number) REFERENCES students(student_number)
    )
''')

# commit changes and close the connection
conn.commit()
conn.close()
