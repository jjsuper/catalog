from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import flash
from sqlalchemy import create_engine, DateTime
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from datetime import datetime
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(open(
                'client_secrets.json', 'r').read())['web']['client_id']

# Connect to Database and create database session
engine = create_engine('sqlite:///categoryitem.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Google CONNECT
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
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
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
    login_session['email'] = data['email']

    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'

    flash("Now logged in as %s" % login_session['username'])
    return output


# Google DISCONNECT
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
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
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
                                'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Facebook CONNECT
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = "https://graph.facebook.com/oauth/access_token?grant_type="
    url += "fb_exchange_token&client_id="
    url += "%s&client_secret=%s&fb_exchange_token=%s" % (
            app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = "https://graph.facebook.com/v2.8/me?access_token="
    url += "%s&fields=name,id,email" % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'

    flash("Now logged in as %s" % login_session['username'])
    return output


# Facebook DISCONNECT
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = "https://graph.facebook.com/"
    url += "%s/permissions?access_token=%s" % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('catalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('catalog'))


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# JSON API endpoint functions
@app.route('/catalog.json')
def catalogJSON():
    categories = session.query(Category).all()
    category_dict = [c.serialize for c in categories]
    for c in range(len(category_dict)):
        items = [i.serialize for i in session.query(Item).filter_by(
                    category_id=category_dict[c]["id"]).all()]
        if items:
            category_dict[c]["Item"] = items
    return jsonify(Category=category_dict)


@app.route('/catalog/<int:category_id>.json')
def categoryJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    category_json = category.serialize
    items = [i.serialize for i in session.query(Item).filter_by(
                category=category).all()]
    if items:
        category_json["Item"] = items
    return jsonify(Category=category_json)


@app.route('/catalog/<int:category_id>/<int:item_id>.json')
def itemJSON(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)


# Show catelog
@app.route('/')
@app.route('/catalog/')
def catalog():
    categories = session.query(Category).all()
    items = session.query(Item).order_by(Item.date.desc()).all()
    if 'username' not in login_session:
        return render_template('publiccatalog.html',
                               categories=categories, items=items)
    else:
        return render_template('catalog.html',
                               categories=categories, items=items)


# Show category
@app.route('/catalog/<int:category_id>/items')
def category(category_id):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id)
    creator = getUserInfo(category.user_id)
    if ('username' not in login_session or
            creator.id != login_session['user_id']):
        return render_template(
            'publiccategory.html', categories=categories, category=category,
            items=items)
    else:
        return render_template('category.html', categories=categories,
                               category=category, items=items)


# Show item
@app.route('/catalog/<int:category_id>/<int:item_id>')
def item(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(
           category_id=category_id, id=item_id).one()
    creator = getUserInfo(item.user_id)
    if ('username' not in login_session or
            creator.id != login_session['user_id']):
        return render_template('publicitem.html', item=item)
    else:
        return render_template('item.html', item=item)


# Add category
@app.route('/catalog/newcategory', methods=['GET', 'POST'])
def addCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name']:
            exist = session.query(Category).filter_by(
                        name=request.form['name']).scalar()
            if exist:
                category = session.query(Category).filter_by(
                    name=request.form['name']).one()
                return redirect(url_for(
                    'category', category_id=category.id))
            else:
                newCategory = Category(name=request.form['name'],
                                       user_id=login_session['user_id'])
                session.add(newCategory)
                session.commit()
                flash("You have successfully added %s." % newCategory.name)
                return redirect(url_for('category',
                                        category_id=newCategory.id))
        else:
            return redirect(url_for('catalog'))
    else:
        return render_template('addcategory.html')


# Delete category
@app.route('/catalog/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteCategory(category_id):
    categoryToDelete = session.query(Category).filter_by(
                        id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if categoryToDelete.user_id != login_session['user_id']:
        output = "<script>function myFunction() {alert('You are not authorized"
        output += " to delete this category. Please create your own category "
        output += "in order to delete.');}</script>"
        output += "<body onload='myFunction()''>"
        return output
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        flash("You have successfully deleted %s." % categoryToDelete.name)
        return redirect(url_for('catalog'))
    else:
        return render_template(
                'deleteCategory.html', category_id=category_id)


# Add item
@app.route('/catalog/newitem', methods=['GET', 'POST'])
def addItem():
    categories = session.query(Category).all()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        category = session.query(Category).filter_by(
                    id=request.form['category_id']).one()
        if request.form['name']:
            exist = session.query(Item).filter_by(
                     category=category, name=request.form['name']).scalar()
            if exist:
                item = session.query(Item).filter_by(
                        category=category, name=request.form['name']).one()
                redirect(url_for('item',
                                 category_id=category.id,
                                 item_id=item.id))
            else:
                newItem = Item(name=request.form['name'],
                               description=request.form['description'],
                               category=category, date=datetime.now(),
                               user_id=login_session['user_id'])
                session.add(newItem)
                session.commit()
                flash("You have successfully added %s." % newItem.name)
                redirect(url_for('item', category_id=category.id,
                                 item_id=newItem.id))
        return redirect(url_for('category', category_id=category.id))
    else:
        return render_template('additem.html', categories=categories)


# Edit item
@app.route('/catalog/<int:category_id>/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    categories = session.query(Category).all()
    editItem = session.query(Item).filter_by(id=item_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editItem.user_id != login_session['user_id']:
        output = "<script>function myFunction() {alert('You are not authorized"
        output += " to edit this item. Please create your own item in order to"
        output += " edit.');}</script><body onload='myFunction()''>"
        return output
    if request.method == 'POST':
        if request.form['name']:
            editItem.name = request.form['name']
        if request.form['description']:
            editItem.description = request.form['description']
        if request.form['category_id']:
            category_id = request.form['category_id']
            category = session.query(Category).filter_by(id=category_id).one()
            editItem.category = category
        editItem.date = datetime.now()
        session.add(editItem)
        session.commit()
        flash("You have successfully edited %s." % editItem.name)
        return redirect(url_for('item', category_id=editItem.category.id,
                                item_id=editItem.id))
    else:
        return render_template('edititem.html', categories=categories,
                               item=editItem)


# Delete item
@app.route('/catalog/<int:category_id>/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id).one()
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if itemToDelete.user_id != login_session['user_id']:
        output = "<script>function myFunction() {alert('You are not authorized"
        output += " to delete this item. Please create your own restaurant in "
        output += "order to delete.');}</script><body onload='myFunction()''>"
        return output
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("You have successfully deleted %s." % itemToDelete.name)
        return redirect(url_for('category', category_id=category_id))
    else:
        return render_template('deleteItem.html', category_id=category_id,
                               item=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
