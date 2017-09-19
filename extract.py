import argparse
import json
import logging.config

from jira.extractor import Extractor

LOG_CFG = './cfg/extract-logging-config.json'
EXTRACT_CFG = './cfg/jira/jira-extract.json'

if __name__ == '__main__':
    with open(LOG_CFG) as log_cfg_file:
        logging.config.dictConfig(json.load(log_cfg_file, strict=False))
    parser = argparse.ArgumentParser()
    parser.add_argument('--login', required=True)
    parser.add_argument('--pswd', required=True)
    args = parser.parse_args()
    logger = logging.getLogger(__name__)

    try:
        logger.info('Init JIRA extractor: {}'.format(EXTRACT_CFG))
        with open(EXTRACT_CFG) as cfg_file:
            Extractor(json.load(cfg_file, strict=False), args.login, args.pswd).extract()
    except Exception as e:
        logging.error(e, exc_info=True)
