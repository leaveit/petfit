from flask import Flask, render_template, flash, request, url_for, redirect, session
from content_management import Content
from dbconnect import connection
from wtforms import Form, BooleanField, TextField, PasswordField, validators 
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
from functools import wraps
import gc

TOPIC_DICT = Content()

app = Flask(__name__)
app.secret_key = 'dev'

@app.errorhandler(404)
def page_not_found(e):
	flash('Not ready yet!')
	return render_template("404.html")

@app.route('/')
def frontpage():
	return render_template("frontpage.html")

@app.route('/dashboard/')
def dashboard():
	return render_template('dashboard.html', TOPIC_DICT = TOPIC_DICT)

def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash("you need to login first")
			return redirect(url_for('login_page'))
	return wrap

@app.route('/logout/')
@login_required
def logout():
	session.clear()
	flash("You have been logged out!")
	gc.collect
	return redirect(url_for('frontpage'))

@app.route('/login/', methods = ['GET', 'POST'])
def login_page():
	error = ''
	try:
		c, conn = connection()
		if request.method == "POST":
			data = c.execute("SELECT * FROM users WHERE email = (%s)", (thwart(request.form['email']),))
			data = c.fetchone()[2]

			if sha256_crypt.verify(request.form['password'], data):
				session['logged_in'] = True
				session['email'] = request.form['email']
				flash("You are now logged in")
				return redirect(url_for("dashboard"))
			else:
				error = "Invalid credentials, please try again"
		gc.collect() 
		return render_template("login.html", error = error)
	except Exception as e:
		flash(e)
		error = "Invalid credentials, please try again"
		return render_template("login.html", error = error)

class RegistrationForm(Form):
	email = TextField('Email Address', [validators.Length(min=4, max=50)])
	password = PasswordField('Password', [validators.Required(), validators.EqualTo('confirm', message="Passwords must match")])
	confirm = PasswordField('Repeat Password')
	accept_tos = BooleanField('I accept the <a href="/tos/">Terms of Service</a> and the <a href="/privacy/">Privacy Notice</a> (Last updated 2018.09.17)', [validators.Required()])

@app.route('/register/', methods = ['GET', 'POST'])
def register_page():
	try:
		form = RegistrationForm(request.form)
		if request.method == "POST" and form.validate():
			email = form.email.data
			password = sha256_crypt.encrypt((str(form.password.data)))
			c, conn = connection()
			x = c.execute("SELECT * FROM users WHERE email = (%s)", (thwart(email),))
			if int(x) > 0:
				flash("That email is already taken, please choose another")
				return render_template('register.html', form=form)
			else:
				c.execute("INSERT INTO users (email, password, tracking) VALUES (%s, %s, %s)", (thwart(email), thwart(password), thwart("/")))
				conn.commit()
				flash("Thanks for registering!")
				c.close()
				conn.close()
				gc.collect()
				session['logged_in'] = True
				session['email'] = email
				return redirect(url_for('dashboard'))
		return render_template("register.html", form=form)

	except Exception as e:
		return(str(e))

if __name__ == "__main__":
    app.debug = True
    app.run()
