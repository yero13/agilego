import logging
import pandas as pd
import json


class Sprint:
    __COLLECTION_PREFIX = 'sprint'
    BACKLOG = 'backlog'
    BACKLOG_DETAILS = 'backlog-details'
    SUBTASKS = 'subtasks'
    SUBTASKS_DETAILS = 'substasks-details'
    ITEM_KEY = 'key'
    ITEM_PARENT = 'parent'

    @staticmethod
    def wrap_db(collection):
        return '{}.{}'.format(Sprint.__COLLECTION_PREFIX, collection)

class SprintWbs:
    """
    Represents sprint backlog tasks. Provides functionality for checking sprint backlog consistency
    """
    __CFG_SPRINT_BACKLOG_BREAKDOWN = './cfg/sprint-backlog-breakdown.json'

    __CFG_KEY_SCOPE_DATASET = 'dataset'
    __CFG_KEY_SCOPE_MODIFY_FIELDS = 'modify-fields' # ToDo: add fields and transformation sign eval/lambda

    __CFG_KEY_INDEXES = 'indexes'
    __CFG_KEY_INDEX_L1KEY = 'l1key'
    __CFG_KEY_INDEX_L2KEY = 'l2key'
    __CFG_KEY_INDEX_WHERE = 'where'

    __CFG_KEY_SUBSETS = 'subsets'
    __CFG_KEY_SUBSET_INDEX = 'index'
    __CFG_KEY_SUBSET_JOIN_ON = 'join_on'
    __CFG_KEY_SUBSET_COLUMNS = 'columns'
    __CFG_KEY_SUBSET_ORDER = 'order'
    __CFG_KEY_SUBSET_SORT = 'sort'

    def __init__(self, work_dict):
        self.__logger = logging.getLogger(__name__)
        self.__logger.info('sprint backlog input: {:d} work items'.format(len(work_dict)))
        self.__work_df = pd.DataFrame.from_dict(work_dict, orient='Index')
        self.__logger.debug('backlog items for planning:\n {}'.format(list(self.__work_df.columns.values)))
        with open(SprintWbs.__CFG_SPRINT_BACKLOG_BREAKDOWN) as cfg_file:
            self.__cfg = json.load(cfg_file, strict=False)
        self.__transform_dataset()
        self.__indexes = self.__create_indexes() if SprintWbs.__CFG_KEY_INDEXES in self.__cfg else []
        self.__subsets = self.__create_subsets()

    def to_db(self, db):
        """
        Saves transformed sprint backlog to MongoDB
        :param db:
        :return:
        """
        for subset in self.__subsets:
            name = Sprint.wrap_db(subset[0])
            data = subset[1]
            db[name].remove() # ToDo: move to clean-up
            db[name].insert_many(json.loads(data.T.to_json()).values())
            self.__logger.info('Subset {} saved to collection {}'.format(subset[0], name))

    def __get_index(self, index_name):
        for index in self.__indexes:
            if index[0] == index_name:
                return index[1]

    def __create_subsets(self):
        # ToDo: order and sort should be implemented for subsets
        subsets = []
        self.__logger.info('creating subsets...')
        for subset in self.__cfg[SprintWbs.__CFG_KEY_SUBSETS]:
            subset_cfg = self.__cfg[SprintWbs.__CFG_KEY_SUBSETS][subset]
            index = subset_cfg[SprintWbs.__CFG_KEY_SUBSET_INDEX]
            # ToDo: if no join and columns return index itself
            join_on = subset_cfg[SprintWbs.__CFG_KEY_SUBSET_JOIN_ON]
            columns = subset_cfg[SprintWbs.__CFG_KEY_SUBSET_COLUMNS]
            order = subset_cfg[
                SprintWbs.__CFG_KEY_SUBSET_ORDER] if SprintWbs.__CFG_KEY_SUBSET_ORDER in subset_cfg else None
            sort = subset_cfg[
                SprintWbs.__CFG_KEY_SUBSET_SORT] if SprintWbs.__CFG_KEY_SUBSET_SORT in subset_cfg else None
            self.__logger.info('creating subset {}...'.format(subset))
            subsets.append((subset, self.__create_subset(index, join_on, columns, order, sort)))
        return subsets

    def __create_subset(self, index, join_on, columns, order, sort):
        self.__logger.info(
            'creating subset: index {}, join on {}, columns {}, order {}, sort {}'.format(index, join_on, columns, order, sort))
        index_df = self.__get_index(index)
        # ToDo: optimize performance - set indexes
        subset_df = index_df.join(self.__work_df[columns], on=[join_on], lsuffix='_left')
        subset_df = subset_df[columns]
        if order:
            if sort:
                subset_df[order] = subset_df[order].astype('category')
                subset_df[order].cat.set_categories(sort, inplace=True)
            subset_df.sort_values(by=order, inplace=True)
        self.__logger.debug('Subset created\n{}'.format(subset_df))
        return subset_df

    @classmethod
    def from_dict(cls, work_dict):
        """
        Construct SprintBacklog from dictionary of work items

        :param work_dict: {work item key: work item descriptor}
        :return: SprintBacklog
        """
        return cls(work_dict)

    def __transform_dataset(self):
        if SprintWbs.__CFG_KEY_SCOPE_MODIFY_FIELDS in self.__cfg[SprintWbs.__CFG_KEY_SCOPE_DATASET]:
            changes = self.__cfg[SprintWbs.__CFG_KEY_SCOPE_DATASET][SprintWbs.__CFG_KEY_SCOPE_MODIFY_FIELDS]
            for field in changes:
                self.__logger.info('modifying field \'{}\' - eval({})'.format(field, changes[field]))
                self.__work_df.eval('{} = {}'.format(field, changes[field]), inplace=True)
                self.__logger.debug('modified field:\n{}'.format(self.__work_df[field]))

    def __is_list(self, field):
        return isinstance(self.__work_df[field].iloc[0], list)  # ToDo: define type based on first not null value

    def __create_indexes(self):
        indexes = []
        self.__logger.info('creating indexes...')
        for index in self.__cfg[SprintWbs.__CFG_KEY_INDEXES]:
            self.__logger.info('creating index {}...'.format(index))
            index_cfg = self.__cfg[SprintWbs.__CFG_KEY_INDEXES][index]
            l1key = index_cfg[SprintWbs.__CFG_KEY_INDEX_L1KEY]
            l2key = index_cfg[SprintWbs.__CFG_KEY_INDEX_L2KEY]
            where = index_cfg[
                SprintWbs.__CFG_KEY_INDEX_WHERE] if SprintWbs.__CFG_KEY_INDEX_WHERE in index_cfg else None
            indexes.append((index, self.__create_index(l1key, l2key, where)))
        return indexes

    def __create_index(self, l1key, l2key, where):
        self.__logger.info(
            'creating index: l1key {}, l2key {}, where {}'.format(l1key, l2key, where))
        if self.__is_list(l1key) and self.__is_list(l2key):
            raise NotImplementedError('Creating index with more than one field of list type is not supported')
        # ToDo: implement checks for null/empty fields - now null/empty values for keys are filtered out
        index_df = self.__work_df.query(where) if where else self.__work_df
        if where:
            self.__logger.debug(
                'filtered: {:d} items from {:d} total'.format(index_df[l1key].count(), self.__work_df[l1key].count()))
        index_df = index_df[[l1key, l2key]]
        index = pd.DataFrame()
        if not self.__is_list(l1key) and not self.__is_list(l2key):
            index_df = index_df[index_df[l1key].notnull()] # l1keys should be not null
            index = index_df[[l1key, l2key]]
        else:
            l1key_index = pd.Series()
            l2key_index = pd.Series()
            if self.__is_list(l1key) and not self.__is_list(l2key):
                index_df = index_df[index_df[l1key].apply(lambda key_list: True if len(key_list) > 0 else False)]
                for item in index_df.iterrows():
                    l1key_index = l1key_index.append(pd.Series.from_array(item[1][l1key]))
                    l2key_index = l2key_index.append(pd.Series.from_array([item[1][l2key]] * len(item[1][l1key])))
            elif not self.__is_list(l1key) and self.__is_list(l2key):
                index_df = index_df[index_df[l2key].apply(lambda value_list: True if len(value_list) > 0 else False)]
                for item in index_df.iterrows():
                    l1key_index = l1key_index.append(pd.Series.from_array([item[1][l1key]] * len(item[1][l2key])))
                    l2key_index = l2key_index.append(pd.Series.from_array(item[1][l2key]))
            index[l1key] = l1key_index
            index[l2key] = l2key_index
        self.__logger.debug('Index created\n{}'.format(index))

        return index
