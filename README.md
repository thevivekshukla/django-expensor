# Expensor

It is a simple and lite expense management web app that I developed for my personal use.

### Features:
- Add the expense with remark
- Search the data using remark or amount
- Expenses can be viewed Year-wise, Month-wise and Day-wise.
- Stats include total expense of all time, total expense of the current year, total expenses of present day, total expense of last and current month.
- Also a minimal income manager app comes with this app.
- and then some more features around above things...

### System requirements:
- Docker

### How to install in local environment:

#### Docker:

Use `example.env` file to create .env file at root level. Update .env vars as per your deployment environment.

**Make Migrations**
```
docker compose run --rm web python manage.py makemigrations
```

**Apply Migrations**
```
docker compose run --rm web python manange.py migrate
```

**Collect Static Assets**
```
docker compose run --rm web python manange.py collectstatic
```

**Create Superuser**
```
docker compose run --rm web python manange.py createsuperuser
```

**Run**
```
docker compose up --build --remove-orphans
```
Use `--detach` to run in the background.

**Stop**
```
docker compose down --remove-orphans
```
Use `-v` to also remove the volumes data.


#### ----------- Happy Coding -----------