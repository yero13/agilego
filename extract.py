import argparse
import json
import logging.config

from db.connect import MongoDb
from db.constants import DbConstants

from extract.jira.backlog import SprintBacklogRequest
from extract.jira.sprint import SprintDefinitionRequest

# ToDo: move log config to separate file
LOG_CFG = './extract/cfg/logging-config.json'

if __name__ == '__main__':
    with open(LOG_CFG) as log_cfg_file:
        logging.config.dictConfig(json.load(log_cfg_file, strict=False))
    parser = argparse.ArgumentParser()
    parser.add_argument('--login', required=True)
    parser.add_argument('--pswd', required=True)
    args = parser.parse_args()
    logger = logging.getLogger(__name__)

    try:
        logger.debug('call parameters {} , {}'.format(args.login, args.pswd))
        db = MongoDb(DbConstants.CFG_DB_EXTRACT).connection
        db[DbConstants.EXTRACT_SPRINT].drop()
        db[DbConstants.EXTRACT_BACKLOG].drop()
        sprint_data = SprintDefinitionRequest(args.login, args.pswd).result
        db[DbConstants.EXTRACT_SPRINT].insert_one(sprint_data)
        logger.info('collection: {} sprint data {} is saved'.format(DbConstants.EXTRACT_SPRINT, sprint_data))
        backlog_data = SprintBacklogRequest(args.login, args.pswd).result
        db[DbConstants.EXTRACT_BACKLOG].insert_many([{issue: backlog_data[issue]} for issue in backlog_data])
        logger.info('collection: {} {:d} items are saved'.format(DbConstants.EXTRACT_BACKLOG, len(backlog_data.keys())))
    except Exception as e:
        logging.error(e, exc_info=True)
