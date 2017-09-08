import logging
import pandas as pd
import json


class SprintBacklog:
    """
    Represents sprint backlog tasks. Provides functionality for checking sprint backlog consistency
    """
    __CFG_SPRINT_BACKLOG_BREAKDOWN = './cfg/sprint-backlog-breakdown.json'

    __CFG_KEY_SCOPE_DATASET = 'dataset'
    __CFG_KEY_SCOPE_MODIFY_FIELDS = 'modify-fields' # ToDo: add fields and transformation sign eval/lambda

    __CFG_KEY_INDEXES = 'indexes'
    __CFG_KEY_INDEX_KEY = 'key'
    __CFG_KEY_INDEX_VALUE = 'value'
    __CFG_KEY_INDEX_WHERE = 'where'
    __CFG_KEY_INDEX_ORDER = 'order'
    __CFG_KEY_INDEX_SORT = 'sort'

    __CFG_KEY_SUBSETS = 'subsets'
    __CFG_KEY_SUBSET_INDEX = 'index'
    __CFG_KEY_SUBSET_COLUMNS = 'columns'

    def __init__(self, work_dict):
        self.__logger = logging.getLogger(__name__)
        #self.__logger.info('sprint backlog input: {:d} work items'.format(len(work_dict)))
        self.__work_df = pd.DataFrame.from_dict(work_dict, orient='Index')
        #self.__logger.debug('backlog items for planning:\n {}'.format(list(self.__work_df.columns.values)))
        with open(SprintBacklog.__CFG_SPRINT_BACKLOG_BREAKDOWN) as cfg_file:
            self.__cfg = json.load(cfg_file, strict=False)
        self.__indexes = self.__create_indexes() if SprintBacklog.__CFG_KEY_INDEXES in self.__cfg else []
        self.__transform_dataset()
        self.__subsets = self.__create_subsets()

    @property
    def issues(self):
        for index in self.__indexes:  # ToDo: fix this - temporary for FE-BE integartion
            if index.name == 'priorities':
                return index

    @property
    def backlog(self):
        for subset in self.__subsets:  # ToDo: fix this - temporary for FE-BE integartion
            if subset.name == 'backlog':
                return subset

    def __get_index(self, index_name):
        for index in self.__indexes:  # ToDo: fix this - temporary for FE-BE integartion
            if index.name == index_name:
                return index

    def __create_subsets(self):
        subsets = []
        self.__logger.info('creating subsets')
        for subset in self.__cfg[SprintBacklog.__CFG_KEY_SUBSETS]:
            subset_cfg = self.__cfg[SprintBacklog.__CFG_KEY_SUBSETS][subset]
            index_name = subset_cfg[SprintBacklog.__CFG_KEY_SUBSET_INDEX]
            columns = subset_cfg[SprintBacklog.__CFG_KEY_SUBSET_COLUMNS]
            self.__logger.info('creating subset {}: index {}, columns {}'.format(subset, index_name, columns))
            index = self.__get_index(index_name)
            subset_df = pd.concat([index, self.__work_df], axis=1, join_axes=[index.index])
            subset_df = subset_df[columns]
            subset_df.name = subset
            subsets.append(subset_df)
        return subsets

    @classmethod
    def from_dict(cls, work_dict):
        """
        Construct SprintBacklog from dictionary of work items

        :param work_dict: {work item key: work item descriptor}
        :return: SprintBacklog
        """
        return cls(work_dict)

    def __transform_dataset(self):
        if SprintBacklog.__CFG_KEY_SCOPE_MODIFY_FIELDS in self.__cfg[SprintBacklog.__CFG_KEY_SCOPE_DATASET]:
            changes = self.__cfg[SprintBacklog.__CFG_KEY_SCOPE_DATASET][SprintBacklog.__CFG_KEY_SCOPE_MODIFY_FIELDS]
            for field in changes:
                self.__logger.info('modifying field \'{}\' - eval({})'.format(field, changes[field]))
                self.__work_df.eval('{} = {}'.format(field, changes[field]), inplace=True)
                self.__logger.debug('modified field:\n{}'.format(self.__work_df[field]))

    def __is_list(self, field):
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
            sort = index_cfg[
                SprintBacklog.__CFG_KEY_INDEX_SORT] if SprintBacklog.__CFG_KEY_INDEX_SORT in index_cfg else None
            indexes.append(self.__create_index(index, key, value, where, order, sort))
        return indexes

    def __create_index(self, name, key, value, where, order, sort):
        self.__logger.info(
            'creating index {}: key {}, value {}, where {}, order {}, sort {}'.format(name, key, value, where, order,
                                                                                      sort))
        if self.__is_list(key) and self.__is_list(value):
            raise NotImplementedError('Creating index with more than one field of list type is not supported')
        # ToDo: implement checks for null/empty fields - now null/empty values for keys are filtered out
        index_df = self.__work_df.query(where) if where else self.__work_df
        if where:
            self.__logger.debug(
                'filtered: {:d} items from {:d} total'.format(index_df[key].count(), self.__work_df[key].count()))
        index_df = index_df[[key, value]]
        if order:
            if self.__is_list(order):
                raise NotImplementedError('Custom order for list type key is not supported')
            index_df[order] = index_df[order].astype('category')
            index_df[order].cat.set_categories(sort, inplace=True)
        if not self.__is_list(key) and not self.__is_list(value):
            index_df = index_df[index_df[key].notnull()]
            index = pd.Series().from_array(index_df[value].values, index=index_df[key], name=name)
        else:
            index = pd.Series(name=name)
            if self.__is_list(key) and not self.__is_list(value):
                index_df = index_df[index_df[key].apply(lambda key_list: True if len(key_list) > 0 else False)]
                for item in index_df.iterrows():
                    index = index.append(pd.Series.from_array([item[1][value]] * len(item[1][key]), index=item[1][key]))
            elif not self.__is_list(key) and self.__is_list(value):
                index_df = index_df[index_df[value].apply(lambda value_list: True if len(value_list) > 0 else False)]
                for item in index_df.iterrows():
                    index = index.append(pd.Series.from_array(item[1][value], index=[item[1][key]] * len(item[1][value])))
        if order == key:
            index.sort_index(inplace=True)
        if order == value:
            index.sort_values(inplace=True)
        self.__logger.debug('\n{}'.format(index))

        return index
