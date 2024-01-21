from flask import Flask, render_template, request, flash, redirect
import sqlite3
from datetime import datetime
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_FILE = "school.db"

# Function to create the database and tables
def create_database():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_number INTEGER PRIMARY KEY,
                name TEXT,
                nickname TEXT,
                age INTEGER,
                grade INTEGER,
                registration_date TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lessons (
                student_number INTEGER,
                lesson_name TEXT,
                FOREIGN KEY (student_number) REFERENCES students (student_number) ON DELETE CASCADE
            )
        ''')

        conn.commit()

# Function to execute SQL queries
def execute_query(query, parameters=None):
    with sqlite3.connect(DB_FILE, timeout=10) as conn:
        conn.execute('PRAGMA busy_timeout = 30000')  # Set busy timeout to 30 seconds
        cursor = conn.cursor()
        if parameters:
            if isinstance(parameters[0], tuple):  # Check if it's a list of tuples
                cursor.executemany(query, parameters)
            else:
                cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        conn.commit()

# Function to fetch data from the database
def fetch_data(query, parameters=None):
    with sqlite3.connect(DB_FILE, timeout=10) as conn:
        cursor = conn.cursor()
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        return cursor.fetchall()

# Extract lessons from the form and return as a list
def extract_lessons(form):
    lessons = form.get('lessons', '')
    return [lesson.strip() for lesson in lessons.split(',') if lesson.strip()]

def validate_and_convert_date(user_input):
    try:
        parsed_date = datetime.strptime(user_input, "%d/%m/%Y")
        formatted_date = parsed_date.strftime("%Y-%m-%d")
        return formatted_date
    except ValueError:
        return None

# Function to get validated input with date format conversion
def get_validated_input(prompt, is_text=True, is_date=False, default_value=None):
    while True:
        user_input = input(prompt)
        if is_text and not user_input.isdigit():
            return user_input
        elif not is_text and user_input.isdigit():
            return user_input
        elif is_date:
            formatted_date = validate_and_convert_date(user_input)
            if formatted_date:
                return formatted_date
            else:
                print("Invalid date format. Please enter a valid date (DD/MM/YYYY).")
        elif not is_text and (not user_input or user_input.isspace()):
            # Allow empty input for non-text fields (e.g., Enter to keep current value)
            return default_value
        print("Invalid input. Please enter a valid value.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_student', methods=['POST'])
def add_student():
    # Extract data from the form
    student_number = request.form['student_number']
    name = request.form['name']
    nickname = request.form['nickname']
    age = request.form['age']
    grade = request.form['grade']
    registration_date = request.form.get('registration_date')

    # Insert data into the database
    execute_query('INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)',
                  (student_number, name, nickname, age, grade, registration_date))

    # Process lessons
    lessons = extract_lessons(request.form)
    if lessons:  # Check if lessons are provided
        execute_query('INSERT INTO lessons (student_number, lesson_name) VALUES (?, ?)',
                      [(student_number, lesson) for lesson in lessons])
        flash("Student added successfully.", 'success')
    return render_template('index.html', message="Student added successfully.")

@app.route('/delete_student', methods=['GET', 'POST'])
def delete_student():
    if request.method == 'POST':
        student_number = request.form['student_number']
        # Check if the student exists
        existing_student = fetch_data('SELECT * FROM students WHERE student_number = ?', (student_number,))
        if not existing_student:
            flash("Student not found.", 'error')
            return redirect('/')

        # Perform the deletion operation in the database
        execute_query('DELETE FROM lessons WHERE student_number = ?', (student_number,))
        execute_query('DELETE FROM students WHERE student_number = ?', (student_number,))
        
        flash("Student deleted successfully.", 'success')
        return redirect('/')
    else:
        return render_template('delete_student.html')

@app.route('/update_student', methods=['POST'])
def update_student():
    if request.method == 'POST':
        student_number = request.form['student_number']
        name = request.form['name']
        nickname = request.form['nickname']
        age = request.form['age']
        grade = request.form['grade']
        registration_date = request.form.get('registration_date')

        # Convert the registration date format
        registration_date = validate_and_convert_date(registration_date)

        # Update the student information in the database
        execute_query('''
            UPDATE students
            SET name = ?, nickname = ?, age = ?, grade = ?, registration_date = ?
            WHERE student_number = ?
        ''', (name, nickname, age, grade, registration_date, student_number))

        # Clear existing lessons for the student
        execute_query('DELETE FROM lessons WHERE student_number = ?', (student_number,))

        # Update the lesson information in the database
        lessons = extract_lessons(request.form)
        if lessons:  # Check if lessons are provided
            # Insert new lessons into the database
            execute_query('INSERT INTO lessons (student_number, lesson_name) VALUES (?, ?)',
                          [(student_number, lesson) for lesson in lessons])

            flash("Student updated successfully.", 'success')
        return render_template('index.html', message="Student updated successfully.")
    else:
        return render_template('update_student.html')

@app.route('/view_student', methods=['POST'])
def view_student():
    if request.method == 'POST':
        student_number = request.form['student_number']
        # Fetch student information from the database
        student_info = fetch_data('SELECT * FROM students WHERE student_number = ?', (student_number,))
        if student_info:
            # Fetch lesson information from the database
            lessons = fetch_data('SELECT lesson_name FROM lessons WHERE student_number = ?', (student_number,))
            return render_template('index.html', view_student_info=student_info[0], view_lessons=lessons)
        else:
            return render_template('index.html', view_student_error="Student not found.")
    else:
        return render_template('index.html')
        if not student_info:
            return render_template('index.html', view_student_error="Student not found.")

if __name__ == '__main__':
    create_database()
    app.run(debug=True)


