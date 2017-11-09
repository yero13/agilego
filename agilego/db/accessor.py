from db.connect import MongoDb
import logging


class DataAccessor:
    CFG_KEY_TYPE = 'type'
    CFG_TYPE_SINGLE = 'single'
    CFG_TYPE_MULTI = 'multi'
    CFG_KEY_COLLECTION = 'collection'
    CFG_KEY_WHERE_PARAMS = 'where'
    CFG_KEY_OBJECT = 'object'

    def __init__(self, db):
        self.__db = MongoDb(db).connection
        self.__logger = logging.getLogger(__class__.__name__)

    def __get_single(self, collection, where_params=None):
        res = self.__db[collection].find_one(where_params if where_params else {})
        if res:
            res['id'] = str(res['_id'])
            res.pop('_id', None)
        return res

    def __get_multi(self, collection, where_params=None):
        res = list(self.__db[collection].find(where_params if where_params else {}))
        for item in res:
            item['id'] = str(item['_id'])
            item.pop('_id', None)
        return res

    def get(self, cfg):
        collection = cfg[DataAccessor.CFG_KEY_COLLECTION]
        where_params = cfg[DataAccessor.CFG_KEY_WHERE_PARAMS] if DataAccessor.CFG_KEY_WHERE_PARAMS in cfg else None

        if cfg[DataAccessor.CFG_KEY_TYPE] == DataAccessor.CFG_TYPE_SINGLE:
            return self.__get_single(collection, where_params)
        elif cfg[DataAccessor.CFG_KEY_TYPE] == DataAccessor.CFG_TYPE_MULTI:
            return self.__get_multi(collection, where_params)

    def __delete_single(self, collection, where_params=None):
        return self.__db[collection].delete_one(where_params).deleted_count

    def __delete_multi(self, collection, where_params=None):
        return self.__db[collection].delete_many(where_params).deleted_count

    def delete(self, cfg):
        collection = cfg[DataAccessor.CFG_KEY_COLLECTION]
        where_params = cfg[DataAccessor.CFG_KEY_WHERE_PARAMS] if DataAccessor.CFG_KEY_WHERE_PARAMS in cfg else {}

        if cfg[DataAccessor.CFG_KEY_TYPE] == DataAccessor.CFG_TYPE_SINGLE:
            return self.__delete_single(collection, where_params)
        elif cfg[DataAccessor.CFG_KEY_TYPE] == DataAccessor.CFG_TYPE_MULTI:
            return self.__delete_multi(collection, where_params)

    def __upsert_single(self, collection, object, where_params=None):
        return str(self.__db[collection].update_one(where_params, {"$set": object}, upsert=True).upserted_id)

    def __upsert_multi(self, collection, object, where_params=None):
        raise NotImplementedError

    def upsert(self, cfg):
        object = cfg[DataAccessor.CFG_KEY_OBJECT]
        collection = cfg[DataAccessor.CFG_KEY_COLLECTION]
        where_params = cfg[DataAccessor.CFG_KEY_WHERE_PARAMS] if DataAccessor.CFG_KEY_WHERE_PARAMS in cfg else {}

        if cfg[DataAccessor.CFG_KEY_TYPE] == DataAccessor.CFG_TYPE_SINGLE:
            return self.__upsert_single(collection, object, where_params)
        elif cfg[DataAccessor.CFG_KEY_TYPE] == DataAccessor.CFG_TYPE_MULTI:
            return self.__upsert_multi(collection, object, where_params)

