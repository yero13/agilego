import logging
import networkx as nx
import abc
from framework.db.data import Accessor, AccessParams
from framework.utils.aggregator import Aggregator
from framework.utils.converter import Converter, Types
from logic.constants import DbConstants, ParamConstants


class Gantt:
    _LINK_TYPE = 'type'
    _LINK_SUBTASK = 'subtask'
    _LINK_BLOCKS = 'blocks'
    _LINK_BLOCKED = 'blocked'
    _LINK_SOURCE = 'source'
    _LINK_TARGET = 'target'
    _LINK_ID = 'id'
    _TASK_ID = 'id'
    _TASK_TYPE = 'type'
    _TASK_TYPE_UNKNOWN = 'Unknown'
    _TASK_TEXT = 'text'
    _TASK_PARENT = 'parent'
    _TASK_STARTDATE = 'start_date'
    _TASK_ENDDATE = 'end_date'
    _TASK_DUEDATE = 'duedate'
    _TASK_DURATION = 'duration'
    _TASK_HRS_ALLOC = 'whrs'
    _TASK_HRS_ESTIMATE = 'estimate'
    _EXT = 'ext'
    _WHRS_DAY = 6
    _SPRINT_ENDDATE = 'endDate'

    def __init__(self):
        self._logger = logging.getLogger(__class__.__name__)
        self._sprint = Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_SPRINT, AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE})
        self._graph = nx.DiGraph()
        self._add_tasks()
        self._add_links()

    def _add_links(self):
        links = self._get_links_source()
        for link in links:
            link_type = link[Gantt._LINK_TYPE]
            link_source = link[Gantt._LINK_SOURCE]
            link_target = link[Gantt._LINK_TARGET]
            self._add_ext_task(link_source)
            self._add_ext_task(link_target)
            if link_type == Gantt._LINK_BLOCKS:
                self._graph.add_edge(link_source, link_target)
            elif link_type == Gantt._LINK_BLOCKED and (link_target, link_source) not in self._graph.edges:
                self._graph.add_edge(link_target, link_source)

    @abc.abstractmethod
    def _get_links_source(self):
        return NotImplemented

    def _add_ext_task(self, node):
        if node not in self._graph.nodes:
            if not Gantt._EXT in self._graph.nodes:
                self._graph.add_node(Gantt._EXT)
                nx.set_node_attributes(self._graph, {
                    Gantt._EXT: {Gantt._TASK_ID: Gantt._EXT, Gantt._TASK_TEXT: 'External dependencies',
                                 Gantt._TASK_DURATION: self._get_default_task_duration({}),
                                 Gantt._TASK_ENDDATE: self._get_default_task_end_date({}),
                                 Gantt._TASK_TYPE: Gantt._TASK_TYPE_UNKNOWN,
                                 Gantt._TASK_DUEDATE: '', Gantt._TASK_HRS_ESTIMATE: '', Gantt._TASK_HRS_ALLOC: ''}})
            self._graph.add_node(node)
            nx.set_node_attributes(self._graph, {
                node: {Gantt._TASK_ID: node, Gantt._TASK_TEXT: node, Gantt._TASK_PARENT: Gantt._EXT,
                       Gantt._TASK_DURATION: self._get_default_task_duration({}),
                       Gantt._TASK_ENDDATE: self._get_default_task_end_date({}),
                       Gantt._TASK_TYPE: Gantt._TASK_TYPE_UNKNOWN,
                       Gantt._TASK_DUEDATE: '', Gantt._TASK_HRS_ESTIMATE: '', Gantt._TASK_HRS_ALLOC: ''}})

    def _get_default_task_duration(self, task):
        return task[Gantt._TASK_HRS_ESTIMATE] if (Gantt._TASK_HRS_ESTIMATE in task and task[Gantt._TASK_HRS_ESTIMATE]) else 0.95

    def _get_default_task_end_date(self, task):
        end_date = task[Gantt._TASK_DUEDATE] if (Gantt._TASK_DUEDATE in task and task[Gantt._TASK_DUEDATE]) else self._sprint[Gantt._SPRINT_ENDDATE]
        return end_date.replace(hour=23, minute=59)

    def _add_tasks(self):
        tasks = self._get_tasks_source()
        for task in tasks:
            task_id = self._get_task_id(task)
            self._graph.add_node(task_id)
            nx.set_node_attributes(self._graph, {task_id: self._get_task_attrs(task)})

    @abc.abstractmethod
    def _get_tasks_source(self):
        return NotImplemented

    @abc.abstractmethod
    def _get_task_attrs(self, task):
        return NotImplemented

    def _get_task_id(self, task):
        return task[ParamConstants.PARAM_ITEM_KEY]

    @property
    def links(self):
        res = []
        for edge in self._graph.edges:
            link = {Gantt._LINK_ID: '{}->{}'.format(edge[0], edge[1]), Gantt._LINK_SOURCE: edge[0],
                    Gantt._LINK_TARGET: edge[1], Gantt._LINK_TYPE: 2}
            res.append(link)
        return res

    @property
    def tasks(self):
        res = []
        for node in self._graph.nodes:
            res.append(self._graph.nodes[node])
        return res


class BaselineGantt(Gantt):
    def __init__(self):
        super().__init__()

    def _get_links_source(self):
        return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_BACKLOG_LINKS,
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI})

    def _get_tasks_source(self):
        return Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_SPRINT_BACKLOG,
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI})

    def _get_task_attrs(self, task):
        res = {}
        id = task[ParamConstants.PARAM_ITEM_KEY]
        res.update({Gantt._TASK_ID: id})
        res.update({Gantt._TASK_TEXT: id})
        parent = task[ParamConstants.PARAM_ITEM_PARENT]
        if parent:
            res.update({Gantt._TASK_PARENT: parent})
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
            duration = alloc_whrs/Gantt._WHRS_DAY if (days_delta == 0 and alloc_whrs < Gantt._WHRS_DAY) else (days_delta + 0.95)
        else:
            end_date = self._get_default_task_end_date(task)
            duration = self._get_default_task_duration(task)
        res.update({Gantt._TASK_ENDDATE: end_date.replace(hour=23, minute=59)})
        res.update({Gantt._TASK_DURATION: duration})
        res.update({Gantt._TASK_HRS_ALLOC: Converter.convert(alloc_whrs, Types.TYPE_STRING)})
        res.update({Gantt._TASK_DUEDATE: task[Gantt._TASK_DUEDATE] if task[Gantt._TASK_DUEDATE] else ''})
        res.update({Gantt._TASK_HRS_ESTIMATE: Converter.convert(task[Gantt._TASK_HRS_ESTIMATE], Types.TYPE_STRING)})
        res.update({Gantt._TASK_TYPE: task[Gantt._TASK_TYPE]})
        return res

    def toString(self):
        self._logger.debug(self.tasks)
        self._logger.debug(self.links)
