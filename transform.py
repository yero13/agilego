import json
import logging.config

from db.connect import MongoDb
from db.constants import DbConstants
from scrum.sprint import Wbs, Sprint
from scrum.team import Team
from scrum.transformer import Transformer

CFG_LOG_TRANSFORM = './cfg/import-logging-config.json'
CFG_TRANSFORM = './cfg/scrum/scrum-transform.json'

if __name__ == '__main__':
    with open(CFG_LOG_TRANSFORM) as logging_cfg_file:
        logging.config.dictConfig(json.load(logging_cfg_file, strict=False))
    logger = logging.getLogger(__name__)

    db_src = MongoDb(DbConstants.CFG_DB_JIRA_IMPORT).connection # Todo: remove
    db_dest = MongoDb(DbConstants.CFG_DB_SCRUM).connection # Todo: remove
    try:
        logger.info('Init transformer: {}'.format(CFG_TRANSFORM))
        with open(CFG_TRANSFORM) as cfg_file:
            Transformer(json.load(cfg_file, strict=False)).transform_data()
        # ToDo: move source/dest for scrum to cfg file + generalize transform rules
        """
        Sprint(db_src[DbConstants.JIRA_IMPORT_SPRINT].find_one()).to_db(db_dest) # Todo: remove
        Team().to_db(db_dest) # Todo: remove
        Wbs.from_records(list(db_src[DbConstants.JIRA_IMPORT_BACKLOG].find({}, {'_id': False}))).to_db(db_dest) # Todo: remove
        """
    except Exception as e:
        logging.error(e, exc_info=True)
