# Expensor

It is a simple and lite expense management web app that I developed for my personal use.

### Features:
- Add the expense with remark
- Search the data using remark or amount
- Expenses can be viewed Year-wise, Month-wise and Day-wise.
- Stats include total expense of all time, total expense of the current year, total expenses of present day, total expense of last and current month.
- Also a minimal income manager app comes with this app.
- and many more...

### System requirements:
- Python 3.8
- Redis

### How to install in local environment:

#### Docker:

**Make Migrations**
```
docker-compose run --rm web python manage.py makemigrations
```

**Apply Migrations**
```
docker-compose run --rm web python manange.py migrate
```

**Run**
```
docker-compose up
```

#### Manual setup:
* Clone the repository in your system then create a virtual envrironment (recommended), activate the virtual envrionment. Then run:

```
pip install -r requirements.txt
```

* Create a new file .env in the same directory as manage.py and set a variable with name DATABASE_URL_DEV to the database url.

* In this app I have used PostgreSQL, however you can use database of your choice, but just don't forget to install the driver for the same in your virtual environment.

* Create __init __.py file in *expensor > settings* and add below code in it.
```
from .development import *
```

* Make sure redis is up and running on you system

* Then run below commands.
```
python manage.py makemigrations
python manage.py migrate
```

Now your app is ready to run.
```
python manage.py runserver
```


#### ----------- Happy Coding -----------