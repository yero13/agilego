from pymongo import MongoClient
import logging
import json


class MongoDb:
    # ToDo: implement pooling and singleton for connections
    __CFG_DB_CONNECT = '././cfg/db.json' # ToDo: move outside framework
    __CFG_PARAM_MONGO_DBNAME = 'MONGO_DBNAME'
    __CFG_PARAM_MONGO_HOST = 'MONGO_HOST'
    __CFG_PARAM_MONGO_PORT = 'MONGO_PORT'
    __CFG_PARAM_MONGO_USER = 'MONGO_USER'
    __CFG_PARAM_MONGO_PSWD = 'MONGO_PASSWORD'

    def __init__(self, cfg_db):
        self.__logger = logging.getLogger(__class__.__name__)
        with open(MongoDb.__CFG_DB_CONNECT) as cfg_file:
            cfg = json.load(cfg_file, strict=False)[cfg_db]
        self.__connection = MongoClient(
            'mongodb://{}:{}@{}:{:d}/'.format(cfg[MongoDb.__CFG_PARAM_MONGO_USER], cfg[MongoDb.__CFG_PARAM_MONGO_PSWD],
                                              cfg[MongoDb.__CFG_PARAM_MONGO_HOST],
                                              cfg[MongoDb.__CFG_PARAM_MONGO_PORT]))[
            cfg[MongoDb.__CFG_PARAM_MONGO_DBNAME]]
        self.__logger.debug('Mongo {} connection - instantiation'.format(cfg[MongoDb.__CFG_PARAM_MONGO_DBNAME]))

    @property
    def connection(self):
        return self.__connection
