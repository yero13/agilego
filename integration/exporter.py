import logging
from db.connect import MongoDb


class Exporter():
    def __init__(self):
        self.__cfg = cfg
        self.__logger = logging.getLogger(__class__.__name__)

