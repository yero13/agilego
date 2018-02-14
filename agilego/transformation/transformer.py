import abc
import logging
from db.connect import MongoDb
from utils.object import class_for_name


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
    __CFG_KEY_TRANSFORMATION_CLASS = 'class'
    __CFG_KEY_TRANSFORMATION_CFG = 'cfg'

    @staticmethod
    def factory(cfg, src_db, dest_db):
        return class_for_name(cfg[Transformation.__CFG_KEY_TRANSFORMATION_CLASS])(
            cfg[Transformation.__CFG_KEY_TRANSFORMATION_CFG], src_db, dest_db)  # ToDo: wrap into try/catch
        '''
        if tranform_type == Transformation.__TYPE_SINGLE_OBJECT:
            return SingleObjectTransformation(cfg[Transformation.__CFG_KEY_TRANSFORMATION_CFG], src_db, dest_db)
        elif tranform_type == Transformation.__TYPE_DATASET:
            return DatasetTransformation(cfg[Transformation.__CFG_KEY_TRANSFORMATION_CFG], src_db, dest_db)
        elif tranform_type == Transformation.__TYPE_TRANSPOSE_FROM_ARRAY:
            return TransposeFromArrayTransformation(cfg[Transformation.__CFG_KEY_TRANSFORMATION_CFG], src_db, dest_db)
        elif tranform_type == Transformation.__TYPE_TRANSPOSE_TO_ARRAY:
            return TransposeToArrayTransformation(cfg[Transformation.__CFG_KEY_TRANSFORMATION_CFG], src_db, dest_db)
        elif tranform_type == Transformation.__TYPE_LEFT_JOIN:
            return LeftJoinTransformation(cfg[Transformation.__CFG_KEY_TRANSFORMATION_CFG], src_db, dest_db)
        elif tranform_type == Transformation.__TYPE_UPDATE_COLLECTION:
            return UpdateTransformation(cfg[Transformation.__CFG_KEY_TRANSFORMATION_CFG], src_db, dest_db)
        else:
            raise NotImplementedError('Not supported transformation type - {}'.format(tranform_type))
        '''

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

    @staticmethod
    def _filter_fields(obj, fields):
        return {k:v for k,v in obj.items() if k in fields}

