from flask import Flask, render_template, request, session, redirect, url_for
import flask_bootstrap
import flask
from flask_mysqldb import MySQL
import yaml

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
flask_bootstrap.Bootstrap(app)

# Configure DB
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)


@app.route('/login/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if session.get('username') is None:
            cur = mysql.connection.cursor()
            username = request.form.get('username')
            password = request.form.get('password')
            if cur.execute("SELECT * from User where username = %s and password = %s", [username, password]) > 0:
                user = cur.fetchone()
                # print(user)
                session['login'] = True
                session['username'] = user[6]
                session['firstName'] = user[4]
                session['lastName'] = user[5]
                mysql.connection.commit()
                cur.execute("UPDATE User SET active = 1 WHERE username = %s ", [username])
                mysql.connection.commit()
                # fetch all blogs
                result_value = cur.execute("SELECT * from Blog")
                if result_value > 0:
                    blogs = cur.fetchall()
                    return render_template("home.html", blogs=blogs)
                return render_template("home.html")
            else:
                flask.flash('Invalid username and password!', 'danger')
                return render_template('login.html')
        else:
            cur = mysql.connection.cursor()
            result_value = cur.execute("SELECT * from Blog")
            if result_value > 0:
                blogs = cur.fetchall()
                return render_template("home.html", blogs=blogs)
            return render_template("home.html")
    else:
        if session.get('username') is not None:
            cur = mysql.connection.cursor()
            result_value = cur.execute("SELECT * from Blog")
            if result_value > 0:
                blogs = cur.fetchall()
                return render_template("home.html", blogs=blogs)
        else:
            return render_template("login.html")
    return render_template("login.html")


@app.route('/logout/')
def logout():
    if session.get('username') is not None:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE User SET active = 0 WHERE username = %s ", [session['username']])
        mysql.connection.commit()
        session.pop('username')
        return render_template('index.html')
    else:
        return render_template('index.html')


@app.route('/')
def home():
    if session.get('username') is None:
        return render_template("index.html")
    else:
        cur = mysql.connection.cursor()
        result_value = cur.execute("SELECT * from Blog")
        if result_value > 0:
            blogs = cur.fetchall()
            return render_template("home.html", blogs=blogs)
        return render_template("home.html")


@app.route('/registration/', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        username = request.form.get('username')
        password = request.form.get('password')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password_confirm = request.form.get('passwordConfirm')
        if password == password_confirm:
            if (cur.execute("SELECT * from User where username = %s", [username]) == 0) and len(username) >= 5:
                if cur.execute("SELECT * from User where email = %s", [email]) == 0:
                    cur.execute("INSERT INTO User(firstname,lastname,email,password,username) VALUES (%s,%s,%s,%s,%s)",
                                [firstname, lastname, email, password, username])
                    mysql.connection.commit()
                    cur.close()
                    flask.flash('Registration successful! Please login.', 'success')
                    return redirect(url_for('index'))
                else:
                    flask.flash('Email exists!', 'danger')
                    return render_template("registration.html")
            else:
                flask.flash('Username exists!', 'danger')
                return render_template("registration.html")
        else:
            flask.flash('Password error!')
            return render_template("registration.html")
    return render_template("registration.html")


@app.route('/blog/<int:id>')
def blog(id):
    if session.get('username') is None:
        return render_template("index.html")
    else:
        cur = mysql.connection.cursor()
        result_value = cur.execute("SELECT * from Blog WHERE idBlog = %s ", [id])
        if result_value > 0:
            b = cur.fetchone()
            return render_template("blog.html", blog=b)
        return render_template("home.html")


@app.route('/blog/', methods=['GET', 'POST'])
def create_blog():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        title = request.form.get('title')
        body = request.form.get('body')
        author = session.get('firstName') + ' ' + session.get('lastName')
        picture = request.form.get('picture')
        cur.execute("INSERT INTO Blog(title,body,author,picture) VALUES (%s,%s,%s,%s)",
                    [title, body, author, picture])
        mysql.connection.commit()
        cur.close()
        flask.flash('Blog created!', 'success')
        return redirect(url_for('home'))
    else:
        return render_template("createBlog.html")

@app.errorhandler(404)
def invalid_route(e):
    return render_template("404.html")
