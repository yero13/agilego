import json
import logging.config
from utils.cfg import CfgUtils
from transformation.transformer import Transformer

CFG_LOG_TRANSFORM = './cfg/log/transform-logging-config.json'
CFG_TRANSFORM = './cfg/scrum/scrum-import-transform.json'
CFG_ENV = './cfg/env.json'

if __name__ == '__main__':
    with open(CFG_LOG_TRANSFORM) as logging_cfg_file:
        logging.config.dictConfig(json.load(logging_cfg_file, strict=False))
    logger = logging.getLogger(__name__)
    with open(CFG_ENV) as env_cfg_file:
        env_cfg = json.load(env_cfg_file, strict=False)
    try:
        logger.info('Init transformer: {}'.format(CFG_TRANSFORM))
        with open(CFG_TRANSFORM) as cfg_file:
            cfg = json.loads(CfgUtils.substitute_params(cfg_file.read(), env_cfg))
        Transformer(cfg).transform_data()
    except Exception as e:
        logging.error(e, exc_info=True)
