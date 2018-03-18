from natrix.db.data import Accessor, AccessParams
from natrix.utils.aggregator import Aggregator
from natrix.utils.converter import Converter, Types
from logic.constants import DbConstants, ParamConstants


class Link:
    LINK_ID = 'id'
    LINK_TYPE = 'type'
    LINK_BLOCKS = 'blocks'
    LINK_BLOCKED = 'blocked'
    LINK_SOURCE = 'source'
    LINK_TARGET = 'target'


class Task:
    TASK_EXT = 'ext'
    TASK_ID = 'id'
    TASK_TYPE = 'type'
    TASK_TYPE_UNKNOWN = 'Unknown'
    TASK_TEXT = 'text'
    TASK_PARENT = 'parent'
    TASK_ENDDATE = 'end_date'
    TASK_DUEDATE = 'duedate'
    TASK_DURATION = 'duration'
    __TASK_DURATION_DEFAULT = 0.99
    TASK_HRS_ALLOC = 'whrs'
    TASK_HRS_ESTIMATE = 'estimate'
    __SPRINT_ENDDATE = 'endDate'
    __WHRS_DAY = 6

    @staticmethod
    def get_default_end_date():
        return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_SPRINT, AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE})[
            Task.__SPRINT_ENDDATE].replace(hour=23, minute=59)

    @staticmethod
    def get_default_duration():
        return Task.__TASK_DURATION_DEFAULT

    @staticmethod
    def create_fake_task(id, text, parent=None):
        res = {Task.TASK_ID: id, Task.TASK_TEXT: text, Task.TASK_DURATION: Task.get_default_duration(),
               Task.TASK_ENDDATE: Task.get_default_end_date(), Task.TASK_TYPE: Task.TASK_TYPE_UNKNOWN,
               Task.TASK_DUEDATE: '', Task.TASK_HRS_ESTIMATE: '', Task.TASK_HRS_ALLOC: ''}
        if parent:
            res.update({Task.TASK_PARENT: parent})
        return res

    @staticmethod
    def create_task(id):
        res = {}
        res.update({Task.TASK_ID: id})
        backlog_item = Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_SPRINT_BACKLOG,
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE,
             AccessParams.KEY_MATCH_PARAMS: {ParamConstants.PARAM_ITEM_KEY: id}})
        res.update({Task.TASK_TEXT: id})
        parent = backlog_item[ParamConstants.PARAM_ITEM_PARENT]
        if parent:
            res.update({Task.TASK_PARENT: parent})
        assignments = Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_ASSIGNMENTS,
             AccessParams.KEY_MATCH_PARAMS: {ParamConstants.PARAM_ITEM_KEY: id},
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI})
        date_aggs = Aggregator.agg_multi_func(assignments, ParamConstants.PARAM_DATE, ['min', 'max'])
        alloc_whrs = Aggregator.agg_single_func(assignments, ParamConstants.PARAM_WHRS, 'sum')
        if date_aggs:
            start_date = date_aggs['min']
            end_date = date_aggs['max']
            days_delta = (end_date - start_date).days
            duration = alloc_whrs / Task.__WHRS_DAY if (days_delta == 0 and alloc_whrs < Task.__WHRS_DAY) else (
                days_delta + Task.get_default_duration())
        else:
            end_date = Task.get_default_end_date()
            duration = Task.get_default_duration()
        res.update({Task.TASK_ENDDATE: end_date.replace(hour=23, minute=59)})
        res.update({Task.TASK_DURATION: duration})
        res.update({Task.TASK_HRS_ALLOC: Converter.convert(alloc_whrs, Types.TYPE_STRING)})
        res.update({Task.TASK_DUEDATE: backlog_item[Task.TASK_DUEDATE] if backlog_item[Task.TASK_DUEDATE] else ''})
        res.update({Task.TASK_HRS_ESTIMATE: Converter.convert(backlog_item[Task.TASK_HRS_ESTIMATE], Types.TYPE_STRING)})
        res.update({Task.TASK_TYPE: backlog_item[Task.TASK_TYPE]})
        return res
