import abc
import logging
from db.data import Accessor, AccessParams
from utils.object import obj_for_name
import pandas as pd
from utils.converter import Converter


class Transformer():
    __CFG_KEY_TRANSFORMATION_SETS = 'transformation-sets'

    def __init__(self, cfg):
        self.__cfg = cfg
        self.__logger = logging.getLogger(__class__.__name__)

    def transform_data(self):
        for transform_set in self.__cfg[Transformer.__CFG_KEY_TRANSFORMATION_SETS]:
            self.__logger.info('Processing transformation set {}'.format(transform_set))
            TransformationSet(self.__cfg[Transformer.__CFG_KEY_TRANSFORMATION_SETS][transform_set]).perform()


class TransformationSet:
    __CFG_KEY_DB = 'db'
    __CFG_KEY_SRC_DB = 'src.db'
    __CFG_KEY_DEST_DB = 'dest.db'
    __CFG_KEY_TRANSFORMATIONS = 'transformations'

    def __init__(self, cfg):
        self.__cfg = cfg
        self.__logger = logging.getLogger(__class__.__name__)
        self.__src_db = self.__cfg[TransformationSet.__CFG_KEY_DB][TransformationSet.__CFG_KEY_SRC_DB]
        self.__dest_db = self.__cfg[TransformationSet.__CFG_KEY_DB][TransformationSet.__CFG_KEY_DEST_DB]

    def perform(self):
        for transformation in self.__cfg[TransformationSet.__CFG_KEY_TRANSFORMATIONS]:
            self.__logger.info('Processing transformation {}'.format(transformation))
            Transformation.factory(self.__cfg[TransformationSet.__CFG_KEY_TRANSFORMATIONS][transformation],
                                   self.__src_db, self.__dest_db).perform(
                self.__cfg[TransformationSet.__CFG_KEY_TRANSFORMATIONS][transformation][
                    Transformation.CFG_KEY_TRANSFORMATION_CFG])


class Transformation:
    __CFG_KEY_TRANSFORMATION = 'transformation'
    __CFG_KEY_TRANSFORMATION_CLASS = 'class'
    CFG_KEY_TRANSFORMATION_CFG = 'cfg'
    __CFG_KEY_LOAD = 'src.db.load'
    _CFG_KEY_LOAD_SRC = 'src'
    __CFG_KEY_TRANSFORM = 'transform'
    __CFG_KEY_CLEANUP = 'dest.db.cleanup'
    _CFG_KEY_CLEANUP_TARGET = 'target'
    __CFG_KEY_SAVE = 'dest.db.save'
    _CFG_KEY_SAVE_DEST = 'dest'
    _CFG_KEY_FUNC = 'func'
    _CFG_KEY_FUNC_PARAMS = 'params'

    @staticmethod
    def factory(cfg, src_db, dest_db):
        return obj_for_name(cfg[Transformation.__CFG_KEY_TRANSFORMATION_CLASS])(
            cfg[Transformation.CFG_KEY_TRANSFORMATION_CFG], src_db, dest_db)

    def __init__(self, cfg, src_db, dest_db):
        self.__cfg = cfg
        self._logger = logging.getLogger(__class__.__name__)
        self._src_db = src_db
        self._dest_db = dest_db
        self._transformation = self.__cfg[
            Transformation.__CFG_KEY_TRANSFORMATION] if Transformation.__CFG_KEY_TRANSFORMATION in self.__cfg else None

    @abc.abstractmethod
    def _cleanup(self, cfg):
        return NotImplemented

    @abc.abstractmethod
    def _load(self, cfg):
        return NotImplemented

    @abc.abstractmethod
    def _save(self, cfg):
        return NotImplemented

    @abc.abstractmethod
    def _transform(self, cfg):
        return NotImplemented

    def perform(self, cfg):
        self._load(cfg[Transformation.__CFG_KEY_LOAD])
        self._transform(cfg[Transformation.__CFG_KEY_TRANSFORM])
        self._cleanup(cfg[Transformation.__CFG_KEY_CLEANUP])
        self._save(cfg[Transformation.__CFG_KEY_SAVE])


class Doc2XTransformation(Transformation):
    def _load(self, cfg):
        self._src = Accessor.factory(self._src_db).get(
            {AccessParams.KEY_COLLECTION: cfg[Transformation._CFG_KEY_LOAD_SRC],
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE})

    def _transform(self, cfg):
        func = cfg[Transformation._CFG_KEY_FUNC]
        args = cfg[Transformation._CFG_KEY_FUNC_PARAMS] if Transformation._CFG_KEY_FUNC_PARAMS in cfg else {}
        self._res = obj_for_name(func)(self._src, args)

    def _cleanup(self, cfg):
        Accessor.factory(self._dest_db).delete(
            {AccessParams.KEY_COLLECTION: cfg[Transformation._CFG_KEY_CLEANUP_TARGET],
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE,
             AccessParams.KEY_MATCH_PARAMS: {}})


class Col2XTransformation(Transformation):
    def _load(self, cfg):
        self._src = Accessor.factory(self._src_db).get(
            {AccessParams.KEY_COLLECTION: cfg[Transformation._CFG_KEY_LOAD_SRC],
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI})

    def _transform(self, cfg):
        func = cfg[Transformation._CFG_KEY_FUNC]
        args = cfg[Transformation._CFG_KEY_FUNC_PARAMS] if Transformation._CFG_KEY_FUNC_PARAMS in cfg else {}
        self._res = obj_for_name(func)(self._src, args)

    def _cleanup(self, cfg):
        Accessor.factory(self._dest_db).delete(
            {AccessParams.KEY_COLLECTION: cfg[Transformation._CFG_KEY_CLEANUP_TARGET],
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI,
             AccessParams.KEY_MATCH_PARAMS: {}})


class Col2DocTransformation(Col2XTransformation):
    def _save(self, cfg):
        Accessor.factory(self._dest_db).upsert(
            {AccessParams.KEY_COLLECTION: cfg[Transformation._CFG_KEY_SAVE_DEST],
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE,
             AccessParams.KEY_OBJECT: self._res})


class Col2ColTransformation(Col2XTransformation):
    def _save(self, cfg):
        Accessor.factory(self._dest_db).upsert(
            {AccessParams.KEY_COLLECTION: cfg[Transformation._CFG_KEY_SAVE_DEST],
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI,
             AccessParams.KEY_OBJECT: self._res})


class Doc2DocTransformation(Doc2XTransformation):
    def _save(self, cfg):
        Accessor.factory(self._dest_db).upsert(
            {AccessParams.KEY_COLLECTION: cfg[Transformation._CFG_KEY_SAVE_DEST],
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE,
             AccessParams.KEY_OBJECT: self._res})


def transformer(func):
    def transformer_wrapper(input, params):
        return func(input, **params)
    return transformer_wrapper


@transformer
def singles2array(input, **params):
    PARAM_FIELD = 'field'

    res = []
    field = params.get(PARAM_FIELD)
    for item in input:
        res.append(item[field])
    return {field: res}


@transformer
def array2singles(input, **params):
    PARAM_FIELD_KEY = 'field.key'
    PARAM_FIELD_ARRAY = 'field.array'
    PARAM_FIELD_SINGLE = 'field.single'

    res = []
    field_key = params.get(PARAM_FIELD_KEY) if PARAM_FIELD_KEY in params else None
    field_array = params.get(PARAM_FIELD_ARRAY)
    field_single = params.get(PARAM_FIELD_SINGLE)
    for row in input:
        if row[field_array] and len(row[field_array]) > 0:
            for value in row[field_array]:
                res.append({field_single: value} if not field_key else {field_key: row[field_key], field_single: value})
    return res


@transformer
def filter_set(input, **params):
    PARAM_WHERE = 'where'

    return Converter.df2list(pd.DataFrame.from_records(input).query(params.get(PARAM_WHERE)))


@transformer
def sort_set(input, **params):
    return

@transformer
def copy(input, **params):
    PARAM_FIELDS = 'fields'

    def filter_fields(obj, fields):
        return {k:v for k,v in obj.items() if k in fields}

    if PARAM_FIELDS in params:
        fields = params.get(PARAM_FIELDS)
        if isinstance(input, list):
            res = []
            for row in input:
                res.append(filter_fields(row, fields))
            return res
        elif isinstance(input, dict):
            return filter_fields(input, fields)
        else:
            raise NotImplementedError('{} is not supported'.format(type(input)))
    else:
        return input
