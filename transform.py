import json
import logging.config

from db.connect import MongoDb
from db.constants import DbConstants
from scrum.sprint import Wbs, Sprint
from scrum.team import Team

# ToDo: move log config to separate file
LOGGING_CONFIG = './cfg/transform-logging-config.json'

if __name__ == '__main__':
    with open(LOGGING_CONFIG) as logging_cfg_file:
        logging.config.dictConfig(json.load(logging_cfg_file, strict=False))
    logger = logging.getLogger(__name__)
    db_src = MongoDb(DbConstants.CFG_DB_JIRA_IMPORT).connection
    db_dest = MongoDb(DbConstants.CFG_DB_SCRUM).connection
    try:
        # ToDo: move source/dest for scrum to cfg file + generalize transform rules
        Sprint(db_src[DbConstants.JIRA_IMPORT_SPRINT].find_one()).to_db(db_dest)
        Team().to_db(db_dest)
        Wbs.from_records(list(db_src[DbConstants.JIRA_IMPORT_BACKLOG].find({}, {'_id': False}))).to_db(db_dest)
    except Exception as e:
        logging.error(e, exc_info=True)
