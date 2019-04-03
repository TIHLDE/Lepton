# TIHLDE API
TIHLDEs API is the API TIHLDE's webiste. The API is made using [Django](https://www.djangoproject.com/), a Python Web framework.

## Contents
1. [Basic info](#basic-info)
2. [Getting started](#getting-started)
3. [Todo](#todo)
4. [Future plans](#future-plans)
5. [Rules](#rules)


### Basic Info
THILDE's API is using following technologies
* [Django](https://www.djangoproject.com/)
* [Django Restframework](https://www.django-rest-framework.org/)

### Getting started

#### Installing
The API is written in python and requires python version 3.6 or higher to run. With python installed, do the
following to run the API:
```
git clone git@github.com:tihlde/API.git
cd API
```
**!NB** - You need have an mysql-driver installed on your computer to run this API!

##### Installing dependencies
The API dependencies are found in the _Pipfile_ which you can either install manually, or with
_pipenv_ installed, you can install all the dependencies from that file by doing the following:
```
pipenv install
```

##### Running the API
To run the API all you have to do is run the following line:
```
python manage.py runserver 0:8080
```

**!NB** - If you installed the dependencies using _pipenv_, you have to enter the shell first. Run the follwing line:
```
pipenv shell
```

##### Required Enviornment variables
For the API to run you have to configure some enviornment variables. These variables can for example be put in a
_.env_ file.
First:
```
DJANGO_SECRET = PUT_A_RANDOM_LONG_STRING_HERE
```

Next you havet to configure the environment variables for the database connection. The API is configured to use
a MYSQL database. Therefore, configure following database variables
```
DATABASE_HOST= HOST_URL
DATABASE_NAME= DATABASE_NAME
DATABASE_PASSWORD= PASSWORD
DATABASE_PORT= PORT (normally 3306)
DATABASE_USER= USERNAME
```

With the configurations above, the api should be able to run. But the API only has some email-functionality build in.
For the email functions to work, you also have to provide email-credentals and host in form of environment variables:
```
EMAIL_HOST= HOST_URL
EMAIL_PORT= PORT (normally 587)
EMAIL_USER= EMAIL_USER
EMAIL_PASSWORD= EMAIL_PASSWORD
```
