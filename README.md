# Expensor

It is a lite expense management web app that I developed for my personal use.

### Features:
- Add the expense with remark.
- Can set the date upto 7 days in the past.
- Search the data using remark or amount.
- Expenses can be viewed Year-wise, Month-wise and Day-wise.
- Stats include total expense of all time, total expense of the current year, total expenses of present day, total expense of last and current month.
- Also a minimal income manager app comes with this app.

### System requirements:
- Python 3.5
- Django 1.11.8
- virtualenv

### How to install app in local environment:

Clone the repository in your system then create a virtual envrironment (recommended), activate the virtual envrionment. Then run:

```
pip install -r requirements.txt
```

Create a new file .env in the same directory as manage.py and set a variable with name DATABASE_URL_DEV to the database url.

In this app I have used PostgreSQL, however you can use database of your choice, but just don't forget to install the driver for the same in your virtual environment.

Create __init __.py file in *expensor > settings* and add given code in it.
```
from .development import *
```
Then run commands given below.
```
python manage.py makemigrations
```
```
python manage.py migrate
```

Now your app is now ready to run.
```
python manage.py runserver
```


#### ----------- Happy Coding -----------
