from flask import Flask, request, render_template_string
import sqlite3
import hashlib


app = Flask(_name_)

DB_PATH = "users.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Create database table
def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        firstname Text,
                        lastname Text,
                        username TEXT UNIQUE,
                        password TEXT
                    )''')
    conn.commit()
    conn.close()

init_db()

# Registration Page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        firstname = request.form["first_name"]
        lastname = request.form["last_name"]

        # Hashing the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (firstname,lastname,username, password) VALUES (?,?,?,?)",
                         (firstname,lastname,username, hashed_password))
            conn.commit()
            message = "Registration successful!"
        except sqlite3.IntegrityError:
            message = "Username already exists."
        conn.close()
        return message

    return render_template_string("""
        <h1>Register</h1>
        <form method="POST">
        
                       
            firstname: <input type="text" name="first_name" required><br>
            lastname: <input type="text" name="last_name" required><br>
            Username: <input type="text" name="username" required><br>
            Password: <input type="password" name="password" required><br>
            <input type="submit" value="Register">
        </form>
    """)

# Login Page (Vulnerable to SQL Injection)
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db_connection()
        # Vulnerable SQL query
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{hashed_password}'"
        print(query)
        result = conn.execute(query).fetchone()
        conn.close()
        print(result)

            
        if result:
            first_name = result["firstname"]
            last_name = result["lastname"]
            return f"User is: {first_name} {last_name}"

        else:
            return "Login failed. Invalid credentials."

    return render_template_string("""
        <h1>Login</h1>
        <form method="POST">
            Username: <input type="text" name="username" required><br>
            Password: <input type="password" name="password" ><br>
            <input type="submit" value="Login">
        </form>
    """)

if _name_ == "_main":  # Corrected __main_
    app.run(debug=True)
