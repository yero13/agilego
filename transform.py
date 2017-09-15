import json
import logging.config

from db.connect import MongoDb
from db.constants import DbConstants
from transform.scrum.sprint import Wbs, Sprint


# ToDo: move log config to separate file
LOGGING_CONFIG = './transform/cfg/logging-config.json'

if __name__ == '__main__':
    with open(LOGGING_CONFIG) as logging_cfg_file:
        logging.config.dictConfig(json.load(logging_cfg_file, strict=False))
    logger = logging.getLogger(__name__)
    db = MongoDb(DbConstants.CFG_DB_TRANSFORM).connection
    try:
        # ToDo: move source for transform to cfg file + generalize transform rules
        with open('./data/jira-sprint.json') as data_file:
            Sprint(json.load(data_file, strict=False)).to_db(db)
        with open('./data/jira-backlog.json') as data_file:
            Wbs.from_dict(json.load(data_file, strict=False)).to_db(db)
    except Exception as e:
        logging.error(e, exc_info=True)
