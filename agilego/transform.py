import argparse
import json
import logging.config
from na3x.transformation.transformer import Transformer
from na3x.cfg import init

CFG_LOG_TRANSFORM = './cfg/log/transform-logging-config.json'
CFG_TRANSFORM_SCOPE = './cfg/scrum/scrum-import-scope-transform.json'
CFG_TRANSFORM_ACTUAL = './cfg/scrum/scrum-import-actual-transform.json'
CFG_NA3X = './cfg/na3x.json'

if __name__ == '__main__':
    with open(CFG_LOG_TRANSFORM) as logging_cfg_file:
        logging.config.dictConfig(json.load(logging_cfg_file, strict=False))
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', choices=['scope', 'actual'], required=True)
    args = parser.parse_args()

    try:
        cfg = CFG_TRANSFORM_SCOPE if args.target == 'scope' else CFG_TRANSFORM_ACTUAL
        with open(CFG_NA3X) as na3x_cfg_file:
            init(json.load(na3x_cfg_file, strict=False))
        logger.info('Init transformer: {}'.format(cfg))
        with open(cfg) as cfg_file:
            Transformer(json.load(cfg_file, strict=False)).transform_data()
    except Exception as e:
        logging.error(e, exc_info=True)
