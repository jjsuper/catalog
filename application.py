from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item

app = Flask(__name__)

engine = create_engine('sqlite:///categoryitem.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()



@app.route('/catalog.json')
def cataglogJSON():
    categories = session.query(Category).all()
    category_dict = [c.serialize for c in categories]
    for c in range(len(category_dict)):
        items = [i.serialize for i in session.query(Item)
                    .filter_by(category_id=category_dict[c]["id"]).all()]
        if items:
            category_dict[c]["Item"] = items
    return jsonify(Category=category_dict)






@app.route('/')
@app.route('/catalog')
def cataglog():
    categories = session.query(Category)
    items = session.query(Item).order_by(Item.id.desc())
    return render_template(
        'catalog.html', categories = categories, items = items)

@app.route('/catalog/<string:category_name>/items')
def category(category_name):
    categories = session.query(Category)
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id)
    return render_template(
        'category.html', categories=categories, category=category, items=items)
    #return "Selecting a specific category shows you all the items available for that category."

@app.route('/catalog/<string:category_name>/<string:item_name>')
def item(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(category_id=category.id, name=item_name).one()
    return render_template(
        'item.html', item=item)
    #return "Selecting a specific item shows you specific information of that item."

@app.route('/catalog/new', methods=['GET', 'POST'])
def addItem():
    if request.method == 'POST':
        category = session.query(Category).filter_by(name=request.form['category_name']).one()
        if not category:
            category = Category(name=request.form['category_name'])
            session.add(category)
            session.commit()
        newItem = Item(name=request.form['name'], description=request.form['description'], category=category)
        session.add(newItem)
        session.commit()
        return redirect(url_for('category', category_name=category.name))
    else:
        return render_template('additem.html')
            
@app.route('/catalog/<string:category_name>/<string:item_name>/edit',
           methods=['GET', 'POST'])
def editItem(category_name, item_name):
    categories = session.query(Category)
    editItem = session.query(Item).filter_by(name=item_name).one()
    if request.method == 'POST':
        if request.form['name']:
            editItem.name = request.form['name']
        if request.form['description']:
            editItem.description = request.form['description']
        if request.form['category_id']:
            category_id = request.form['category_id']
            category = session.query(Category).filter_by(id=category_id).one()
            editItem.category = category
        session.add(editItem)
        session.commit()
        return redirect(url_for('category', category_name=category_name))
    else:
        return render_template('edititem.html', categories=categories, item=editItem)
    #return "edit item info"

@app.route('/catalog/<string:category_name>/<string:item_name>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
    itemToDelete = session.query(Item).filter_by(name=item_name).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('category', category_name=category_name))
    else:
        return render_template('deleteItem.html', category_name=category_name, item=itemToDelete)
    #return "delete item info"
    
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)