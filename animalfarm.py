#For timestamps in comments  
import time

#For database commands
import sqlite3

#Microframework used for simple web application
from flask import Flask, request, session, g, redirect, url_for, \
	 abort, render_template, flash

#Used to close databases
from contextlib import closing

#Random class for choosing a random topic
import random

#OS to check port and change debug settings
import os


#Configuration
DATABASE = 'barn.db'
DEBUG = False
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'


#Creating our application 
app = Flask(__name__)
app.config.from_object(__name__)


#Homepage which redirects to a random number in the SQL database 			
@app.route('/')
def new_url():
	cur = g.db.execute('SELECT max(id) FROM topics')
	max_id = cur.fetchone()[0]
	if(max_id):
		page = random.randint(1,max_id)
	else:
		return redirect(url_for('new_post'))

	return redirect(url_for('pages' ,page_num = str(page)))


#Displays topic, text, and comments dynamically	
@app.route('/discussion/<page_num>')
def pages(page_num):
	pro = True

	page_num = int(page_num)
	
	session['topic_id'] = page_num
	session['current_page'] = request.path

	cur = g.db.execute('SELECT max(id) FROM topics')
	limit = cur.fetchone()[0]

	if page_num > limit:
		return redirect(url_for('invalid_topic'))


	cur = g.db.execute('SELECT title, text FROM topics WHERE id=:uid', {'uid': page_num})
	row = cur.fetchone()
	
	cur = g.db.execute('SELECT * FROM comments WHERE topicid=:uid', {'uid': page_num})
	commentList = cur.fetchall()

	return render_template('HomePage.html', row=row, comments=commentList, debug=DEBUG, pro=pro)


#The comment route implements the comment. Essentially redirects back to the
#discussion page at the end 
@app.route('/comment', methods=['POST'])
def comment():

	if not session.get('logged_in'):
		#send to login page, w/ topic number to redirect back
		return redirect(url_for('login'))
	else:
		#handle comment/add to db and send back to page
		cur = g.db.execute('SELECT * FROM comments WHERE userid=:uid', {'uid': session.get('user_id')})
		comments = cur.fetchall()

		if comments:
			animal_name = comments[0][2]
		else:
			animal_name = rand_animal_name()

		text = request.form['Response']
		if text != None:
			g.db.execute('INSERT INTO comments VALUES(?, ?, ?, ?, ?)', 
				(session.get('topic_id'), session.get('user_id'), animal_name, request.form['Response'], int(time.time())))
			g.db.commit()

		return redirect(session.get('current_page'))


#Routes to login redirects user back to page where they left off
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		username = request.form['user']
		password = request.form['pass']
	else:
		username = None
		password = None

	cur = g.db.execute('SELECT * FROM users WHERE main_username=:uid', {'uid': username})
	userList = cur.fetchone()
	if userList:
		if userList[2] == password:
			session['logged_in'] = True
			return redirect(url_for('pages', page_num=session.get('topic_id')))
		else:
			error = "There was an error in your submission."
			return render_template('Login.html', error=error)
	else:
		return render_template('Login.html', error=error)

@app.route('/logout')
def logout():
	session['logged_in'] = False
	return redirect(url_for('login'))

@app.route('/new', methods=['GET', 'POST'])
def new_post():
	if not session.get('logged_in'):
		#send to login page, w/ topic number to redirect back
		return redirect(url_for('login'))
	
	error = None

	if request.method == 'POST':
		#handle input and send
		title = request.form['Title']
		body = request.form['Body']

		if title == None or body == None:
			error = "Field cannot be left blank."
		else:
			g.db.execute('INSERT INTO topics VALUES(NULL, ?, ?)', (title, body))
			g.db.commit()

		cur = g.db.execute('SELECT max(id) FROM topics')
		max_id = cur.fetchone()[0]

		return redirect(url_for('pages', page_num=max_id))
	else:
		#show page and get input
		return render_template('NewTopic.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	error = None
	if request.method == 'POST':
		username = request.form['user']
		cur = g.db.execute("SELECT * FROM users WHERE main_username=:user", {'user':username})
		if cur.fetchone():
			error = "Username already taken."
		else:
			password1 = request.form['pass']
			password2 = request.form['pass_conf']
			if password1 == None or password2 == None:
				error = "Password cannot be blank"
			elif password1 == password2:
				g.db.execute("INSERT INTO users VALUES(NULL, ?, ?)", (username, request.form['pass']))
				g.db.commit()
				#Implement flash message to say user name sign up was successful 
				return redirect(url_for('login'))
			else:
				error = "Passwords did not match."
	return render_template('signup.html', error = error)

@app.route('/about')
def about():
	return render_template('About.html')

#Generates a random animal name
def rand_animal_name():
	with open('adjectives.txt') as f:
		adjectives = f.readlines()
		
	with open('animals.txt') as b:
		animals = b.readlines()

	s1 = random.choice(adjectives).title()
	s2 = random.choice(animals)


	strpre = s1 + s2 
	strfinal = strpre.replace("\n", " ")
	return strfinal


#Connects to database thru sqlite3 
def connect_db():
	return sqlite3.connect(app.config['DATABASE'])


#Connects to database at the beginning of each page request 
@app.before_request
def before_request():
	g.db = connect_db()
	#Possibly needs semicolon at end(?)
	g.db.execute('PRAGMA foreign_keys= ON')


#Closes database after each page request 
@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

#Exception when a user tries to access an out of bounds topic
@app.route('/invalid')
def invalid_topic():
	return 'This topic does not exist.'

#Error handler for dead links that aren't there
@app.errorhandler(404)
def page_not_found(error):
	return 'This page does not exist', 404


#Standard boilerplate for python main
if __name__ == '__main__':
	app.run()




