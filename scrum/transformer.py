import logging
from db.connect import MongoDb
import abc
import pandas as pd
import json


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

    # ToDo: define cached objects on this level(?)

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
    __CFG_KEY_TRANSFORMATION = 'transformation'
    __CFG_KEY_FIELDS = 'fields'
    __CFG_KEY_SRC_COLLECTION = 'src.collection'
    __CFG_KEY_DEST_COLLECTION = 'dest.collection'
    __CFG_KEY_TRANSFORMATION_TYPE = 'type'
    __CFG_KEY_TRANSFORMATION_CFG = 'cfg'

    __TYPE_SINGLE_OBJECT = 'single_object'
    __TYPE_DATASET = 'dataset'
    __TYPE_TRANSPOSE_ARRAY = 'transpose_array'

    @classmethod
    def factory(cls, cfg, src_db, dest_db):
        tranform_type = cfg[Transformation.__CFG_KEY_TRANSFORMATION_TYPE]
        if tranform_type == Transformation.__TYPE_SINGLE_OBJECT:
            return SingleObjectTransformation(cfg[Transformation.__CFG_KEY_TRANSFORMATION_CFG], src_db, dest_db)
        elif tranform_type == Transformation.__TYPE_DATASET:
            return DatasetTransformation(cfg[Transformation.__CFG_KEY_TRANSFORMATION_CFG], src_db, dest_db)
        elif tranform_type == Transformation.__TYPE_TRANSPOSE_ARRAY:
            return TransposeArrayTransformation(cfg[Transformation.__CFG_KEY_TRANSFORMATION_CFG], src_db, dest_db)
        else:
            raise NotImplementedError('Not supported transformation type - {}'.format(tranform_type))

    def __init__(self, cfg, src_db, dest_db):
        self.__cfg = cfg
        self._logger = logging.getLogger(__class__.__name__)
        self._src_db = src_db
        self._dest_db = dest_db
        self._src_collection = self.__cfg[Transformation.__CFG_KEY_SRC_COLLECTION]
        self._dest_collection = self.__cfg[Transformation.__CFG_KEY_DEST_COLLECTION]
        self._transformation = self.__cfg[
            Transformation.__CFG_KEY_TRANSFORMATION] if Transformation.__CFG_KEY_TRANSFORMATION in self.__cfg else None
        self._fields = self.__cfg[Transformation.__CFG_KEY_FIELDS] if Transformation.__CFG_KEY_FIELDS in self.__cfg else None

    def __cleanup(self):
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
        if self._transformation:
            self._transform()
        self.__cleanup()
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
        for transformation in self._transformation:
            obj = self.__object # for access from timeline
            exec(self._transformation[transformation])  # ToDo: change to compile/eval (need to add key as target in cfg)


class DatasetTransformation(Transformation):
    def _load(self):
        self.__dataset = list(self._src_db[self._src_collection].find({}, {'_id': False}))

    def _transform(self):
        dataset = pd.DataFrame.from_records(self.__dataset)
        for transformation in self._transformation:
            exec(self._transformation[transformation])  # ToDo: change to compile/eval (need to add key as target in cfg)
        self.__dataset = json.loads(dataset.T.to_json()).values()

    def _save(self):
        self._dest_db[self._dest_collection].insert_many(self.__dataset)


class TransposeArrayTransformation(Transformation):
    __CFG_KEY_L1KEY = 'l1key'
    __CFG_KEY_L2KEY = 'l2key'

    def _load(self):
        self.__l1key = self._transformation[TransposeArrayTransformation.__CFG_KEY_L1KEY]
        self.__l2key = self._transformation[TransposeArrayTransformation.__CFG_KEY_L2KEY]
        self.__dataset = list(
            self._src_db[self._src_collection].find({}, {self.__l1key: True, self.__l2key: True}))

    def _transform(self):
        return
        """
        dataset = pd.DataFrame.from_records(self.__dataset)
        for transformation in self._transformation:
            exec(self._transformation[transformation])  # ToDo: change to compile/eval (need to add key as target in cfg)
        self.__dataset = json.loads(dataset.T.to_json()).values()
        """

    def _save(self):
        self._dest_db[self._dest_collection].insert_many(self.__dataset)
