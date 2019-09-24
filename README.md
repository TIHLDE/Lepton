# TIHLDE API
TIHLDEs API is the API TIHLDE's webiste. The API is made using [Django](https://www.djangoproject.com/), a Python Web framework.
[![Build Status](https://travis-ci.org/tihlde/API.svg?branch=master)](https://travis-ci.org/tihlde/API)
## Contents
1. [Basic info](#basic-info)
2. [Getting started](#getting-started)
3. [Database Map (ER-Model)](#database-map)
4. [Authentication Flow](#authentication-flow)
5. [Authorization Flow](#authorization-flow)
6. [Tutorial](#tutorial)


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
**!NB** - You need have an **mysql-driver** installed on your computer to run this API!

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

**IN PRODUCTION** you have to set an extra environment variable to set debug-mode to false. This is done my doing the following:
```
PROD=True
```

#### Missing static folder ####
If you are not able to run the API or are getting lots of 500 errors with the configuration over it might be because you are missing the static folder. In the root of the project create a folder named _staticfiles_ and run the command:
```
python manage.py collectstatic
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

### Tutorial
Django and Django Restframework is a very abstract framework, and is very difficult to understand for beginners. Therefore, here is a simple tutorial showing how to create a simple entity, a Todo item. It is a good idea to do this tutorial in a seperate Django project.

**!NB** The tutorial does not include all imports, so you have to deal with this yourself.

#### 1. Creating an Todo model
First we need to describe how the Todo-entity should look like. This description will be used by Django to generate a table in the database. Open the _models.py_ file and write the following:
![Entity](https://user-images.githubusercontent.com/31648998/55508062-5c2c5c80-5659-11e9-9ffd-9639e9df0cd9.png)

#### 2. Auto-generate endpoints
For creating the basic CRUD-endpoints (GET, POST, PUT, PATCH and DELETE) for the Todo-entity we have to tell Django to auto-generate them. Open the _views.py_ file and write the following: 

![View](https://user-images.githubusercontent.com/31648998/55508726-c396dc00-565a-11e9-847a-78f60b88c4fe.png)
By making a class inheriting django.viewsets.ModelViewSet, Django will auto-generate the wanted endpoints. But you can see we are setting something called a _serializer_class_ equal to _TodoSerializer_. What is a serializer?

#### 3. Model serializiation
When the website sends data to the API, the data is most likely in the form of JSON. But the API is writtin in python and does not support JSON-format in the language, like in Javascript. This means Django have to convert the data from JSON-format to a valid python format (and the other way around). This is done by something called a _Serializer_. In Django we just simply have to create a Serializer-Class, and tell it which Model to serializer.

Open _serializers.py_ and write the following: 

![Serializers](https://user-images.githubusercontent.com/31648998/55508839-fc36b580-565a-11e9-95a9-73a77b23fc43.png)

#### 4. Specifying a route to your endpoints
So far you have created a _view_ for auto-generating endpoints, but you have to specify the route for the clients to go to for accessing these endpoints. Open _urls.py_ and write the following: 

![Url-registration](https://user-images.githubusercontent.com/31648998/55509086-9ac31680-565b-11e9-8b16-410658bab256.png)

#### 5. Migrating the changes to your database

**IT IS SUPER IMPORTANT THAT YOU DON'T DO THIS IN THE API PROJECT! MIGRATION-FILES DESCRIBES HOW THE DATABASE SHOULD LOOK LIKE, AND YOU DON'T WANT TO APPLY THESE CHANGES TO THE PRODUCTION DATABASE...AT ALL! CONFIGURE THE DJANGO PROJECT WITH YOUR OWN SEPERATE DATABASE BEFORE YOU PROCEED!**

You have earlier created a Model-entity call Todo. This entity needs to be added to the database, and this is done by telling Django to do so. Django uses something called _migrations_. Migrations are just files that describes how the database looks like, and Django generates these files by looking at the Models you have created in the _models.py_ file. To generate these files, run the following command:
```
python manage.py makemigrations
```

When the migration-files are created, you have to tell Django to use these files to change the database based on how the migrations look like. To do so, run the following command:
```
python manage.py migrate
```

**IF YOU DID THIS ON THE PRODUCTION SERVER...THEN YOU ARE DEAD! YOU WILL BE FIRED AND HATED FOR THE REST OF YOUR LIFE! (This is just a hint for telling you that you should not do this on the production database)**

#### 6. Enjoy life
That's it! If you run the django project by running the command "_python manage.py runserver 0:8080_" and open the link "_http://localhost:8080/api/v1/todo_" (depends on your url-configuration) you will be able to see, edit and delete data.

Congratulations, your are set!

#### 7. Expand your knownledge
To learn more, start looking at the official documentation for Django and Django Rest-framework:
* [Django](https://www.djangoproject.com/)
* [Django Rest-framework](https://www.django-rest-framework.org/)
