from flask import Flask, request, session, redirect, url_for, render_template
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import re
from flask import flash
 
app = Flask(__name__)
 
# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'drashti'
 
   
# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'todousers'
mysql = MySQL(app)

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()

        cursor.execute('SELECT username, password FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[1], password):
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['username'] = user[0]
            # Redirect to home page
            return redirect('/index')
        else:
            # User doesn't exist or username/password is incorrect
            return 'Incorrect username/password!'

    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        encrypted_passwrod = generate_password_hash(password)
        cursor = mysql.connection.cursor()

        # Check if user exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()

        # If user exists, show error and validation checks
        if user:
            return 'User already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            return 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            return 'Please fill out the form!'
        else:
            # User doesn't exist, and the form data is valid, now insert new user into the users table
            cursor.execute('INSERT INTO users (username, fullname, email, password) VALUES (%s, %s, %s, %s)',
                           (username, fullname, email, encrypted_passwrod))
            mysql.connection.commit()
            cursor.close()

            return redirect('/')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        return 'Please fill out the form!'
    
    # Show registration form with message (if any)
    return render_template('register.html')

# @app.route('/index')
# def index():
#     if 'username' in session:
#         username = session['username']
#         cursor = mysql.connection.cursor()
#         cursor.execute("SELECT task_id, title, description, status FROM tasks WHERE username = %s", (username,))
#         data = cursor.fetchall()
#         cursor.close()
#         return render_template('home.html', tasks = data)
#     else:   
#         return render_template('home.html')
@app.route('/index')
def index():
    if 'username' in session:
        username = session['username']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT task_id, title, description, status FROM tasks WHERE username = %s", (username,))
        tasks = cursor.fetchall()
        cursor.close()

        # Print the value of 'data' to check if it's not empty
        print(tasks)

        return render_template('home.html', tasks=tasks)
    else:
        return render_template('home.html')

    
@app.route('/add_item', methods=['POST'])
def add_item():
    if request.method == 'POST':
        username = session['username']
        title = request.form['title']
        description = request.form['description']
        status = request.form['status']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO tasks (username,title, description,status) VALUES (%s,%s,%s,%s)", (username,title, description,status))
        mysql.connection.commit()
        cursor.close()
        flash('List Added successfully')
        return redirect(url_for('index'))
    
@app.route('/delete/<int:task_id>', methods=['GET','POST'])
def delete(task_id):
    username = session['username']
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM tasks WHERE task_id = %s AND username = %s", (task_id, username))
    mysql.connection.commit()
    cursor.close()
    flash('Deleted successfully')
    return redirect('/index')

@app.route('/edit/<int:task_id>', methods=['POST', 'GET'])
def edit(task_id):
    if request.method == 'POST':
        username = session['username']
        title = request.form['title']
        description = request.form['description']
        status = request.form['status']
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE tasks SET title = %s, description = %s, status = %s WHERE task_id = %s AND username = %s",
                    (title, description,status, task_id,username))
        mysql.connection.commit()
        cursor.close()
        print("done")
        return redirect('/index')
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
        task = cursor.fetchone()
        cursor.close()
        return render_template('edit.html', task=task)

@app.route('/logout')
def logout():
    session.pop('Username', None)
    return redirect('/')











if __name__ == '__main__':
    app.run(debug=True)