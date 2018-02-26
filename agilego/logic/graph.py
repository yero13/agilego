import networkx as nx
import logging
from logic.constants import DbConstants
from db.data import Accessor, AccessParams


class SprintGraph:
    __EDGE_TYPE = 'type'
    __EDGE_TYPE_SUBTASK = 'subtask'
    __EDGE_TYPE_BLOCKS = 'blocks'
    __EDGE_TYPE_BLOCKED = 'blocked'
    __EDGE_A = 'A'
    __EDGE_B = 'B'
    __NODE_TYPE = 'type'
    __NODE_KEY = 'key'
    __NODE_EXT = 'ext'

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
        for issue in backlog:
            self.__graph.add_node(issue[SprintGraph.__NODE_KEY],
                                  attr_dict={SprintGraph.__NODE_TYPE: issue[SprintGraph.__NODE_TYPE],
                                             SprintGraph.__NODE_EXT: False})

    def __add_ext_node(self, node):
        if node not in self.__graph.nodes:
            self.__graph.add_node(node, attr_dict={SprintGraph.__NODE_EXT: True})

    def __add_edges(self):
        links = Accessor.factory(DbConstants.CFG_DB_SCRUM_API).get(
            {AccessParams.KEY_COLLECTION: DbConstants.SCRUM_BACKLOG_LINKS,
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI})
        for link in links:
            link_type = link[SprintGraph.__EDGE_TYPE]
            link_a = link[SprintGraph.__EDGE_A]
            link_b = link[SprintGraph.__EDGE_B]
            self.__add_ext_node(link_a)
            self.__add_ext_node(link_b)
            if link_type in [SprintGraph.__EDGE_TYPE_SUBTASK, SprintGraph.__EDGE_TYPE_BLOCKS]:
                self.__graph.add_edge(link_a, link_b, attr_dict={SprintGraph.__EDGE_TYPE: link_type})
            elif link_type == SprintGraph.__EDGE_TYPE_BLOCKED and (link_b, link_a) not in self.__graph.edges:
                self.__graph.add_edge(link_b, link_a, attr_dict={SprintGraph.__EDGE_TYPE: SprintGraph.__EDGE_TYPE_BLOCKS})
