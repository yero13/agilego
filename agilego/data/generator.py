import logging
from integration.exporter import Exporter
from integration.importer import Importer
import json
from utils.cfg import CfgUtils


class Generator():
    # ToDo: remove
    CFG_KEY_JIRA_URL = 'cfg_jira_url'
    CFG_KEY_STATIC_ENTITIES_EXPORT = 'cfg_static_entities'
    CFG_KEY_DYNAMIC_ENTITIES_IMPORT = 'cfg_dynamic_entities'
    CFG_KEY_ENTITIES_CLEANUP = 'cfg_entities_cleanup'
    CFG_KEY_DB_ENTITIES = 'db'

    __CFG_KEY_STEPS = 'steps'
    __CFG_KEY_STEP_TYPE = 'type'
    __CFG_STEP_TYPE_EXPORT = 'jira.export'
    __CFG_STEP_TYPE_IMPORT = 'jira.import'
    __CFG_STEP_TYPE_TRANSFORMATION = 'db.transformation'
    __CFG_KEY_STEP_CFG = 'cfg'

    def __init__(self, cfg, login, pswd, env_params):
        self.__logger = logging.getLogger(__class__.__name__)
        self.__login = login
        self.__pswd = pswd
        self.__cfg = cfg
        self.__env_cfg = env_params

    def perform(self):
        try:
            for step in self.__cfg[Generator.__CFG_KEY_STEPS]:
                step_type = self.__cfg[Generator.__CFG_KEY_STEPS][step][Generator.__CFG_KEY_STEP_TYPE]
                step_cfg_file = self.__cfg[Generator.__CFG_KEY_STEPS][step][Generator.__CFG_KEY_STEP_CFG]
                self.__logger.info('Perform data generation step: {}, type: {}, configuration: {}'.format(step, step_type, step_cfg_file))
                with open(step_cfg_file) as cfg_file:
                    str_cfg = cfg_file.read()
                step_cfg = json.loads(CfgUtils.substitute_params(str_cfg, self.__env_cfg))
                if step_type == Generator.__CFG_STEP_TYPE_EXPORT:
                    Exporter(step_cfg, self.__login, self.__pswd).perform()
                elif step_type == Generator.__CFG_STEP_TYPE_IMPORT:
                    Importer(step_cfg, self.__login, self.__pswd).perform()
                elif step_type == Generator.__CFG_STEP_TYPE_TRANSFORMATION:
                    pass
        except Exception as e:
            logging.error(e, exc_info=True)



    #ToDo: remove
    def generate(self):
        try:
            self.__logger.info('Init JIRA data creation exporter: {}'.format(self.__cfg[Generator.CFG_KEY_STATIC_ENTITIES_EXPORT]))
            with open(self.__cfg[Generator.CFG_KEY_STATIC_ENTITIES_EXPORT]) as cfg_static_entities_export_file:
                Exporter(json.load(cfg_static_entities_export_file, strict=False), self.__login, self.__pswd).perform()
            with open(self.__cfg[Generator.CFG_KEY_DYNAMIC_ENTITIES_IMPORT]) as cfg_data_ext_file:
                Importer(json.load(cfg_data_ext_file, strict=False), self.__login, self.__pswd).perform()
        except Exception as e:
            logging.error(e, exc_info=True)


    def cleanup(self):
        try:
            self.__logger.info('Init JIRA test data cleanup exporter: {}'.format(self.__cfg[Generator.CFG_KEY_ENTITIES_CLEANUP]))
            with open(self.__cfg[Generator.CFG_KEY_ENTITIES_CLEANUP]) as cfg_cleanup_entities_export_file:
                Exporter(json.load(cfg_cleanup_entities_export_file, strict=False), self.__login, self.__pswd).perform()
        except Exception as e:
            logging.error(e, exc_info=True)


