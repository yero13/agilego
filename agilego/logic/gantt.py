import logging
import networkx as nx
from framework.db.data import Accessor, AccessParams
from framework.utils.aggregator import Aggregator
from logic.constants import DbConstants, ParamConstants


# ToDo: this class should be optimized to work with sevaral data sets
class Gantt:
    __LINK_TYPE = 'type'
    __LINK_SUBTASK = 'subtask'
    __LINK_BLOCKS = 'blocks'
    __LINK_BLOCKED = 'blocked'
    __LINK_A = 'A'
    __LINK_B = 'B'
    __TASK_TYPE = 'type'
    __TASK_KEY = 'key'
    __TASK_EXT = 'ext'
    __TASK_DUEDATE = 'duedate'
    __TASK_STARTDATE = 'startdate'
    __TASK_ENDDATE = 'enddate'
    __TASK_ESTIMATE = 'estimate'
    __TASK_WHRS = 'whrs'

    def __init__(self):
        self.__logger = logging.getLogger(__class__.__name__)
        self.__graph = nx.Graph()
        self.__add_tasks()
        self.__add_links()

    def toString(self):
        for node in self.__graph.nodes:
            self.__logger.debug('node: {} {}'.format(node, self.__graph.nodes[node]))
        for edge in self.__graph.edges:
            self.__logger.debug('edge: {} {}'.format(edge, self.__graph.edges[edge]))
        return '\n{}\n{}\n'.format(self.__graph.nodes, self.__graph.edges)

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
            whrs = time_aggs[issue[ParamConstants.PARAM_ITEM_KEY]] if issue[ParamConstants.PARAM_ITEM_KEY] in time_aggs else None
            self.__graph.add_node(issue[Gantt.__TASK_KEY],
                                  attr_dict={Gantt.__TASK_TYPE: issue[ParamConstants.PARAM_ITEM_KEY],
                                             Gantt.__TASK_DUEDATE: issue[Gantt.__TASK_DUEDATE],
                                             Gantt.__TASK_STARTDATE: start_date,
                                             Gantt.__TASK_ENDDATE: end_date,
                                             Gantt.__TASK_ESTIMATE: issue[Gantt.__TASK_ESTIMATE],
                                             Gantt.__TASK_WHRS: whrs,
                                             Gantt.__TASK_EXT: False})

    def __add_ext_task(self, node):
        if node not in self.__graph.nodes:
            self.__graph.add_node(node, attr_dict={Gantt.__TASK_EXT: True})

    def __add_links(self):
        links = Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_BACKLOG_LINKS,
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI})
        for link in links:
            link_type = link[Gantt.__LINK_TYPE]
            link_a = link[Gantt.__LINK_A]
            link_b = link[Gantt.__LINK_B]
            self.__add_ext_task(link_a)
            self.__add_ext_task(link_b)
            if link_type in [Gantt.__LINK_SUBTASK, Gantt.__LINK_BLOCKS]:
                self.__graph.add_edge(link_a, link_b, attr_dict={Gantt.__LINK_TYPE: link_type})
            elif link_type == Gantt.__LINK_BLOCKED and (link_b, link_a) not in self.__graph.edges:
                self.__graph.add_edge(link_b, link_a, attr_dict={Gantt.__LINK_TYPE: Gantt.__LINK_BLOCKS})

    def chart(self):
        pass