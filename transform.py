import json
import logging.config

from services.constants import ApiConstants
from db.connect import MongoDb
from transformation.team import Team
from transformation.transformer import Transformer

CFG_LOG_TRANSFORM = './cfg/transform-logging-config.json'
CFG_TRANSFORM = './cfg/scrum/scrum-transform.json'

if __name__ == '__main__':
    with open(CFG_LOG_TRANSFORM) as logging_cfg_file:
        logging.config.dictConfig(json.load(logging_cfg_file, strict=False))
    logger = logging.getLogger(__name__)

    db_dest = MongoDb(ApiConstants.CFG_DB_SCRUM_API).connection # Todo: remove
    try:
        logger.info('Init transformer: {}'.format(CFG_TRANSFORM))
        with open(CFG_TRANSFORM) as cfg_file:
            Transformer(json.load(cfg_file, strict=False)).transform_data()
        Team().to_db(db_dest) # Todo: remove
    except Exception as e:
        logging.error(e, exc_info=True)
