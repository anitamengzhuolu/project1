#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver
To run locally
    python server.py
Go to http://localhost:8111 in your browser
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for
from flask.ext.wtf import Form  
from wtforms import StringField, SubmitField, RadioField
import datetime

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following uses the sqlite3 database test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@w4111db.eastus.cloudapp.azure.com/username
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@w4111db.eastus.cloudapp.azure.com/ewu2493"
#
DATABASEURI = "postgresql://yl3406:AXLLXZ@w4111db.eastus.cloudapp.azure.com/yl3406"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


class LoginForm(Form):
    username = StringField('username')
    usertype = RadioField('usertype')
    submit = SubmitField('Submit')

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request
  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:
  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2
  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT username FROM users")
  names = []
  for result in cursor:
    names.append(result['username'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another')
def another():
  return render_template("anotherfile.html")

MODEL_ID=0

#@app.route('/modeldetail')
@app.route('/modeldetail/<modeln>')
def modeldetail(modeln):
  global MODEL_ID
  MODEL_ID = modeln
  cursor = g.conn.execute("SELECT * FROM models WHERE id=(%s)",modeln)
  detail=[]
  for n in cursor:
   #print n
    detail.append(n)
  cursor.close()
  cursor1 = g.conn.execute("SELECT * FROM feedback_user_model WHERE id=(%s)",modeln)
  feedback=[]
  for n in cursor1:
    feedback.append(n)
  cursor1.close()
  cursor2 = g.conn.execute("SELECT * FROM assessment_expert,own WHERE own.aid=assessment_expert.aid and own.username=assessment_expert.username and own.id=(%s)",modeln)
  assessment=[]
  for n in cursor2:
    assessment.append(n)
  cursor2.close()
  cursor3 = g.conn.execute("SELECT * FROM link_list WHERE id=(%s)",modeln)
  links=[]
  for n in cursor3:
    links.append(n)
  cursor3.close()
  usersclick=[]
  for link in links:
    print link[1]
    cursor4 = g.conn.execute("SELECT username FROM visit_history WHERE url=(%s)",link[1])
    for n in cursor4:
      print n
      usersclick.append(n)
    cursor4.close()
  print usersclick
  context = dict(data = detail,feedback=feedback, assessment=assessment, links=links,usersclick=usersclick)
  return render_template('modeldetail.html',**context)

@app.route('/model')
def model():
  cursor = g.conn.execute("SELECT modelname, brand, id FROM models")
  model_info = []
  for result in cursor:
    #print result
    model_info.append(result)
  cursor.close()
  context = dict(data = model_info)
  return render_template("model.html", **context)

@app.route('/allusers')
def allusers():
  cursor = g.conn.execute("SELECT *  FROM users")
  names = []
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(data = names)
  return render_template("allusers.html", **context)

@app.route('/experts')
def experts():
  cursor = g.conn.execute("SELECT *  FROM expert")
  names = []
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(data = names)
  return render_template("experts.html", **context)

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
  return redirect('/')

@app.route('/findaddress', methods=['POST'])
def findaddress():
  username = request.form['username']
  #print username
  cursor = g.conn.execute("SELECT * FROM address_user WHERE username=(%s)",username)
  #print cursor
  if cursor == None:
    context = 'nouser'
    print "nouser"
  else:
    names = []
    for result in cursor:
      names.append(result)  # can also be accessed using result[0]
    cursor.close()
    context = dict(data = names)
  return render_template("addressofuser.html", **context)

#@app.route('/addressofuser')
#def addressofuser():
#  return render_template("addressofuser.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
#    global USERNAME,USERTYPE
#    form = LoginForm()
#    print 'hehe'
#    if form.validate_on_submit():
#      USERNAME=form.username.data
#      USERTYPE=form.usertype.data
#      cursor = g.conn.execute("SELECT * FROM users WHERE username=(%s)",USERNAME)
#      if cursor != None:
#        if USERTYPE=='expert':
#	  cursor1 = g.conn.execute("SELECT * FROM expert WHERE username=(%s)",USERNAME)
#          if cursor1 != None:
#            return redirect('/')
#          else:
#            return redirect('/')
    return render_template('login.html')
      
@app.route('/username', methods=['POST'])
def username():
  global USERNAME
  username = request.form['username']
  #g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
  cursor = g.conn.execute("SELECT * FROM users WHERE username=(%s)",username)
  result = []
  for i in cursor:
    result.append(i)
  l = len(result)
  if l != 0:
    USERNAME = result[0][0]
    print USERNAME
    return redirect('/')
  else:
    return render_template('login.html')

@app.route('/comment', methods=['POST'])
def comment():
  rating = request.form['rating']
  comment = request.form['comment']
  feedback_id = g.conn.execute('SELECT fid FROM feedback_user_model WHERE username=(%s) ORDER BY fid DESC LIMIT 1',USERNAME)
  mylist = []
  today = datetime.date.today()
  mylist.append(today)
  date = mylist[0]
  for i in feedback_id:
    feedid = i[0]
  feedid = int(feedid)+1
  g.conn.execute('INSERT INTO feedback_user_model VALUES (%s, %s, %s, %s, %s, %s)', (USERNAME, feedid, MODEL_ID, rating, comment, date))
  return redirect(url_for('modeldetail',modeln=MODEL_ID))

USERNAME='visitor'
if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using
        python server.py
    Show the help text using
        python server.py --help
    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
