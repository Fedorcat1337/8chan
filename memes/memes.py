import sqlite3
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, session

def insert_meme(url, title, autor):
	
	conn = sqlite3.connect('memes.sqlite')
	c = conn.cursor()
	c.execute("INSERT INTO memes (url, title, time, autor_id) VALUES (?, ?, ?, ?)",(url, title, datetime.fromtimestamp(int(time.time())).strftime("%m/%d/%Y, %H:%M:%S"), autor))
	conn.commit()
	conn.close()

def fetchall_memes():

	conn = sqlite3.connect('memes.sqlite')
	c = conn.cursor()
	c.execute("SELECT * FROM memes ORDER BY id DESC")
	result = c.fetchall()
	conn.close()
	return result

def Search(title):
	
	conn = sqlite3.connect('memes.sqlite')
	c = conn.cursor()
	c.execute("SELECT * FROM memes WHERE title LIKE ? ORDER BY id DESC",('%' + title + '%',))
	result = c.fetchall()
	conn.close()
	return result

def delete_meme(id):

	conn = sqlite3.connect('memes.sqlite')
	c = conn.cursor()
	c.execute("SELECT * FROM memes WHERE id = ? and autor_id = ?",(id, session['user']))
	result = c.fetchall()
	if len(result) != 0:

		c.execute("DELETE FROM memes WHERE id = ?",(id,))
		c.execute("DELETE FROM comments WHERE meme_id = ?",(id,))
		conn.commit()
	conn.close()

def insert_comment(text, meme_id):
	
	conn = sqlite3.connect('memes.sqlite')
	c = conn.cursor()
	c.execute("INSERT INTO comments (text, meme_id, autor_id) VALUES (?, ?, ?)",(text, meme_id, session['user']))
	conn.commit()
	conn.close()	

def delete_comment(id):

	conn = sqlite3.connect('memes.sqlite')
	c = conn.cursor()
	c.execute("SELECT * FROM comments WHERE id = ? and autor_id = ?",(id, session['user']))
	result = c.fetchall()
	if len(result) != 0:
		c.execute("DELETE FROM comments WHERE id = ?",(id,))
		conn.commit()
	conn.close()

def fetchall_comments():

	conn = sqlite3.connect('memes.sqlite')
	c = conn.cursor()
	c.execute("SELECT * FROM comments")
	result = c.fetchall()
	conn.close()
	return result

def check_login(username, password):

	conn = sqlite3.connect('memes.sqlite')
	c = conn.cursor()
	c.execute("SELECT * FROM user_data WHERE username = ? AND password = ?",(username, password))
	result = c.fetchall()
	conn.close()
	if len(result) != 0:
		return True
	return False

def is_available(username):

	conn = sqlite3.connect('memes.sqlite')
	c = conn.cursor()
	c.execute("SELECT * FROM user_data WHERE username = ?",(username,))
	result = c.fetchall()
	if len(result) == 0:
		return True
	return False

def add_user(username, password):

	conn = sqlite3.connect("memes.sqlite")
	c = conn.cursor()
	c.execute("INSERT INTO user_data( username, password) VALUES (?, ?)",(username, password))
	conn.commit()
	conn.close()

def logout():
	del session['user']

app = Flask(__name__)
app.secret_key = b'1234567890123456789012345678901234567890123456789012345678234567823453456345672354563425678432qr45790[]243567890-0243567=rwqetwioypuowafdgsfgnmh,jk.j34y5u6tulibgvndrkngwerhijijijijijijijij'


@app.route("/sign_up", methods = ["get"])

def Sign_up():

	return render_template('sign_up.html')

@app.route("/sign_up", methods = ["post"])

def Sign_up2():

	username = request.form.get("username", "")
	password1 = request.form.get("password1", "")
	password2 = request.form.get("password2", "")
	if username != "" and password1 != "" and password2 != "":
		if password1 == password2:
			if is_available(username):
				add_user(username, password1)
				return redirect("/sign_in")

			else:
				error = "Это имя пользователя уже занято."
		else:
			error = "Пароли не совпадают."
	else:
		error = "Заполните все поля."

	return redirect("/sign_up")


@app.route("/sign_in", methods = ["get"])

def Sign_in():

	return render_template("sign_in.html")

@app.route("/sign_in", methods = ["post"])

def Sign_in2():

	username = request.form.get('username', '')
	password = request.form.get('password', '')

	if check_login(username, password) and username != '' and password != '':
		session['user'] = username
		return redirect("/")
	return redirect("/sign_in")



@app.route("/")

def Home():

	if 'user' not in session:

		return redirect("/sign_in")


	search = request.args.get('search', "")
	if search == "":

		memels = fetchall_memes()
		
		if len(memels) == 0:
			error = "Мемов пока нет. Будьте первым, кто оставит здесь запись."

		else:
			error = ""
	else: 

		memels = Search(search)

		if len(memels) == 0:
			error = "По вашему запросу ничего не найдено."
		
		else:
			error = ""

	commls = fetchall_comments()

	return render_template("index.html", memels = memels, commls = commls, username = session['user'])

@app.route("/add_meme", methods = ["get"])

def Add():

	if 'user' not in session:

		return redirect("/sign_in")

	return render_template("add.html")

@app.route("/add_meme", methods = ["post"])

def AddRed():
	
	if 'user' not in session:

		return redirect("/sign_in")

	url = request.form.get('url', "")
	title = request.form.get('title', "")
	autor = session["user"]
	
	if url != "" and title != "" and autor != None:

		insert_meme(url, title, autor)
		return redirect("/")
	
	else:
		
		error = "Перед отправкой заполните все поля."
		return redirect("/add_meme")

@app.route("/delete_meme")

def Delete():

	if 'user' not in session:

		return redirect("/sign_in")

	id = request.args.get('id', "")

	if id != "":

		delete_meme(id)
		return redirect("/")

	else:

		error = "Ошибка сервера"
		return redirect("/")

@app.route("/add_comment", methods = ["post"])
	
def Add_comment():

	if 'user' not in session:

		return redirect("/sign_in")
	
	text = request.form.get('text', "")
	meme_id = request.args.get('meme_id', "")

	if text != "" and meme_id != "":

		insert_comment(text, meme_id)
		return redirect("/")

	elif text == "":

		error = "Введите текст комментария."
		return redirect("/")

	else:

		error = "Ошибка сервера."
		return redirect("/")

@app.route("/delete_comment")

def Delete_comment():
	
	if 'user' not in session:

		return redirect("/sign_in")

	id  = request.args.get("id", "")

	if  id != "":
		delete_comment(id)

	else:
		error = "Ошибка сервера"
	
	return redirect("/")

@app.route("/log_out")

def Log_out():
	logout()
	return redirect("/sign_in")
	
app.run(debug = True)