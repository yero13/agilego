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
    _TASK_TEXT = 'text'
    _TASK_PARENT = 'parent'
    _TASK_STARTDATE = 'start_date'
    _TASK_ENDDATE = 'end_date'
    _TASK_EXT = 'ext'

    def __init__(self):
        self._logger = logging.getLogger(__class__.__name__)
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
        return NotImplementedError

    def _add_ext_task(self, node):
        if node not in self._graph.nodes:
            self._graph.add_node(node)
            nx.set_node_attributes(self._graph, {node: {Gantt._TASK_EXT: True}})

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
    #_TASK_DUEDATE = 'duedate'
    #_TASK_ESTIMATE = 'estimate'
    #_TASK_WHRS = 'whrs'

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
        if date_aggs:
            res.update({Gantt._TASK_STARTDATE: Converter.convert(date_aggs['min'], Types.TYPE_STRING)})
            res.update({Gantt._TASK_ENDDATE: Converter.convert(date_aggs['max'], Types.TYPE_STRING)})

            # whrs = time_aggs[issue[ParamConstants.PARAM_ITEM_KEY]] if issue[ParamConstants.PARAM_ITEM_KEY] in time_aggs else None
            # type = issue[Gantt.__TASK_TYPE]
            # Gantt.__TASK_DUEDATE: issue[Gantt.__TASK_DUEDATE],
            # Gantt.__TASK_WHRS: whrs, Gantt.__TASK_EXT: False,
            # Gantt.__TASK_TEXT: issue[ParamConstants.PARAM_ITEM_KEY]})


        return res

    def toString(self):
        self._logger.debug(self.tasks)
        self._logger.debug(self.links)
