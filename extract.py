import argparse
import json
import logging.config

from db.connect import MongoDb

from jira.backlog import SprintBacklogRequest
from jira.sprint import SprintDefinitionRequest


LOGGING_CONFIG = './extract/cfg/logging-config.json'


if __name__ == '__main__':
    with open(LOGGING_CONFIG) as logging_cfg_file:
        logging.config.dictConfig(json.load(logging_cfg_file, strict=False))
    parser = argparse.ArgumentParser()
    # ToDo: split to extract.py, transform.py, etc
    parser.add_argument('--login', required=True)
    parser.add_argument('--pswd', required=True)
    args = parser.parse_args()
    logger = logging.getLogger(__name__)

    try:
        logger.debug('call parameters {} , {}'.format(args.login, args.pswd))
        sprint_data = SprintDefinitionRequest(args.login, args.pswd).result
        # ToDo: store to mongo temp db/collections
        with open('./data/jira-sprint.json', 'w') as out_file:
            json.dump(sprint_data, out_file, ensure_ascii=False)
        logger.info('file: {} {} items'.format(out_file.name, sprint_data))
        backlog_data = SprintBacklogRequest(args.login, args.pswd).result
        # ToDo: store to mongo temp db/collections
        with open('./data/jira-backlog.json', 'w') as out_file:
            json.dump(backlog_data, out_file, ensure_ascii=False)
        logger.info('file: {} {:d} items'.format(out_file.name, len(backlog_data.keys())))
    except Exception as e:
        logging.error(e, exc_info=True)