import json
import logging.config
from natrix.transformation.transformer import Transformer
from natrix.cfg import init

CFG_LOG_TRANSFORM = './cfg/log/transform-logging-config.json'
CFG_TRANSFORM = './cfg/scrum/scrum-import-transform.json'
CFG_NATRIX = './cfg/natrix.json'

if __name__ == '__main__':
    with open(CFG_LOG_TRANSFORM) as logging_cfg_file:
        logging.config.dictConfig(json.load(logging_cfg_file, strict=False))
    logger = logging.getLogger(__name__)
    try:
        with open(CFG_NATRIX) as natrix_cfg_file:
            init(json.load(natrix_cfg_file, strict=False))
        logger.info('Init transformer: {}'.format(CFG_TRANSFORM))
        with open(CFG_TRANSFORM) as cfg_file:
            Transformer(json.load(cfg_file, strict=False)).transform_data()
    except Exception as e:
        logging.error(e, exc_info=True)
