import json
import logging
import logging.config
from scrum.sprint import Wbs
from jira.sprint import SprintDefinitionRequest
from jira.backlog import SprintBacklogRequest
import argparse
from db.connect import MongoDb

LOGGING_CONFIG = './cfg/logging-config.json'


if __name__ == '__main__':
    with open(LOGGING_CONFIG) as logging_cfg_file:
        logging.config.dictConfig(json.load(logging_cfg_file, strict=False))
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', choices=['extract', 'validate', 'transform'], required=True)
    parser.add_argument('--login', required=False)
    parser.add_argument('--pswd', required=False)
    args = parser.parse_args()
    logger = logging.getLogger(__name__)

    try:
        if args.action == 'extract':
            logger.debug('call parameters {} , {}'.format(args.login, args.pswd))
            sprint_data = SprintDefinitionRequest(args.login, args.pswd).result
            with open('./data/jira-sprint.json', 'w') as out_file:
                json.dump(sprint_data, out_file, ensure_ascii=False)
            logger.info('file: {} {} items'.format(out_file.name, sprint_data))
            backlog_data = SprintBacklogRequest(args.login, args.pswd).result
            with open('./data/jira-backlog.json', 'w') as out_file:
                json.dump(backlog_data, out_file, ensure_ascii=False)
            logger.info('file: {} {:d} items'.format(out_file.name, len(backlog_data.keys())))
        elif args.action == 'transform':
            with open('./data/jira-backlog.json') as data_file:
                Wbs.from_dict(json.load(data_file, strict=False)).to_db(MongoDb().connection)
    except Exception as e:
        logging.error(e, exc_info=True)
