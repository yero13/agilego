import json
import unittest
import logging.config
from integration.importer import Importer
from data.DataGenerator import DataGenerator

CFG_IMPORT = './cfg/jira/jira-import.json'
CFG_LOG_TEST = './cfg/log/test-logging-config.json'

CFG_MAPPING = 'mapping'
CFG_MAPPING_URL = 'url'
CFG_MAPPING_PROJECT = 'project'
TEST_PROJECT = 'TEST'
CFG_MAPPING_SPRINT = 'sprint'
TEST_SPRINT = '1'
TEST_JIRA_URL = 'http://192.168.254.129:8080'
CFG_DB = 'db'
TEST_DB = 'jira-test-data'

cfg_data_gen = {
    DataGenerator.CFG_JIRA_URL: 'http://192.168.254.129:8080',
    DataGenerator.CFG_STATIC_ENTITIES_EXPORT: './cfg/test/jira-test-data.json',
    DataGenerator.CFG_DYNAMIC_ENTITIES_IMPORT: './cfg/test/jira-test-data-ext.json',
    DataGenerator.CFG_ENTITIES_CLEANUP: './cfg/test/jira-test-data-cleanup.json'
}

dg = DataGenerator(cfg_data_gen, 'jira', 'jira')

def set_test_env(cfg):
    cfg[CFG_MAPPING][CFG_MAPPING_URL] = TEST_JIRA_URL
    cfg[CFG_DB] = TEST_DB


def set_test_project(cfg):
    cfg[CFG_MAPPING][CFG_MAPPING_PROJECT] = TEST_PROJECT
    cfg[CFG_MAPPING][CFG_MAPPING_SPRINT] = TEST_SPRINT


def setUpModule():
    with open(CFG_LOG_TEST) as logging_cfg_file:
        logging.config.dictConfig(json.load(logging_cfg_file, strict=False))
    dg.generate()


def tearDownModule():
    dg.cleanup()


class ImportTestCase(unittest.TestCase):
    def setUp(self):
        logger = logging.getLogger(__name__)
        try:
            logger.info('Init JIRA test data importer: {}'.format(CFG_IMPORT))
            with open(CFG_IMPORT) as cfg_file:
                cfg = json.load(cfg_file, strict=False)
            set_test_env(cfg)
            set_test_project(cfg)
            Importer(cfg, 'jira', 'jira').perform()
        except Exception as e:
            logging.error(e, exc_info=True)


    def test_import(self):
        logger = logging.getLogger(__name__)
        print('>>>>>>>>>>>>>>>aaaaaaaaaaaaa1111')
        logger.info('>>>>>>>>>>>>>>>aaaaaaaaaaaaaa')


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(ImportTestCase('test_import'))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
