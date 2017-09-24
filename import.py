import argparse
import json
import logging.config

from jira.importer import Importer

CFG_LOG_IMPORT = './cfg/import-logging-config.json'
CFG_IMPORT = './cfg/jira/jira-import.json'

if __name__ == '__main__':
    with open(CFG_LOG_IMPORT) as log_cfg_file:
        logging.config.dictConfig(json.load(log_cfg_file, strict=False))
    parser = argparse.ArgumentParser()
    parser.add_argument('--login', required=True)
    parser.add_argument('--pswd', required=True)
    args = parser.parse_args()
    logger = logging.getLogger(__name__)

    try:
        logger.info('Init JIRA importer: {}'.format(CFG_IMPORT))
        with open(CFG_IMPORT) as cfg_file:
            Importer(json.load(cfg_file, strict=False), args.login, args.pswd).import_data()
    except Exception as e:
        logging.error(e, exc_info=True)
