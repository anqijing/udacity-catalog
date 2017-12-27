from flask import Flask, make_response, render_template, request, redirect, url_for, flash, jsonify, g, abort
from sqlalchemy import create_engine, distinct, or_, func, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Moviecategory, Movieitem, User
from flask_httpauth import HTTPBasicAuth
from flask import session as login_session
import random, os, json, requests, string, httplib2
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

app = Flask(__name__)

# load client secrets.json
CLIENT_ID = json.loads(
     open('client_secrets.json', 'r').read())['web']['client_id']

# Connect database and create database session
engine = create_engine('sqlite:///moviecatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# create user
def createUser(login_session):
    newUser = User(username=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

# get user 
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

# get user id
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# return json data for categories and corresponding items
@app.route('/catalog')
def catalogJSON():
	allcategories = session.query(Moviecategory).all()		
	return jsonify(Category=[i.serialize for i in allcategories])


@app.route('/')
@app.route('/index')
def index():
	# query all categories
	categories = session.query(Moviecategory).all()
	return render_template('index.html', categories=categories)

# show category and item list
@app.route('/catalog/<string:catalog_name>')
@app.route('/catalog/<string:catalog_name>/items')
def showcategory(catalog_name):
	categories = session.query(Moviecategory).all()
	category = session.query(Moviecategory).filter_by(name = catalog_name).first()
	movieitems = session.query(Movieitem).filter_by(category_name = catalog_name).all()
	print catalog_name
	return render_template('showcategory.html', categoryname= catalog_name, categories = categories, movieitems = movieitems)

# show specific item information
@app.route('/catalog/<string:catalog_name>/<string:catalog_item>')
def showitem(catalog_name, catalog_item):
	category = session.query(Moviecategory).filter_by(name = catalog_name).first()
	movieitem = session.query(Movieitem).filter_by(name = catalog_item).first()
	user_id = movieitem.user_id
	user = getUserInfo(user_id)
	return render_template('showitem.html', category = category, movieitem = movieitem, user = user)

# add new item
@app.route('/catalog/<string:catalog_name>/add', methods=['GET', 'POST'])
def addCategoryItem(catalog_name):
	if 'user_id' not in login_session:
		return redirect(url_for('login'))
	if request.method == 'POST':
		category = session.query(Moviecategory).filter_by(name = catalog_name).first()
		print login_session['user_id']
		user = getUserInfo(login_session['user_id'])
		if request.form['name'] and request.form['director'] and request.form['description']:
			name = request.form['name']
			print name
			director = request.form['director']
			description = request.form['description']
			movieitem = Movieitem(name=name, director=director, description=description, category_name=category.name, user=user)
			session.add(movieitem)
			session.commit()
			return render_template('showitem.html', category = category, movieitem = movieitem, user = user)
		else:
			return redirect(url_for('addCategoryItem'))
	else:
		return render_template('additem.html', catalog_name=catalog_name)

# edit item 
@app.route('/catalog/<string:catalog_name>/<string:catalog_item>/edit', methods=['GET', 'POST'])
def editCategoryItem(catalog_name, catalog_item):
	if 'username' not in login_session:
		return redirect(url_for('login'))
	category = session.query(Moviecategory).filter_by(name = catalog_name).first()
	movieitem = session.query(Movieitem).filter_by(name = catalog_item).first()
	user_id = movieitem.user_id
	user = getUserInfo(user_id)
	if user.id != login_session['user_id']:
		return redirect(url_for('login'))
	if request.method == 'POST':
		if request.form['name']:
			movieitem.name = request.form['name']
		if request.form['director']:
			movieitem.director = request.form['director']
		if request.form['description']:
			movieitem.description = request.form['description']
		session.add(movieitem)
		session.commit()
		return redirect(url_for('showitem', catalog_name= category.name, catalog_item=movieitem.name))
	else: 
		return render_template('edititem.html', catalog_name = category.name, user = user, catalog_item = catalog_item, movieitem=movieitem)

# delete item
@app.route('/catalog/<string:catalog_name>/<string:catalog_item>/delete', methods=['GET', 'POST'])
def deleteCategoryItem(catalog_name, catalog_item):
	# Check if user is logged in
	if 'username' not in login_session:
	    return redirect('/login')
	#category = session.query(Moviecategory).filter_by(name = catalog_name).first()
	if request.method == 'POST':
		movieitem = session.query(Movieitem).filter_by(name = catalog_item).first()
		user_id = movieitem.user_id
		user = getUserInfo(user_id)
		if user.id != login_session['user_id']:
			return redirect(url_for('login'))
		session.delete(movieitem)
		session.commit()
		return redirect(url_for('showcategory', catalog_name=movieitem.category_name, catalog_item=movieitem.name))
	else:
		return render_template('deleteitem.html', catalog_name=catalog_name, catalog_item=catalog_item)

# user login
@app.route('/login')
def login():
	# Create anti-forgery state token
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)

# log out
@app.route('/logout')
def logout():
	access_token = login_session.get('access_token')
	if access_token is None:
		response = make_response(
		json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	if result['status'] == '200':
		del login_session['access_token']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		response = make_response(json.dumps('Successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return redirect(url_for('index'))	
	else:
		response = make_response(json.dumps('Failed to revoke token for given user.', 400))
		response.headers['Content-Type'] = 'application/json'
		return response
		
# google sign in callback function
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    print "done!"
    return output

@app.route('/gdisconnect')
def gdisconnect():
	# Only disconnect a connected user.
	access_token = login_session.get('access_token')

	if access_token is None:
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]

	if result['status'] != '200':
	    # For whatever reason, the given token was invalid.
	    response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
	    response.headers['Content-Type'] = 'application/json'
	    return response

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)