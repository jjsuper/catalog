# Item Catalog App Project

Item catalog app is an application that provides a list of items within a variety of categories 
as well as provide a user registration and authentication system.
Registered users will have the ability to post, edit and delete their own items.

# Quickstart

Now type **python database_setup.py** to initialize the database.

Type **python lotsofitems.py** to populate the database with categories and items. (Optional)


#### Command Line

```
python database_setup.py
ptyhon lotsofitems.py
```

# Usage

Type **python application.py** to run the Flask web server. In your browser visit **http://localhost:8000** to view the item catalog app.
You should be able to view, add, and delete categories.
You should be able to view, add, edit and delete items.

#### Command Line

```
python application.py
```


# Website Overview

## catalog(homepage)

The homepage displays all current categories with the latest added items.

After logging in, a user has the ability to **add category**, and **add item** information. 

## category

Selecting a specific category shows you all the items available for that category.

After logging in, a user has the ability to **delete category** with all items that bolongs to this category. Users should be able to delete only those categories that they themselves have created.

## item

Selecting a specific item shows you specific information about that item.

After logging in, a user has the ability to **edit item**, and **delete item** information. Users should be able to modify only those items that they themselves have created.

## Flash

Flash is added to give feedback to users.

## JSON API

The application provides JSON endpoint. For example,

http://localhost:8000/catalog.json

http://localhost:8000/catalog/Soccer.json

http://localhost:8000/catalog/Hockey/Stick.json
