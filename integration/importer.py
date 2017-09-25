import logging
from db.connect import MongoDb
from integration.request import ImportRequest


class Importer():
    __CFG_KEY_DB = 'db'
    __CFG_KEY_REQUESTS = 'requests'
    __CFG_KEY_REQUEST_CFG_FILE = 'cfg'
    __CFG_KEY_REQUEST_TYPE = 'type'
    __CFG_KEY_REQUEST_DEST = 'dest'
    __CFG_KEY_MAPPING = 'mapping'

    def __init__(self, cfg, login, pswd):
        self.__cfg = cfg
        self.__login = login
        self.__pswd = pswd
        self.__logger = logging.getLogger(__class__.__name__)
        self.__db = MongoDb(cfg[Importer.__CFG_KEY_DB]).connection

    def import_data(self):
        mappings = self.__cfg[
            Importer.__CFG_KEY_MAPPING] if Importer.__CFG_KEY_MAPPING in self.__cfg else None
        for request in self.__cfg[Importer.__CFG_KEY_REQUESTS]:
            request_type = self.__cfg[Importer.__CFG_KEY_REQUESTS][request][Importer.__CFG_KEY_REQUEST_TYPE]
            request_cfg = self.__cfg[Importer.__CFG_KEY_REQUESTS][request][Importer.__CFG_KEY_REQUEST_CFG_FILE]
            request_dest = self.__cfg[Importer.__CFG_KEY_REQUESTS][request][Importer.__CFG_KEY_REQUEST_DEST]
            self.__db[request_dest].drop()
            result = ImportRequest.factory(request_cfg, self.__login, self.__pswd, request_type, mappings).result
            self.__logger.debug(result)
            if isinstance(result, dict):
                res = self.__db[request_dest].insert_one(result)
                self.__logger.info('collection: {} data {} is saved'.format(request_dest, result))
            elif isinstance(result, list):
                self.__db[request_dest].insert_many([item for item in result])
                self.__logger.info('collection: {} {:d} items are saved'.format(request_dest, len(result)))
            else:
                raise NotImplementedError('{} - request is not supported'.format(request_type))

