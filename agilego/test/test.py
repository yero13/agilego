import json
import unittest
import logging.config
from integration.importer import Importer
from data.generator import Generator
from db.extractor import Extractor
from db.connect import MongoDb
from utils.cfg import CfgUtils

CFG_LOG_TEST = './cfg/log/test-logging-config.json'
CFG_DATA_GENERATION  = './cfg/data/jira-data-generation.json'
CFG_DATA_CLEANUP  = './cfg/data/jira-data-cleanup.json'
CFG_TEST_DATA_DB = 'jira-test-data'
CFG_TEST_ENV_PARAMS = 'env.params'
CFG_KEY_JIRA_LOGIN = 'jira_login'
CFG_KEY_JIRA_PSWD = 'jira_pswd'


with open(CFG_LOG_TEST) as logging_cfg_file:
    logging.config.dictConfig(json.load(logging_cfg_file, strict=False))


def get_env_params():
    return Extractor(CFG_TEST_DATA_DB).get(
        {Extractor.CFG_KEY_COLLECTION: CFG_TEST_ENV_PARAMS, Extractor.CFG_KEY_TYPE: Extractor.CFG_KEY_TYPE_SINGLE})


def setUpModule():
    test_env_cfg = get_env_params()
    with open(CFG_DATA_GENERATION) as cfg_file:
        Generator(json.load(cfg_file, strict=False), test_env_cfg[CFG_KEY_JIRA_LOGIN],
              test_env_cfg[CFG_KEY_JIRA_PSWD], test_env_cfg).perform()


def tearDownModule():
    test_env_cfg = get_env_params()
    with open(CFG_DATA_CLEANUP) as cfg_file:
        Generator(json.load(cfg_file, strict=False), test_env_cfg[CFG_KEY_JIRA_LOGIN],
              test_env_cfg[CFG_KEY_JIRA_PSWD], test_env_cfg).perform()


class ImportTestCase(unittest.TestCase):
    __CFG_IMPORT = './cfg/jira/jira-import.json'
    __CFG_IMPORT_DB = 'db_jira_import'
    __COL_BACKLOG = 'backlog'
    __COL_SPRINT = 'sprint'
    __COL_EMPLOYEES = 'employees'
    __COL_COMPONENTS = 'components'

    def setUp(self):
        logger = logging.getLogger(__name__)
        self.__test_env_cfg = get_env_params()
        try:
            logger.info('Init JIRA test data importer: {}'.format(CFG_IMPORT))
            with open(ImportTestCase.__CFG_IMPORT) as cfg_file:
                cfg = json.loads(CfgUtils.substitute_params(cfg_file.read(), self.__test_env_cfg))
            Importer(cfg, self.__test_env_cfg[CFG_KEY_JIRA_LOGIN], self.__test_env_cfg[CFG_KEY_JIRA_PSWD]).perform()
        except Exception as e:
            logging.error(e, exc_info=True)

    def test_import(self):
        collections = MongoDb(self.__test_env_cfg[ImportTestCase.__CFG_IMPORT_DB]).connection.collection_names()
        logger = logging.getLogger(__name__)
        logger.info(collections)
        self.assertIn(ImportTestCase.__COL_BACKLOG, collections)
        self.assertIn(ImportTestCase.__COL_SPRINT, collections)
        self.assertIn(ImportTestCase.__COL_EMPLOYEES, collections)
        self.assertIn(ImportTestCase.__COL_COMPONENTS, collections)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(ImportTestCase('test_import'))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
