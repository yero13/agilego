import argparse
import json
import logging.config
from natrix.integration.importer import Importer
from natrix.utils.cfg import CfgUtils
from natrix.cfg import init, get_env_params

CFG_LOG_IMPORT = './cfg/log/import-logging-config.json'
CFG_IMPORT = './cfg/jira/jira-import.json'
CFG_NATRIX = './cfg/natrix.json'

if __name__ == '__main__':
    with open(CFG_LOG_IMPORT) as log_cfg_file:
        logging.config.dictConfig(json.load(log_cfg_file, strict=False))
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser()
    parser.add_argument('--login', required=True)
    parser.add_argument('--pswd', required=True)
    args = parser.parse_args()

    try:
        logger.info('Init JIRA importer: {}'.format(CFG_IMPORT))
        with open(CFG_NATRIX) as natrix_cfg_file:
            init(json.load(natrix_cfg_file, strict=False))
        with open(CFG_IMPORT) as cfg_file:
            cfg = json.loads(CfgUtils.substitute_params(cfg_file.read(), get_env_params()))
        Importer(cfg, args.login, args.pswd).perform()
    except Exception as e:
        logging.error(e, exc_info=True)
