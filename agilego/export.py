import argparse
import json
import logging.config

from integration.exporter import Exporter
from transformation.transformer import Transformer

CFG_LOG_EXPORT = './cfg/log/export-logging-config.json'
CFG_TRANSFORM = './cfg/scrum/scrum-export-transform.json'
CFG_EXPORT = './cfg/jira/jira-export.json'

if __name__ == '__main__':
    with open(CFG_LOG_EXPORT) as logging_cfg_file:
        logging.config.dictConfig(json.load(logging_cfg_file, strict=False))
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser()
    parser.add_argument('--login', required=True)
    parser.add_argument('--pswd', required=True)
    args = parser.parse_args()

    try:
        logger.info('Init transformer: {}'.format(CFG_TRANSFORM))
        with open(CFG_TRANSFORM) as cfg_transform_file:
            Transformer(json.load(cfg_transform_file, strict=False)).transform_data()
        logger.info('Init JIRA exporter: {}'.format(CFG_EXPORT))
        with open(CFG_EXPORT) as cfg_export_file:
            Exporter(json.load(cfg_export_file, strict=False), args.login, args.pswd).perform()
    except Exception as e:
        logging.error(e, exc_info=True)
