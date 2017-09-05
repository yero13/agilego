import logging
import pandas as pd
import json


class SprintBacklog:
    """
    Represents sprint backlog tasks. Provides functionality for checking sprint backlog consistency
    """
    __CFG_SPRINT_BACKLOG_BREAKDOWN = './cfg/sprint-backlog-breakdown.json'

    __CFG_KEY_INDEXES = 'indexes'
    __CFG_KEY_INDEX_KEY = 'key'
    __CFG_KEY_INDEX_VALUE = 'value'
    __CFG_KEY_INDEX_WHERE = 'where'
    __CFG_KEY_INDEX_ORDER = 'order'

    def __init__(self, work_dict):
        self.__logger = logging.getLogger(__name__)
        #self.__logger.info('sprint backlog input: {:d} work items'.format(len(work_dict)))
        self.__work_df = pd.DataFrame.from_dict(work_dict, orient='Index')
        #self.__logger.debug('backlog items for planning:\n {}'.format(list(self.__work_df.columns.values)))
        with open(SprintBacklog.__CFG_SPRINT_BACKLOG_BREAKDOWN) as cfg_file:
            self.__cfg = json.load(cfg_file, strict=False)
        self.__indexes = self.__create_indexes()

    @classmethod
    def from_dict(cls, work_dict):
        """
        Construct SprintBacklog from dictionary of work items

        :param work_dict: {work item key: work item descriptor}
        :return: SprintBacklog
        """
        return cls(work_dict)

    def __islist(self, field):
        return isinstance(self.__work_df[field].iloc[0], list)  # ToDo: define type based on first not null value

    def __create_indexes(self):
        indexes = []
        self.__logger.info('creating indexes')
        for index in self.__cfg[SprintBacklog.__CFG_KEY_INDEXES]:
            index_cfg = self.__cfg[SprintBacklog.__CFG_KEY_INDEXES][index]
            key = index_cfg[SprintBacklog.__CFG_KEY_INDEX_KEY]
            value = index_cfg[SprintBacklog.__CFG_KEY_INDEX_VALUE]
            where = index_cfg[
                SprintBacklog.__CFG_KEY_INDEX_WHERE] if SprintBacklog.__CFG_KEY_INDEX_WHERE in index_cfg else None
            order = index_cfg[
                SprintBacklog.__CFG_KEY_INDEX_ORDER] if SprintBacklog.__CFG_KEY_INDEX_ORDER in index_cfg else None
            indexes.append(self.__create_index(index, key, value, where, order))
        return indexes

    def __create_index(self, name, key, value, where, order):
        self.__logger.info(
            'creating index {}: key {}, value {}, where {}, order {}'.format(name, key, value, where, order))
        if self.__islist(key) and self.__islist(value):
            raise NotImplementedError('Creating index with more than one field of list type is not supported')
        # ToDo: implement checks for null/empty fields - now null/empty values for keys are filtered out
        index_df = self.__work_df.query(where) if where else self.__work_df
        if where:
            self.__logger.debug(
                'filtered: {:d} items from {:d} total'.format(index_df[key].count(), self.__work_df[key].count()))
        index_df = index_df[[key, value]]
        if order:
            if self.__islist(key):
                raise NotImplementedError('Custom order for list type key is not supported')
            index_df[key] = index_df[key].astype('category')
            index_df[key].cat.set_categories(order, inplace=True)
        if not self.__islist(key) and not self.__islist(value):
            index_df = index_df[index_df[key].notnull()]
            index = pd.Series().from_array(index_df[value].values, index=index_df[key], name=name)
        else:
            index = pd.Series(name=name)
            if self.__islist(key) and not self.__islist(value):
                index_df = index_df[index_df[key].apply(lambda key_list: True if len(key_list) > 0 else False)]
                for item in index_df.iterrows():
                    index = index.append(pd.Series.from_array([item[1][value]] * len(item[1][key]), index=item[1][key]))
            elif not self.__islist(key) and self.__islist(value):
                index_df = index_df[index_df[value].apply(lambda value_list: True if len(value_list) > 0 else False)]
                for item in index_df.iterrows():
                    index = index.append(pd.Series.from_array(item[1][value], index=[item[1][key]] * len(item[1][value])))
        index.sort_index(inplace=True)
        self.__logger.debug('\n{}'.format(index))

        return index
