import logging
import networkx as nx
from framework.db.data import Accessor, AccessParams
from framework.utils.aggregator import Aggregator
from framework.utils.converter import Converter, Types
from logic.constants import DbConstants, ParamConstants


class AbstractGantt:
    def __init__(self):
        self._logger = logging.getLogger(__class__.__name__)
        self._graph = nx.DiGraph()


# ToDo: this class should be optimized to work with sevaral data sets (see AbsGantt)
class Gantt(AbstractGantt):
    __LINK_TYPE = 'type'
    __LINK_SUBTASK = 'subtask'
    __LINK_BLOCKS = 'blocks'
    __LINK_BLOCKED = 'blocked'
    #__LINK_A = 'A' # ToDo: replace by source
    #__LINK_B = 'B' # ToDo: replace by target
    __LINK_SOURCE = 'source'
    __LINK_TARGET = 'target'
    __LINK_ID = 'id'
    __TASK_TYPE = 'type'
    __TASK_ID = 'id'
    __TASK_EXT = 'ext'
    __TASK_DUEDATE = 'duedate'
    __TASK_STARTDATE = 'start_date'
    __TASK_ENDDATE = 'end_date'
    __TASK_ESTIMATE = 'estimate'
    __TASK_WHRS = 'whrs'
    __TASK_TEXT = 'text'
    __TASK_PARENT = 'parent'

    def __init__(self):
        super().__init__()
        self.__add_tasks()
        self.__add_links()

    def toString(self):
        self._logger.debug(self.tasks)
        self._logger.debug(self.links)

    def __add_tasks(self):
        backlog = Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_SPRINT_BACKLOG,
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI})
        assignments = Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_ASSIGNMENTS,
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI})
        date_aggs = Aggregator.agg_multi_func(assignments, ParamConstants.PARAM_DATE, ['min', 'max'], ParamConstants.PARAM_ITEM_KEY)
        time_aggs = Aggregator.agg_single_func(assignments, ParamConstants.PARAM_WHRS, 'sum', ParamConstants.PARAM_ITEM_KEY)
        for issue in backlog:
            start_date = date_aggs[issue[ParamConstants.PARAM_ITEM_KEY]]['min'] if issue[ParamConstants.PARAM_ITEM_KEY] in date_aggs else None
            end_date = date_aggs[issue[ParamConstants.PARAM_ITEM_KEY]]['max'] if issue[ParamConstants.PARAM_ITEM_KEY] in date_aggs else None
            # whrs = time_aggs[issue[ParamConstants.PARAM_ITEM_KEY]] if issue[ParamConstants.PARAM_ITEM_KEY] in time_aggs else None
            # type = issue[Gantt.__TASK_TYPE]
            # Gantt.__TASK_DUEDATE: issue[Gantt.__TASK_DUEDATE],
            # Gantt.__TASK_WHRS: whrs, Gantt.__TASK_EXT: False,
            # Gantt.__TASK_TEXT: issue[ParamConstants.PARAM_ITEM_KEY]})
            parent = issue[ParamConstants.PARAM_ITEM_PARENT]
            id = issue[ParamConstants.PARAM_ITEM_KEY]
            self._graph.add_node(id)
            node_attrs = {id: {Gantt.__TASK_ID: id, Gantt.__TASK_TEXT: id, Gantt.__TASK_STARTDATE: start_date,
                               Gantt.__TASK_ENDDATE: end_date, Gantt.__TASK_PARENT: parent, Gantt.__TASK_EXT: False}}
            nx.set_node_attributes(self._graph, node_attrs)
            #self._logger.debug('---> {}'.format(self._graph.nodes.data()))

    def __add_ext_task(self, node):
        if node not in self._graph.nodes:
            self._graph.add_node(node)
            nx.set_node_attributes(self._graph, {node: {Gantt.__TASK_EXT: True}})

    def __add_links(self):
        links = Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_BACKLOG_LINKS,
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI})
        for link in links:
            link_type = link[Gantt.__LINK_TYPE]
            link_source = link[Gantt.__LINK_SOURCE]
            link_target = link[Gantt.__LINK_TARGET]
            self.__add_ext_task(link_source)
            self.__add_ext_task(link_target)
            #link_attrs = {}
            #self._logger.debug('{}: {}->{}'.format(link_type, link_source, link_target))
            if link_type == Gantt.__LINK_BLOCKS: #in [Gantt.__LINK_SUBTASK, Gantt.__LINK_BLOCKS]:
                self._graph.add_edge(link_source, link_target) #, attr_dict={Gantt.__LINK_TYPE: link_type})
                self._logger.debug('{}: {}->{}'.format(link_type, link_source, link_target))
            elif link_type == Gantt.__LINK_BLOCKED and (link_target, link_source) not in self._graph.edges:
                #edge = (link_target, link_source)
                self._graph.add_edge(link_target, link_source) #, attr_dict={Gantt.__LINK_TYPE: Gantt.__LINK_BLOCKS})
                self._logger.debug('{}: {}->{}'.format(link_type, link_target, link_source))
            self._logger.debug('edges: {}'.format(self._graph.edges))

    @property
    def tasks(self):
        res = []
        for node in self._graph.nodes:
            node_attrs = self._graph.nodes[node]
            task = {}
            task.update({Gantt.__TASK_ID: node})
            task.update({Gantt.__TASK_TEXT: node})
            if node_attrs[Gantt.__TASK_EXT]:
                task.update({Gantt.__TASK_STARTDATE: '2017-10-14'})
                task.update({Gantt.__TASK_ENDDATE: '2017-10-15'})
            else:
                task.update({Gantt.__TASK_STARTDATE: Converter.convert(node_attrs[Gantt.__TASK_STARTDATE], Types.TYPE_STRING)})
                task.update({Gantt.__TASK_ENDDATE: Converter.convert(node_attrs[Gantt.__TASK_ENDDATE], Types.TYPE_STRING)})
                parent = node_attrs[Gantt.__TASK_PARENT]
                if parent:
                    task.update({Gantt.__TASK_PARENT: parent})
            res.append(task)
        return res

    @property
    def links(self):
        res = []
        for edge in self._graph.edges:
            link = {Gantt.__LINK_ID: '{}->{}'.format(edge[0], edge[1]), Gantt.__LINK_SOURCE: edge[0],
                    Gantt.__LINK_TARGET: edge[1], Gantt.__LINK_TYPE: 2}
            res.append(link)
        return res
