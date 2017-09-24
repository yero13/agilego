import logging
from db.connect import MongoDb
import abc
import pandas as pd


class Transformer():
    __CFG_KEY_TRANSFORMATION_SETS = 'transformation-sets'

    def __init__(self, cfg):
        self.__cfg = cfg
        self.__logger = logging.getLogger(__class__.__name__)

    def transform_data(self):
        for transform_set in self.__cfg[Transformer.__CFG_KEY_TRANSFORMATION_SETS]:
            self.__logger.info('Processing transformation set {}'.format(transform_set))
            TransformationSet(self.__cfg[Transformer.__CFG_KEY_TRANSFORMATION_SETS][transform_set]).transform_data()


class TransformationSet:
    __CFG_KEY_DB = 'db'
    __CFG_KEY_SRC_DB = 'src.db'
    __CFG_KEY_DEST_DB = 'dest.db'
    __CFG_KEY_TRANSFORMATIONS = 'transformations'

    def __init__(self, cfg):
        self.__cfg = cfg
        self.__logger = logging.getLogger(__class__.__name__)
        self.__src_db = MongoDb(
            self.__cfg[TransformationSet.__CFG_KEY_DB][TransformationSet.__CFG_KEY_SRC_DB]).connection
        self.__dest_db = MongoDb(
            self.__cfg[TransformationSet.__CFG_KEY_DB][TransformationSet.__CFG_KEY_DEST_DB]).connection

    def transform_data(self):
        for transformation in self.__cfg[TransformationSet.__CFG_KEY_TRANSFORMATIONS]:
            self.__logger.info('Processing transformation {}'.format(transformation))
            Transformation.factory(self.__cfg[TransformationSet.__CFG_KEY_TRANSFORMATIONS][transformation],
                                   self.__src_db, self.__dest_db).transform_data()


class Transformation:
    __CFG_KEY_TRANSFORMATIONS = 'transformations'
    __CFG_KEY_FIELDS = 'fields'
    __CFG_KEY_SRC_COLLECTION = 'src.collection'
    __CFG_KEY_DEST_COLLECTION = 'dest.collection'
    __CFG_KEY_TRANSFORMATION_TYPE = 'type'
    __CFG_KEY_TRANSFORMATION_CFG = 'cfg'

    __TYPE_SINGLE_OBJECT = 'single_object'

    @classmethod
    def factory(cls, cfg, src_db, dest_db):
        if cfg[Transformation.__CFG_KEY_TRANSFORMATION_TYPE] == Transformation.__TYPE_SINGLE_OBJECT:
            return SingleObjectTransformation(cfg[Transformation.__CFG_KEY_TRANSFORMATION_CFG], src_db, dest_db)

    def __init__(self, cfg, src_db, dest_db):
        self.__cfg = cfg
        self._logger = logging.getLogger(__class__.__name__)
        self._src_db = src_db
        self._dest_db = dest_db
        self._src_collection = self.__cfg[Transformation.__CFG_KEY_SRC_COLLECTION]
        self._dest_collection = self.__cfg[Transformation.__CFG_KEY_DEST_COLLECTION]
        self._transformations = self.__cfg[
            Transformation.__CFG_KEY_TRANSFORMATIONS] if Transformation.__CFG_KEY_TRANSFORMATIONS in self.__cfg else None
        self._fields = self.__cfg[Transformation.__CFG_KEY_FIELDS] if Transformation.__CFG_KEY_FIELDS in self.__cfg else None

    def __clean(self):
        self._dest_db[self._dest_collection].drop()

    @abc.abstractmethod
    def _load(self):
        return NotImplemented

    @abc.abstractmethod
    def _save(self):
        return NotImplemented

    @abc.abstractmethod
    def _transform(self):
        return NotImplemented

    def transform_data(self):
        self._load()
        if self._transformations:
            self._transform()
        self.__clean()
        self._save()


class SingleObjectTransformation(Transformation):
    def _load(self):
        self.__object = self._src_db[self._src_collection].find_one({}, {'_id': False})

    def _save(self):
        if self._fields:
            obj = {k:v for k,v in self.__object.items() if k in self._fields}
        else:
            obj = self.__object
        self._dest_db[self._dest_collection].insert_one(obj)

    def _transform(self):
        for transformation in self._transformations:
            obj = self.__object # for access from timeline
            exec(self._transformations[transformation])  # ToDo: change to compile/eval (need to add key as target in cfg)
