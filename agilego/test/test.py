import json
import unittest
import logging.config
from integration.importer import Importer
from data.generator import Generator
from utils.cfg import CfgUtils

CFG_IMPORT = './cfg/jira/jira-import.json'
CFG_LOG_TEST = './cfg/log/test-logging-config.json'
CFG_DATA_GENERATION  = './cfg/data/jira-data-generation.json'
CFG_DATA_CLEANUP  = './cfg/data/jira-data-cleanup.json'
CFG_TEST_ENV = './cfg/test/test-env-params.json'
CFG_KEY_JIRA_LOGIN = 'jira_login'
CFG_KEY_JIRA_PSWD = 'jira_pswd'


with open(CFG_LOG_TEST) as logging_cfg_file:
    logging.config.dictConfig(json.load(logging_cfg_file, strict=False))
with open(CFG_TEST_ENV) as test_env_cfg_file:
    test_env_cfg = json.load(test_env_cfg_file, strict=False)


def setUpModule():
    with open(CFG_DATA_GENERATION) as cfg_file:
        Generator(json.load(cfg_file, strict=False), test_env_cfg[CFG_KEY_JIRA_LOGIN],
              test_env_cfg[CFG_KEY_JIRA_PSWD], test_env_cfg).perform()


def tearDownModule():
    with open(CFG_DATA_CLEANUP) as cfg_file:
        Generator(json.load(cfg_file, strict=False), test_env_cfg[CFG_KEY_JIRA_LOGIN],
              test_env_cfg[CFG_KEY_JIRA_PSWD], test_env_cfg).perform()


class ImportTestCase(unittest.TestCase):
    def setUp(self):
        logger = logging.getLogger(__name__)
        try:
            logger.info('Init JIRA test data importer: {}'.format(CFG_IMPORT))
            with open(CFG_IMPORT) as cfg_file:
                cfg = json.loads(CfgUtils.substitute_params(cfg_file.read(), test_env_cfg))
            Importer(cfg, test_env_cfg[CFG_KEY_JIRA_LOGIN], test_env_cfg[CFG_KEY_JIRA_PSWD]).perform()
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
