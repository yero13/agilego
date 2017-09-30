==========
agilego.py
==========

Please refer https://github.com/yero13/agilego.ts/wiki for Agilego application functionality description and https://github.com/yero13/agilego.ts for frontend installation guide

============
Installation
============

*******
MongoDB
*******
- Install MongoDB https://www.mongodb.com/
- Run mongo https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/#run-mongodb-community-edition
- Create user agilego (currently Agilego works only with 1 superuser) https://docs.mongodb.com/v2.6/tutorial/add-user-administrator/

>>> mongo --port 27017
>>> use admin
>>> db.createUser(
>>>  {
>>>     user: "agilego",
>>>     pwd: "1",
>>>     roles: [ { role: "root", db: "admin" } ]
>>>  }
>>> )

*******
Python
*******
- Install Python 3.6.2 https://www.python.org/downloads/release/python-362/
- Download source dist archive https://github.com/yero13/agilego.py/tree/master/dist or corresponding branch
- pip install agilego-0.1.tar.gz

Dependencies
************
- pandas, jsonschema, requests, pymongo, flask, flask-cors, flask_cache

=============
Configuration
=============
Please refer https://github.com/yero13/agilego.py/wiki
