
![chat](https://github.com/user-attachments/assets/e55d7f3e-225e-400a-a3c6-4f97c28fa8d7)

## Overview
This repository contains the implementation of a chatting application, aiming to connect people accross the world with a minimal appearance and features. Its environment is very similar to telegram and its core 
backend is implemented using django, and its frontend using raw html and css and js. 

## Key Features
- login and registeration of users
- sending request to other users and acceptance of other users (adding as friends)
- sending messages to friends, deleting (by clicking) and editing (by holding) messages
- creating groups and adding friends to them
- sending group messages, deleting (by clicking) and editing (by holding) group messages
- viewing last seen of friends and time stamps for messages
- sending images to friends and groups
- changing main theme of application

## Requirements
- Python 3.x
- Django
- Django-mathfilters

## Usage
```
git clone https://github.com/meysam-omidy/Chatting-Application-With-Django
python manage.py createsuperuser # to create admin user
python manage.py runserver
```
Then go to http://127.0.0.1:8000/ and perform registeration of new user or logging in to another account
