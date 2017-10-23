import json
import unittest
from test.test_import import ImportTestCase
import logging.config
from integration.exporter import Exporter

CFG_LOG_TEST = './cfg/log/test-logging-config.json'
CFG_TEST_DATA = './cfg/test/jira-test-data.json'
CFG_TEST_DATA_CLEANUP = './cfg/test/jira-test-data-cleanup.json'


def setUpModule():
    with open(CFG_LOG_TEST) as log_cfg_file:
        logging.config.dictConfig(json.load(log_cfg_file, strict=False))
    logger = logging.getLogger(__name__)
    try:
        logger.info('Init JIRA test data creation exporter: {}'.format(CFG_TEST_DATA))
        with open(CFG_TEST_DATA) as cfg_export_file:
            Exporter(json.load(cfg_export_file, strict=False)).perform()
    except Exception as e:
        logging.error(e, exc_info=True)

def tearDownModule():
    logger = logging.getLogger(__name__)
    try:
        logger.info('Init JIRA test data cleanup exporter: {}'.format(CFG_TEST_DATA))
        with open(CFG_TEST_DATA_CLEANUP) as cfg_export_file:
            Exporter(json.load(cfg_export_file, strict=False)).perform()
    except Exception as e:
        logging.error(e, exc_info=True)


class EmptyTestCase(unittest.TestCase):
    def test(self):
        logger = logging.getLogger(__name__)
        print('>>>>>>>>>>>>>>>aaaaaaaaaaaaa1111')
        logger.info('>>>>>>>>>>>>>>>aaaaaaaaaaaaaa')


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(EmptyTestCase('test'))
    suite.addTest(ImportTestCase('test_import_users'))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
