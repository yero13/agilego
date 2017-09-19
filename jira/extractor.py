import logging
from db.connect import MongoDb
from jira.request import Request, SingleObjectRequest, MultiPageRequest


class Extractor():
    __CFG_KEY_DB = 'db'
    __CFG_KEY_REQUESTS = 'requests'
    __CFG_KEY_REQUEST_CFG_FILE = 'cfg'
    __CFG_KEY_REQUEST_TYPE = 'type'
    __CFG_KEY_REQUEST_DEST = 'dest'

    def __init__(self, cfg, login, pswd):
        self.__cfg = cfg
        self.__login = login
        self.__pswd = pswd
        self.__logger = logging.getLogger(__class__.__name__)
        self.__db = MongoDb(cfg[Extractor.__CFG_KEY_DB]).connection

    def extract(self):
        for request in self.__cfg[Extractor.__CFG_KEY_REQUESTS]:
            request_type = self.__cfg[Extractor.__CFG_KEY_REQUESTS][request][Extractor.__CFG_KEY_REQUEST_TYPE]
            request_cfg = self.__cfg[Extractor.__CFG_KEY_REQUESTS][request][Extractor.__CFG_KEY_REQUEST_CFG_FILE]
            request_dest = self.__cfg[Extractor.__CFG_KEY_REQUESTS][request][Extractor.__CFG_KEY_REQUEST_DEST]
            self.__db[request_dest].drop()
            if request_type == Request.TYPE_SINGLE_OBJECT:
                result = SingleObjectRequest(request_cfg, self.__login, self.__pswd).result
                self.__db[request_dest].insert_one(result)
                self.__logger.info('collection: {} data {} is saved'.format(request_dest, result))
            elif request_type == Request.TYPE_MULTI_PAGE:
                result = MultiPageRequest(request_cfg, self.__login, self.__pswd).result
                self.__db[request_dest].insert_many([item for item in result.values()])
                self.__logger.info('collection: {} {:d} items are saved'.format(request_dest, len(result.keys())))
            else:
                raise NotImplementedError('{} - request is not supported'.format(request_type))
            self.__db[request_dest].drop()
