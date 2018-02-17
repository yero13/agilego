import abc
import logging
from db.data import Accessor, AccessParams
from utils.object import obj_for_name
import pandas as pd
from utils.converter import Converter
import re


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


class MultiCol2XTransformation(Transformation):
    def _load(self, cfg):
        sources = cfg[Transformation._CFG_KEY_LOAD_SRC]
        self._src = {}
        for collection in sources:
            self._src[collection] = Accessor.factory(self._src_db).get(
                {AccessParams.KEY_COLLECTION: collection, AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI})

    def _transform(self, cfg):
        func = cfg[Transformation._CFG_KEY_FUNC]
        args = cfg[Transformation._CFG_KEY_FUNC_PARAMS] if Transformation._CFG_KEY_FUNC_PARAMS in cfg else {}
        self._res = obj_for_name(func)(self._src, args)

    def _cleanup(self, cfg):
        Accessor.factory(self._dest_db).delete(
            {AccessParams.KEY_COLLECTION: cfg[Transformation._CFG_KEY_CLEANUP_TARGET],
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI,
             AccessParams.KEY_MATCH_PARAMS: {}})


class MultiCol2ColTransformation(MultiCol2XTransformation):
    def _save(self, cfg):
        Accessor.factory(self._dest_db).upsert(
            {AccessParams.KEY_COLLECTION: cfg[Transformation._CFG_KEY_SAVE_DEST],
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI,
             AccessParams.KEY_OBJECT: self._res})


def transformer(func):
    def transformer_wrapper(input, params):
        return func(input, **params)
    return transformer_wrapper


@transformer
def group_singles2array(input, **params):
    PARAM_FIELD_KEY = 'field.key'
    PARAM_FIELD_ARRAY = 'field.array'
    PARAM_FIELD_SINGLE = 'field.single'

    field_key = params.get(PARAM_FIELD_KEY) if PARAM_FIELD_KEY in params else None
    field_array = params.get(PARAM_FIELD_ARRAY)
    field_single = params.get(PARAM_FIELD_SINGLE)

    if not field_key:
        res = []
        for item in input:
            res.append(item[field_single])
        return {field_array: res}
    else:
        tdict = {}
        for row in input:
            if not row[field_key] in tdict:
                tdict.update({row[field_key]: [row[field_single]]})
            else:
                tdict[row[field_key]].append(row[field_single])
        res = []
        for key, value in tdict.items():
            res.append({field_key: key, field_array: value})
        return res


@transformer
def ungroup_array2singles(input, **params):
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
    PARAM_SORT_FIELD = 'sort.field'
    PARAM_SORT_ORDER = 'sort.order'

    df = pd.DataFrame.from_records(input)
    sort_field = params.get(PARAM_SORT_FIELD)
    sort_order = params.get(PARAM_SORT_ORDER) if PARAM_SORT_ORDER in params else None
    if sort_order:
        df[sort_field] = df[sort_field].astype('category')
        df[sort_field].cat.set_categories(sort_order, inplace=True)
    df.sort_values(by=sort_field, inplace=True)
    return Converter.df2list(df)


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


@transformer
def regexp(input, **params):
    PARAM_FIELD_TO_PARSE = 'input.field'
    PARAM_PATTERN = 'pattern'
    PARAM_OUTPUT = 'output'
    OUT_DESC_FIELD = 'field'
    OUT_DESC_IDX = 'idx'
    OUT_DESC_TYPE = 'type'

    res = []
    regex = re.compile(params.get(PARAM_PATTERN))
    field2parse = params.get(PARAM_FIELD_TO_PARSE)
    out_desc = params.get(PARAM_OUTPUT)
    for row in input:
        matches = regex.findall(row[field2parse])[0]
        obj = {}
        for desc in out_desc:
            obj[desc[OUT_DESC_FIELD]] = Converter.convert(matches[desc[OUT_DESC_IDX]], desc[OUT_DESC_TYPE])
        res.append(obj)
    return res


@transformer
def format(input, **params):
    PARAM_FORMAT_STRING = 'format.string'
    PARAM_FORMAT_INPUT = 'format.input'
    PARAM_RESULT_FIELD = 'result.field'
    IN_DESC_FIELD = 'field'
    IN_DESC_TYPE = 'type'

    format_string = params.get(PARAM_FORMAT_STRING)
    format_inputs = params.get(PARAM_FORMAT_INPUT)
    result_field = params.get(PARAM_RESULT_FIELD)
    for row in input:
        row_input = []
        for desc in format_inputs:
            row_input.append(Converter.convert(row[desc[IN_DESC_FIELD]], desc[IN_DESC_TYPE]))
        row[result_field] = format_string.format(*row_input)
    return input


@transformer
def left_join(input, **params):
    PARAM_COL_RIGHT = 'col.right'
    PARAM_COL_LEFT = 'col.left'
    PARAM_FIELD_JOIN = 'field.join'

    right_df = pd.DataFrame.from_records(input[params.get(PARAM_COL_RIGHT)])
    left_df = pd.DataFrame.from_records(input[params.get(PARAM_COL_LEFT)])
    join_on = params.get(PARAM_FIELD_JOIN)
    res = right_df.set_index(join_on, drop=False).join(left_df.set_index(join_on, drop=False), on=[join_on], rsuffix='_right')
    return Converter.df2list(res)


@transformer
def union(input, **params):
    return NotImplementedError


@transformer
def update(input, **params):
    return NotImplementedError


@transformer
def replace(input, **params):
    PARAM_REPLACE_LIST = 'replace'
    REPLACE_FIELD = 'field'
    REPLACE_FIND_VALUE = 'value.to_find'
    REPLACE_WITH_VALUE = 'value.replace_with'

    replace_list = params.get(PARAM_REPLACE_LIST)
    for row in input:
        for replace in replace_list:
            if row[replace[REPLACE_FIELD]] == replace[REPLACE_FIND_VALUE]:
                row[replace[REPLACE_FIELD]] = replace[REPLACE_WITH_VALUE]
    return input
