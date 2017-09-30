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
