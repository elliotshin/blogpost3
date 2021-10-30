from flask import Flask, render_template, request, Blueprint, g, url_for, abort
import sqlite3 
 

def get_message_db():
	"""This function checks whether there is a database called message_db in the g attribute of the app. 
	If not, then connect to that database, ensuring that the connection is an attribute of g"""
	if 'message_db' not in g:
		g.message_db = sqlite3.connect('messages.sqlite') #connection established

		#query to create sqlite table
		messages_table_query = """ CREATE TABLE IF NOT EXISTS messages (
			id INTEGER,
			handle TEXT NOT NULL,
			message TEXT NOT NULL
		); """
		c = g.message_db.cursor()
		#creates sqlite table
		c.execute(messages_table_query)
		print("sqlite3 connected")
	# c = g.message_db.cursor()
	# c.execute("SHOW TABLES")
	# for x in c:
	# 	print(x)
	return g.message_db

def close_message_db(e = None):
	"""This method breaks the connection to the database and closes it"""
	db = g.pop('message_db', None) #popping the element releases the connection, if no database, return none 

	if db is not None:
		print("sqlite3 closed")
		db.close()


def insert_message(request):
	"""
	Extracts the message and the handle from request. 
	inserts the message into the message database
	"""
	handle = request.form['handle'] #user input for handle
	usermessage = request.form['usermessage'] #user input for message
	print(handle,usermessage)
	db = get_message_db() #opens connection
	c = db.cursor() # creates a cursor to enter a query command

	#checks to see how many rows there are, this is necessary to create an ID
	#for each submission 
	x = c.execute('SELECT COUNT(*) AS rows FROM messages') #get row count

	#retrieve row count, it is in form of tuple 
	test = x.fetchone()
	print(test)
	print(type(test)) #type: tuple, need to unpack
	(ID,) = test #tuple unpacked, stored in ID variable
	ID = ID + 1 #increment ID by one 
	print(ID)
	#question marks are substitutable values, stored in val variable
	insert_query = """INSERT OR IGNORE INTO messages (id,handle, message) VALUES (?,?,?)"""
	val = (ID, handle, usermessage)
	c.execute(insert_query,val)  
	print("executed order 66")

	# IMPORTANT: IN ORDER TO SAVE DATA, YOU MUST COMMIT IT
	# LIKE GITHUB
	db.commit() 
	print("db committed")
	print("finished insert_message method")

def random_messages(n):
	"""
	returns a collection of n random messages from the message_db, or fewer if necessary
	"""
	db = get_message_db();
	c = db.cursor();
	rows = c.execute('SELECT id FROM messages').fetchall()[-1]
	(rows,) = rows
	print(n,rows)
	if (rows < n):
		n = rows
		rando_query = """SELECT * FROM messages ORDER BY RANDOM() LIMIT ? """
		c.execute(rando_query,(n,))
	else:
		rando_query = """SELECT * FROM messages ORDER BY RANDOM() LIMIT ? """
		c.execute(rando_query,(n,))
	return c

app = Flask(__name__) 

@app.route("/")
def main():
	return render_template("main.html")
#controls what url the page you develop will have
#root directory

@app.route("/submit/", methods = ["POST", "GET"])
def submit():
	if request.method == "GET":
		return render_template("submit.html")
	if request.method == "POST":
		insert_message(request)
		print("message inserted") 
		return render_template("submit.html", handle = request.form["handle"], usermessage = request.form["usermessage"], thanks = True) 

@app.route("/view/")
def view():
	db = get_message_db()
	rand_messages = random_messages(5)
	messages = rand_messages.fetchall()
	return render_template('view.html', messages = messages) 
	



app.teardown_appcontext(close_message_db)