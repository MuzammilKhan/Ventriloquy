# Ventriloquy Backend

### About
Django backend of Ventriloquy project. The site is currently using MySQL as
the database server. Since the database might only contain word name and the
path to the sound clip, sqlite can possibly be used.

### Dependencies
##### MySQL
Download from [here](https://dev.mysql.com/downloads/mysql/). Finish the installation according to different OS. Setup account and password for the database. **Change the db authentication setting in the file /mysite/mysite/my.cnf according to the account/password you just setup.** Now the website will use the database server on your machine.



##### Django
If you have `pip`, do this:
```
pip install Django==1.8.2 # the deployed version
```
or if not, download the source code from the [official website](https://www.djangoproject.com/download/) and do
```
python setup.py install
```
##### Python MySQL adaptor
Download from [here](http://www.djangoproject.com/r/python-mysql/). Untar the download package, cd into the package root folder and do
```
python setup.py install
```


### Run
In the website root directory (where the `manage.py` file is), do
```
python manage.py runserver
```
The server should be now running now and listening on localhost(127.0.0.1:8000).

To listen on different port, do the following instead:
```
python manage.py runserver 0.0.0.0:<your_port>
```
for development or
```
python manage.py runserver <your_port>
```
for nonlocal host.
