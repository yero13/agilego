import json
import logging.config
from utils.cfg import CfgUtils
from transformation.transformer import Transformer
from utils.env import get_env_params

CFG_LOG_TRANSFORM = './cfg/log/transform-logging-config.json'
CFG_TRANSFORM = './cfg/scrum/scrum-import-transform.json'

if __name__ == '__main__':
    with open(CFG_LOG_TRANSFORM) as logging_cfg_file:
        logging.config.dictConfig(json.load(logging_cfg_file, strict=False))
    logger = logging.getLogger(__name__)
    env_cfg = get_env_params()
    try:
        logger.info('Init transformer: {}'.format(CFG_TRANSFORM))
        with open(CFG_TRANSFORM) as cfg_file:
            cfg = json.loads(CfgUtils.substitute_params(cfg_file.read(), env_cfg))
        Transformer(cfg).transform_data()
    except Exception as e:
        logging.error(e, exc_info=True)
