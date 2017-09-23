import logging
from db.connect import MongoDb


class TransformationSet:
    __CFG_KEY_DB = 'db'
    __CFG_KEY_TRANSFORMATION = 'transformations'

    def __init__(self, cfg):
        self.__cfg = cfg
        self.__logger = logging.getLogger(__class__.__name__)

    def __init_db(self):
        self.__dbs = {}

    def transform_data(self):
        return

class Transformer():
    __CFG_KEY_TRANSFORMATION_SETS = 'transformation-sets'

    def __init__(self, cfg):
        self.__cfg = cfg
        self.__logger = logging.getLogger(__class__.__name__)

    def transform_data(self):
        for transform_set in self.__cfg[Transformer.__CFG_KEY_TRANSFORMATION_SETS]:
            TransformationSet(self.__cfg[Transformer.__CFG_KEY_TRANSFORMATION_SETS]).transform()

