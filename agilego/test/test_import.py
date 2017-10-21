import argparse
import json
import logging.config

CFG_LOG_TEST_DATA = './cfg/log/test-logging-config.json'
CFG_TEST_DATA = './cfg/test/jira-test-data.json'

import unittest
from integration.exporter import Exporter

class ImportTestCase(unittest.TestCase):
    def setUp(self):
        #ToDo:
        return

    def tearDown(self):
        #ToDo:
        return

"""

def suite():
    suite = unittest.TestSuite()
    suite.addTest(WidgetTestCase('test_default_widget_size'))
    suite.addTest(WidgetTestCase('test_widget_resize'))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())

"""

if __name__ == '__main__':
    with open(CFG_LOG_TEST_DATA) as logging_cfg_file:
        logging.config.dictConfig(json.load(logging_cfg_file, strict=False))
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser()
    parser.add_argument('--login', required=True)
    parser.add_argument('--pswd', required=True)
    args = parser.parse_args()

    try:
        logger.info('Init JIRA exporter: {}'.format(CFG_TEST_DATA))
        with open(CFG_TEST_DATA) as cfg_export_file:
            Exporter(json.load(cfg_export_file, strict=False), args.login, args.pswd).perform()
    except Exception as e:
        logging.error(e, exc_info=True)