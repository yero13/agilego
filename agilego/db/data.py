from db.connect import MongoDb
import logging
from utils.env import get_env_params


class Accessor:
    PARAM_KEY_TYPE = 'type'
    PARAM_TYPE_SINGLE = 'single'
    PARAM_TYPE_MULTI = 'multi'
    PARAM_KEY_COLLECTION = 'collection'
    PARAM_KEY_MATCH_PARAMS = 'match'
    PARAM_KEY_OBJECT = 'object'

    @staticmethod
    def factory(db):
        return Accessor(get_env_params()[db])

    def __init__(self, db):
        self._db = MongoDb(db).connection
        self._logger = logging.getLogger(__class__.__name__)

    def __get_single(self, collection, match_params=None):
        res = self._db[collection].find_one(match_params if match_params else {})
        if res:
            res['id'] = str(res['_id'])
            res.pop('_id', None)
        return res

    def __get_multi(self, collection, match_params=None):
        res = list(self._db[collection].find(match_params if match_params else {}))
        for item in res:
            item['id'] = str(item['_id'])
            item.pop('_id', None)
        return res

    def get(self, cfg):
        collection = cfg[Accessor.PARAM_KEY_COLLECTION]
        match_params = cfg[Accessor.PARAM_KEY_MATCH_PARAMS] if Accessor.PARAM_KEY_MATCH_PARAMS in cfg else None

        target_type = cfg[Accessor.PARAM_KEY_TYPE] if Accessor.PARAM_KEY_TYPE in cfg else Accessor.PARAM_TYPE_MULTI
        if target_type == Accessor.PARAM_TYPE_SINGLE:
            return self.__get_single(collection, match_params)
        elif target_type == Accessor.PARAM_TYPE_MULTI:
            return self.__get_multi(collection, match_params)

    def __delete_single(self, collection, match_params=None):
        return self._db[collection].delete_one(match_params).deleted_count

    def __delete_multi(self, collection, match_params=None):
        return self._db[collection].delete_many(match_params).deleted_count

    def delete(self, cfg):
        collection = cfg[Accessor.PARAM_KEY_COLLECTION]
        match_params = cfg[Accessor.PARAM_KEY_MATCH_PARAMS] if Accessor.PARAM_KEY_MATCH_PARAMS in cfg else {}

        target_type = cfg[Accessor.PARAM_KEY_TYPE] if Accessor.PARAM_KEY_TYPE in cfg else Accessor.PARAM_TYPE_MULTI
        if target_type == Accessor.PARAM_TYPE_SINGLE:
            return self.__delete_single(collection, match_params)
        elif target_type == Accessor.PARAM_TYPE_MULTI:
            return self.__delete_multi(collection, match_params)

    def __upsert_single(self, collection, object, match_params=None):
        return str(self._db[collection].update_one(match_params, {"$set": object}, upsert=True).upserted_id)

    def __upsert_multi(self, collection, object, match_params=None):
        raise NotImplementedError

    def upsert(self, cfg):
        object = cfg[Accessor.PARAM_KEY_OBJECT]
        collection = cfg[Accessor.PARAM_KEY_COLLECTION]
        match_params = cfg[Accessor.PARAM_KEY_MATCH_PARAMS] if Accessor.PARAM_KEY_MATCH_PARAMS in cfg else {}

        if cfg[Accessor.PARAM_KEY_TYPE] == Accessor.PARAM_TYPE_SINGLE:
            return self.__upsert_single(collection, object, match_params)
        elif cfg[Accessor.PARAM_KEY_TYPE] == Accessor.PARAM_TYPE_MULTI:
            return self.__upsert_multi(collection, object, match_params)
