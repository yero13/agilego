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

    @staticmethod
    def factory(cfg, src_db, dest_db):
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
        self.__cleanup()
        if self._transformation:
            self._transform()
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
            obj = self.__object # for access from exec
            exec(self._transformation[transformation])  # ToDo: change to compile/eval (need to add key as target in cfg)


class DatasetTransformation(Transformation):
    __CFG_KEY_TRANSFORM_VALUES = 'transform_values'
    __CFG_KEY_TRANSFORM_WHERE = 'where'
    __CFG_KEY_TRANSFORM_ORDER = 'order'
    __CFG_KEY_ORDER_BY = 'by_column'
    __CFG_KEY_ORDER_SORT = 'sort_order'

    def _load(self):
        self.__dataset = list(self._src_db[self._src_collection].find({}, {'_id': False}))

    def _transform(self):
        self.__df_dataset = pd.DataFrame.from_records(self.__dataset)
        if DatasetTransformation.__CFG_KEY_TRANSFORM_VALUES in self._transformation:
            self.__transform_values()
        if DatasetTransformation.__CFG_KEY_TRANSFORM_WHERE in self._transformation:
            self.__transform_where()
        if DatasetTransformation.__CFG_KEY_TRANSFORM_ORDER in self._transformation:
            self.__transform_order()
        if self._fields:
            self.__df_dataset = self.__df_dataset[self._fields]
        self.__dataset = json.loads(self.__df_dataset.T.to_json()).values()

    def __transform_values(self):
        value_transformations = self._transformation[DatasetTransformation.__CFG_KEY_TRANSFORM_VALUES]
        #dataset = self.__df_dataset # dataset is required for access from exec
        dataset = self.__df_dataset.to_dict(orient='records')
        for transformation in value_transformations:
            for row in dataset: # row is required for exec
                exec(value_transformations[transformation]) # ToDo: compile, etc
        self.__df_dataset = pd.DataFrame.from_records(dataset)

    def __transform_where(self):
        self.__df_dataset = self.__df_dataset.query(
            self._transformation[DatasetTransformation.__CFG_KEY_TRANSFORM_WHERE])

    def __transform_order(self): # ToDo: move to corresponding API call
        order_cfg = self._transformation[DatasetTransformation.__CFG_KEY_TRANSFORM_ORDER]
        sort = order_cfg[
            DatasetTransformation.__CFG_KEY_ORDER_SORT] if DatasetTransformation.__CFG_KEY_ORDER_SORT in order_cfg else None
        order = order_cfg[DatasetTransformation.__CFG_KEY_ORDER_BY]
        if sort:
            self.__df_dataset[order] = self.__df_dataset[order].astype('category')
            self.__df_dataset[order].cat.set_categories(sort, inplace=True)
        self.__df_dataset.sort_values(by=order, inplace=True)

    def _save(self):
        self._dest_db[self._dest_collection].insert_many(self.__dataset)


class TransposeArrayTransformation(Transformation):
    __CFG_KEY_TKEY = 'key'
    __CFG_KEY_TVALUES = 'values'

    def _load(self):
        self.__field_key = self._transformation[TransposeArrayTransformation.__CFG_KEY_TKEY]
        self.__field_values = self._transformation[TransposeArrayTransformation.__CFG_KEY_TVALUES]
        self.__dataset = list(self._src_db[self._src_collection].find({}, {self.__field_key: True, self.__field_values: True, '_id': False}))

    def _transform(self):
        # ToDo: implement check - tvalues must be list type and tkey must not be list
        res = []
        for item in self.__dataset:
            if len(item[self.__field_values]) > 0: # No need to keep empty values
                for value in item[self.__field_values]:
                    res.append({item[self.__field_key]: value})
        self.__dataset = res

    def _save(self):
        self._dest_db[self._dest_collection].insert_many(self.__dataset)

