# TIHLDE API
TIHLDEs API is the API TIHLDE's webiste. The API is made using [Django](https://www.djangoproject.com/), a Python Web framework.

## Contents
1. [Basic info](#basic-info)
2. [Getting started](#getting-started)
3. [Database Map (ER-Model)](#database-map)
4. [Authentication Flow](#authentication-flow)
5. [Authorization Flow](#authorization-flow)


### Basic Info
THILDE's API is using following technologies
* [Django](https://www.djangoproject.com/)
* [Django Restframework](https://www.django-rest-framework.org/)

### Getting started

#### Setup
The API is written in python and requires python version 3.6 or higher to run. With python installed, do the
following to run the API:
```
git clone git@github.com:tihlde/API.git
cd API
```
**!NB** - You need have an mysql-driver installed on your computer to run this API!

#### Installing dependencies
The API dependencies are found in the _Pipfile_ which you can either install manually, or with
_pipenv_ installed, you can install all the dependencies from that file by doing the following:
```
pipenv install
```

#### Running the API
To run the API all you have to do is run the following line:
```
python manage.py runserver 0:8080
```

**!NB** - If you installed the dependencies using _pipenv_, you have to enter the shell first. Run the follwing line:
```
pipenv shell
```

#### Required Enviornment variables
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

### Database Map (Simplified ER-Model)
![ER-model](https://user-images.githubusercontent.com/31648998/55506006-b4149480-5654-11e9-8a17-0c8d6d48ac64.png)

### Authentication Flow
All the TIHLDE's members are stored in a different system of TIHLDE. This means that this API does not handle user authentication.
Instead the API communicates with a different running API for handling user authentication, called [WebAuth]. So the flow can be described as below:
(https://github.com/tihlde/WebAuth).
![AuthenticationFlow](https://user-images.githubusercontent.com/31648998/55506395-9d227200-5655-11e9-8471-0d4384151e41.png)
The API also talks to [WebAuth](https://github.com/tihlde/WebAuth) for verifying the token.


### Authorization Flow
To know if a member is authorized to for example post new events or jobposts, we need to know if that member is a part of a "Undergruppe" or "Komitee" that is authorized to do so. For example should a member of Promo or HS be able to post new events. This done by _connecting_ a TIHLDE-userId with a "Undergruppe" or "Komitee". There are tables in the database for this, called _Group_ and _Connection_. All authorization is handled with Django-premissions.
![](https://user-images.githubusercontent.com/31648998/55507277-94cb3680-5657-11e9-88b5-b09b73a24a62.png)
