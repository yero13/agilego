from transformation.transformer import transformer
import pandas as pd

@transformer
def dates2range(input, **params):
    PARAM_FIELD_STARTDATE = 'field.startDate'
    PARAM_FIELD_ENDDATE = 'field.endDate'
    PARAM_FIELD_RANGE = 'field.range'

    return {params.get(PARAM_FIELD_RANGE): pd.date_range(input[params.get(PARAM_FIELD_STARTDATE)],
                                                         input[params.get(PARAM_FIELD_ENDDATE)]).tolist()}


@transformer
def sec2hrs(input, **params):
    PARAM_FIELDS = 'fields'

    fields = params.get(PARAM_FIELDS)
    for field in fields:
        for row in input:
            row[field] = row[field]/3600 if row[field] else None
    return input


'''
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
                    self.__df_dataset[dest_field] = self.__update_data[src_field]m
    def _save(self):
        res = Converter.df2list(self.__df_dataset)
        if len(res) > 0:
            self._dest_db[self._dest_collection].insert_many(res)
'''