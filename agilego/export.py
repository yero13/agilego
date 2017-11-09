import argparse
import json
import logging.config
from utils.cfg import CfgUtils

from integration.exporter import Exporter
from transformation.transformer import Transformer

CFG_LOG_EXPORT = './cfg/log/export-logging-config.json'
CFG_TRANSFORM = './cfg/scrum/scrum-export-transform.json'
CFG_EXPORT = './cfg/jira/jira-export.json'
CFG_ENV = './cfg/env.json'

if __name__ == '__main__':
    with open(CFG_LOG_EXPORT) as logging_cfg_file:
        logging.config.dictConfig(json.load(logging_cfg_file, strict=False))
    with open(CFG_ENV) as env_cfg_file:
        env_cfg = json.load(env_cfg_file, strict=False)
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser()
    parser.add_argument('--login', required=True)
    parser.add_argument('--pswd', required=True)
    args = parser.parse_args()

    try:
        logger.info('Init transformer: {}'.format(CFG_TRANSFORM))
        with open(CFG_TRANSFORM) as cfg_file:
            cfg = json.loads(CfgUtils.substitute_params(cfg_file.read(), env_cfg))
        Transformer(cfg).transform_data()
        logger.info('Init JIRA exporter: {}'.format(CFG_EXPORT))
        with open(CFG_EXPORT) as cfg_file:
            cfg = json.loads(CfgUtils.substitute_params(cfg_file.read(), env_cfg))
        Exporter(cfg, args.login, args.pswd).perform()
    except Exception as e:
        logging.error(e, exc_info=True)
