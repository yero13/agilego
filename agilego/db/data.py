from db.connect import MongoDb
import logging
import abc
import json
from utils.env import get_env_params
from utils.reflect import class_for_name

CFG_TRIGGERS = './cfg/dependency/triggers.json'


class CRUD:
    @staticmethod
    def read_single(db, collection, match_params=None):
       return db[collection].find_one(match_params if match_params else {}, {'_id': False})

    @staticmethod
    def read_multi(db, collection, match_params=None):
        return list(db[collection].find(match_params if match_params else {}, {'_id': False}))

    @staticmethod
    def delete_single(db, collection, match_params=None):
        return db[collection].delete_one(match_params).deleted_count

    @staticmethod
    def delete_multi(db, collection, match_params=None):
        return db[collection].delete_many(match_params).deleted_count

    @staticmethod
    def upsert_single(db, collection, object, match_params=None):
        return str(db[collection].update_one(match_params, {"$set": object}, upsert=True).upserted_id)

    @staticmethod
    def upsert_multi(db, collection, object, match_params=None):
        raise NotImplementedError


class Trigger:
    ACTION_BEFORE_DELETE = 'before-delete'
    ACTION_AFTER_DELETE = 'after-delete'
    ACTION_BEFORE_UPSERT = 'before-upsert'
    ACTION_AFTER_UPSERT = 'after-upsert'

    @staticmethod
    def factory(db, collection, action):
        with open(CFG_TRIGGERS) as triggers_cfg_file:
            triggers_cfg = json.load(triggers_cfg_file, strict=False) # ToDo: load once on startup
        if (collection in triggers_cfg) and (action in triggers_cfg[collection]):
            return class_for_name(triggers_cfg[collection][action])(db, collection)
        else:
            return None

    def __init__(self, db, collection):
        self._logger = logging.getLogger(__class__.__name__)
        self._db = db
        self._collection = collection

    @abc.abstractmethod
    def execute(self, input_object, match_params):
        return NotImplemented


class Accessor:
    PARAM_KEY_TYPE = 'type'
    PARAM_TYPE_SINGLE = 'single'
    PARAM_TYPE_MULTI = 'multi'
    PARAM_KEY_COLLECTION = 'collection'
    PARAM_KEY_MATCH_PARAMS = 'match'
    PARAM_KEY_OBJECT = 'object'

    OPERATOR_OR = '$or'

    @staticmethod
    def factory(db):
        return Accessor(get_env_params()[db])

    def __init__(self, db):
        self.__db = MongoDb(db).connection
        self.__logger = logging.getLogger(__class__.__name__)

    def __exec_trigger(self, action, collection, input_object, match_params):
        # ToDo: catch exception
        trigger = Trigger.factory(self.__db, collection, action)
        if trigger:
            self.__logger.info('exec trigger {} on {}'.format(action, collection))
            trigger.execute(input_object, match_params)

    def get(self, cfg):
        collection = cfg[Accessor.PARAM_KEY_COLLECTION]
        match_params = cfg[Accessor.PARAM_KEY_MATCH_PARAMS] if Accessor.PARAM_KEY_MATCH_PARAMS in cfg else None

        target_type = cfg[Accessor.PARAM_KEY_TYPE] if Accessor.PARAM_KEY_TYPE in cfg else Accessor.PARAM_TYPE_MULTI
        if target_type == Accessor.PARAM_TYPE_SINGLE:
            result = CRUD.read_single(self.__db, collection, match_params)
        elif target_type == Accessor.PARAM_TYPE_MULTI:
            result = CRUD.read_multi(self.__db, collection, match_params)
        return result

    def delete(self, cfg):
        collection = cfg[Accessor.PARAM_KEY_COLLECTION]
        match_params = cfg[Accessor.PARAM_KEY_MATCH_PARAMS] if Accessor.PARAM_KEY_MATCH_PARAMS in cfg else {}
        target_type = cfg[Accessor.PARAM_KEY_TYPE] if Accessor.PARAM_KEY_TYPE in cfg else Accessor.PARAM_TYPE_MULTI
        self.__exec_trigger(Trigger.ACTION_BEFORE_DELETE, collection, None, match_params)
        if target_type == Accessor.PARAM_TYPE_SINGLE:
            result = CRUD.delete_single(self.__db, collection, match_params)
        elif target_type == Accessor.PARAM_TYPE_MULTI:
            result = CRUD.delete_multi(self.__db, collection, match_params)
        self.__exec_trigger(Trigger.ACTION_AFTER_DELETE, collection, None, match_params)
        return result

    def upsert(self, cfg):
        input_object = cfg[Accessor.PARAM_KEY_OBJECT]
        collection = cfg[Accessor.PARAM_KEY_COLLECTION]
        match_params = cfg[Accessor.PARAM_KEY_MATCH_PARAMS] if Accessor.PARAM_KEY_MATCH_PARAMS in cfg else {}
        self.__exec_trigger(Trigger.ACTION_BEFORE_UPSERT, collection, input_object, match_params)
        if cfg[Accessor.PARAM_KEY_TYPE] == Accessor.PARAM_TYPE_SINGLE:
            result =  CRUD.upsert_single(self.__db, collection, input_object, match_params)
        elif cfg[Accessor.PARAM_KEY_TYPE] == Accessor.PARAM_TYPE_MULTI:
            result =  CRUD.upsert_multi(self.__db, collection, input_object, match_params)
        self.__exec_trigger(Trigger.ACTION_AFTER_UPSERT, collection, input_object, match_params)
        return result
