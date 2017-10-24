import logging
from integration.exporter import Exporter
from integration.importer import Importer
import json


class DataGenerator():
    CFG_JIRA_URL = 'cfg_jira_url'
    CFG_STATIC_ENTITIES_EXPORT = 'cfg_static_entities'
    CFG_DYNAMIC_ENTITIES_IMPORT = 'cfg_dynamic_entities'
    CFG_ENTITIES_CLEANUP = 'cfg_entities_cleanup'

    def __init__(self, cfg, login, pswd):
        self.__logger = logging.getLogger(__class__.__name__)
        self.__login = login
        self.__pswd = pswd
        self.__cfg = cfg

    def generate(self):
        try:
            self.__logger.info('Init JIRA data creation exporter: {}'.format(self.__cfg[DataGenerator.CFG_STATIC_ENTITIES_EXPORT]))
            with open(self.__cfg[DataGenerator.CFG_STATIC_ENTITIES_EXPORT]) as cfg_static_entities_export_file:
                Exporter(json.load(cfg_static_entities_export_file, strict=False), self.__login, self.__pswd).perform()
            with open(self.__cfg[DataGenerator.CFG_DYNAMIC_ENTITIES_IMPORT]) as cfg_data_ext_file:
                Importer(json.load(cfg_data_ext_file, strict=False), self.__login, self.__pswd).perform()
        except Exception as e:
            logging.error(e, exc_info=True)


    def cleanup(self):
        try:
            self.__logger.info('Init JIRA test data cleanup exporter: {}'.format(self.__cfg[DataGenerator.CFG_ENTITIES_CLEANUP]))
            with open(self.__cfg[DataGenerator.CFG_ENTITIES_CLEANUP]) as cfg_cleanup_entities_export_file:
                Exporter(json.load(cfg_cleanup_entities_export_file, strict=False), self.__login, self.__pswd).perform()
        except Exception as e:
            logging.error(e, exc_info=True)


