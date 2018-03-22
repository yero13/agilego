import argparse
import json
import logging.config
from na3x.integration.importer import Importer
from na3x.utils.cfg import CfgUtils
from na3x.cfg import init, get_env_params

CFG_LOG_IMPORT = './cfg/log/import-logging-config.json'
CFG_IMPORT_ACTUAL = './cfg/jira/jira-import-actual.json'
CFG_IMPORT_SCOPE = './cfg/jira/jira-import-scope.json'
CFG_NA3X = './cfg/na3x.json'

if __name__ == '__main__':
    with open(CFG_LOG_IMPORT) as log_cfg_file:
        logging.config.dictConfig(json.load(log_cfg_file, strict=False))
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser()
    parser.add_argument('--login', required=True)
    parser.add_argument('--pswd', required=True)
    parser.add_argument('--target', choices=['scope', 'actual'], required=True)
    args = parser.parse_args()

    try:
        cfg = CFG_IMPORT_SCOPE if args.target == 'scope' else CFG_IMPORT_ACTUAL
        logger.info('Init JIRA importer: {}'.format(cfg))
        with open(CFG_NA3X) as na3x_cfg_file:
            init(json.load(na3x_cfg_file, strict=False))
        with open(cfg) as cfg_file:
            cfg = json.loads(CfgUtils.substitute_params(cfg_file.read(), get_env_params()))
        Importer(cfg, args.login, args.pswd).perform()
    except Exception as e:
        logging.error(e, exc_info=True)
