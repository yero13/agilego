from transformation.transformer import transformer
import pandas as pd

@transformer
def dates2range(input, **params):
    PARAM_FIELD_STARTDATE = 'field.startDate'
    PARAM_FIELD_ENDDATE = 'field.endDate'
    PARAM_FIELD_RANGE = 'field.range'

    return {params.get(PARAM_FIELD_RANGE): pd.date_range(input[params.get(PARAM_FIELD_STARTDATE)],
                                                         input[params.get(PARAM_FIELD_ENDDATE)]).tolist()}

'''
from transformation.transformer import Transformation
import re

import pandas as pd  # ToDo: exec should be moved to functions
import datetime

from utils.converter import Converter


class SingleObjectTransformation(Transformation):
    def _load(self):
        self.__object = self._src_db[self._src_collection].find_one({}, {'_id': False})

    def _save(self):
        if not self.__object:
            return
        if self._fields:
            obj = Transformation._filter_fields(self.__object, self._fields)
        else:
            obj = self.__object
        self._dest_db[self._dest_collection].insert_one(obj)

    def _transform(self):
        for transformation in self._transformation:
            obj = self.__object # for access from exec # ToDo: check if notnull validation is required
            exec(self._transformation[transformation])  # ToDo: change to compile/eval (need to add key as target in cfg)


class DatasetTransformation(Transformation):
    __CFG_KEY_TRANSFORM_VALUES = 'transform_values'
    __CFG_KEY_TRANSFORM_WHERE = 'where'
    __CFG_KEY_TRANSFORM_ORDER = 'order'
    __CFG_KEY_ORDER_BY = 'by_column'
    __CFG_KEY_ORDER_SORT = 'sort_order'
    __CFG_KEY_REGEX = 'regex'
    __CFG_KEY_REGEX_PATTERN = 'pattern'
    __CFG_KEY_REGEX_INPUT = 'input'

    def _load(self):
        self.__dataset = list(self._src_db[self._src_collection].find({}, {'_id': False}))

    def _transform(self):
        if len(self.__dataset) == 0:
            return
        self.__df_dataset = pd.DataFrame.from_records(self.__dataset)
        self.__regex = re.compile(self._transformation[DatasetTransformation.__CFG_KEY_REGEX][
                                      DatasetTransformation.__CFG_KEY_REGEX_PATTERN]) if DatasetTransformation.__CFG_KEY_REGEX in self._transformation else None
        if DatasetTransformation.__CFG_KEY_TRANSFORM_VALUES in self._transformation:
            self.__transform_values()
        if DatasetTransformation.__CFG_KEY_TRANSFORM_WHERE in self._transformation:
            self.__transform_where()
        if DatasetTransformation.__CFG_KEY_TRANSFORM_ORDER in self._transformation:
            self.__transform_order()
        self.__dataset = Converter.df2list(self.__df_dataset)

    def __transform_values(self):
        value_transformations = self._transformation[DatasetTransformation.__CFG_KEY_TRANSFORM_VALUES]
        dataset = self.__df_dataset.to_dict(orient='records')
        for transformation in value_transformations:
            for row in dataset: # row is required for exec
                if self.__regex:
                    regex = self.__regex.findall(row[self._transformation[DatasetTransformation.__CFG_KEY_REGEX][DatasetTransformation.__CFG_KEY_REGEX_INPUT]])
                    if regex:
                        regex = regex[0] if regex else None
                        exec(value_transformations[transformation]) # ToDo: compile, etc
                else:
                    exec(value_transformations[transformation])
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
        if self._fields:
            res = []
            for item in self.__dataset:
                obj = Transformation._filter_fields(item, self._fields)
                res.append(obj)
            self.__dataset = res
        if len(self.__dataset) > 0:
            self._dest_db[self._dest_collection].insert_many(self.__dataset)


class TransposeTransformation(Transformation):
    __CFG_KEY_TKEY = 'key'
    __CFG_KEY_TVALUES = 'values'
    # ToDo: implement support for multi arrays

    def _load(self):
        self._field_key = self._transformation[TransposeTransformation.__CFG_KEY_TKEY]
        self._field_values = self._transformation[TransposeTransformation.__CFG_KEY_TVALUES]
        self._dataset = list(self._src_db[self._src_collection].find({}, {self._field_key: True, self._field_values: True, '_id': False}))

    def _save(self):
        if len(self._dataset) > 0:
            self._dest_db[self._dest_collection].insert_many(self._dataset)


class TransposeFromArrayTransformation(TransposeTransformation):
    def _transform(self):
        res = []
        for item in self._dataset:
            if item[self._field_values] and len(item[self._field_values]) > 0:# No need to keep empty values
                for value in item[self._field_values]:
                    res.append({self._field_key: item[self._field_key], self._field_values: value})
        self._dataset = res


class TransposeToArrayTransformation(TransposeTransformation):
    def _transform(self):
        tdict = {}
        for item in self._dataset:
            if not item[self._field_key] in tdict:
                tdict.update({item[self._field_key]: [item[self._field_values]]})
            else:
                tdict[item[self._field_key]].append(item[self._field_values])
        res = []
        for key, value in tdict.items():
            res.append({self._field_key: key, self._field_values: value})
        self._dataset = res


class LeftJoinTransformation(Transformation):
    __CFG_KEY_LEFT = 'left'
    __CFG_KEY_JOIN_ON = 'join_on'

    def _load(self):
        self.__right_df = pd.DataFrame.from_records(list(self._src_db[self._src_collection].find({}, {'_id': False})))
        self.__left_df = pd.DataFrame.from_records(
            list(self._src_db[self._transformation[LeftJoinTransformation.__CFG_KEY_LEFT]].find({}, {'_id': False})))

    def _transform(self):
        join_on = self._transformation[LeftJoinTransformation.__CFG_KEY_JOIN_ON]
        self.__result = self.__right_df.set_index(join_on, drop=False).join(
            self.__left_df.set_index(join_on, drop=False), on=[join_on], rsuffix='_right')

    def _save(self):
        res = Converter.df2list(self.__result)
        if len(res) > 0:
            self._dest_db[self._dest_collection].insert_many(res)


class UpdateTransformation(Transformation):
    __CFG_KEY_UPD_COLLECTION = 'upd.collection'
    __CFG_KEY_UPD_FIELDS = 'upd.fields'

    def _load(self):
        self.__dataset = list(self._src_db[self._src_collection].find({}, {'_id': False}))
        self.__update_data = self._src_db[self._transformation[UpdateTransformation.__CFG_KEY_UPD_COLLECTION]].find_one({}, {'_id': False})

    def _transform(self):
        self.__df_dataset = pd.DataFrame.from_records(self.__dataset)
        if len(self.__update_data) > 0 and len(self.__dataset) > 0:
            for item in self._transformation[UpdateTransformation.__CFG_KEY_UPD_FIELDS]:
                (src_field, dest_field), = item.items()
                self.__df_dataset[dest_field] = self.__update_data[src_field]

    def _save(self):
        res = Converter.df2list(self.__df_dataset)
        if len(res) > 0:
            self._dest_db[self._dest_collection].insert_many(res)
'''