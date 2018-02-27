import networkx as nx
import logging
from logic.constants import DbConstants, ParamConstants
from db.data import Accessor, AccessParams
from utils.aggregator import Aggregator


class GanntGraph:
    __EDGE_ATTR_TYPE = 'type'
    __EDGE_TYPE_SUBTASK = 'subtask'
    __EDGE_TYPE_BLOCKS = 'blocks'
    __EDGE_TYPE_BLOCKED = 'blocked'
    __EDGE_A = 'A'
    __EDGE_B = 'B'
    __NODE_ATTR_TYPE = 'type'
    __NODE_ATTR_KEY = 'key'
    __NODE_ATTR_EXT = 'ext'
    __NODE_ATTR_DUEDATE = 'duedate'
    __NODE_ATTR_STARTDATE = 'startdate'
    __NODE_ATTR_ENDDATE = 'enddate'
    __NODE_ATTR_ESTIMATE = 'estimate'
    __NODE_ATTR_WHRS = 'whrs'

    def __init__(self):
        self.__logger = logging.getLogger(__class__.__name__)
        self.__graph = nx.Graph()
        self.__add_nodes()
        self.__add_edges()

    def toString(self):
        for node in self.__graph.nodes:
            self.__logger.debug('node: {} {}'.format(node, self.__graph.nodes[node]))
        for edge in self.__graph.edges:
            self.__logger.debug('edge: {} {}'.format(edge, self.__graph.edges[edge]))
        return '\n{}\n{}\n'.format(self.__graph.nodes, self.__graph.edges)

    def __add_nodes(self):
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
            self.__graph.add_node(issue[GanntGraph.__NODE_ATTR_KEY],
                                  attr_dict={GanntGraph.__NODE_ATTR_TYPE: issue[ParamConstants.PARAM_ITEM_KEY],
                                             GanntGraph.__NODE_ATTR_DUEDATE: issue[GanntGraph.__NODE_ATTR_DUEDATE],
                                             GanntGraph.__NODE_ATTR_STARTDATE: start_date,
                                             GanntGraph.__NODE_ATTR_ENDDATE: end_date,
                                             GanntGraph.__NODE_ATTR_ESTIMATE: issue[GanntGraph.__NODE_ATTR_ESTIMATE],
                                             GanntGraph.__NODE_ATTR_WHRS: whrs,
                                             GanntGraph.__NODE_ATTR_EXT: False})

    def __add_ext_node(self, node):
        if node not in self.__graph.nodes:
            self.__graph.add_node(node, attr_dict={GanntGraph.__NODE_ATTR_EXT: True})

    def __add_edges(self):
        links = Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_BACKLOG_LINKS,
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI})
        for link in links:
            link_type = link[GanntGraph.__EDGE_ATTR_TYPE]
            link_a = link[GanntGraph.__EDGE_A]
            link_b = link[GanntGraph.__EDGE_B]
            self.__add_ext_node(link_a)
            self.__add_ext_node(link_b)
            if link_type in [GanntGraph.__EDGE_TYPE_SUBTASK, GanntGraph.__EDGE_TYPE_BLOCKS]:
                self.__graph.add_edge(link_a, link_b, attr_dict={GanntGraph.__EDGE_ATTR_TYPE: link_type})
            elif link_type == GanntGraph.__EDGE_TYPE_BLOCKED and (link_b, link_a) not in self.__graph.edges:
                self.__graph.add_edge(link_b, link_a, attr_dict={GanntGraph.__EDGE_ATTR_TYPE: GanntGraph.__EDGE_TYPE_BLOCKS})
