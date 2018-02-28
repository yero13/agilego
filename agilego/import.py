import argparse
import json
import logging.config
from framework.integration.importer import Importer
from framework.utils.cfg import CfgUtils
from framework.utils.env import get_env_params

CFG_LOG_IMPORT = './cfg/log/import-logging-config.json'
CFG_IMPORT = './cfg/jira/jira-import.json'

if __name__ == '__main__':
    with open(CFG_LOG_IMPORT) as log_cfg_file:
        logging.config.dictConfig(json.load(log_cfg_file, strict=False))
    env_cfg = get_env_params()
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser()
    parser.add_argument('--login', required=True)
    parser.add_argument('--pswd', required=True)
    args = parser.parse_args()

    try:
        logger.info('Init JIRA importer: {}'.format(CFG_IMPORT))
        with open(CFG_IMPORT) as cfg_file:
            cfg = json.loads(CfgUtils.substitute_params(cfg_file.read(), env_cfg))
        Importer(cfg, args.login, args.pswd).perform()
    except Exception as e:
        logging.error(e, exc_info=True)
