import json
from datetime import datetime
import logging
import logging.config
from scrum.sprint import SprintBacklog
from jira.work import SprintBacklogRequest
import argparse
from db.connect import db

LOGGING_CONFIG = './cfg/logging-config.json'


if __name__ == '__main__':
    with open(LOGGING_CONFIG) as logging_cfg_file:
        logging.config.dictConfig(json.load(logging_cfg_file, strict=False))
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', choices=['extract', 'validate'], required=True)
    parser.add_argument('--login', required=False)
    parser.add_argument('--pswd', required=False)
    args = parser.parse_args()
    logger = logging.getLogger(__name__)

    try:
        if args.action == 'extract':
            logger.debug('call parameters {} , {}'.format(args.login, args.pswd))
            row_data = SprintBacklogRequest(args.login, args.pswd).result
            with open('./data/backlog-{}.json'.format(datetime.now().strftime('%Y-%m-%d-%H-%M-%S')), 'w') as out_file:
                json.dump(row_data, out_file, ensure_ascii=False)
            logger.info('file: {} {:d} items'.format(out_file.name, len(row_data.keys())))
        elif args.action == 'validate':
            with open('./data/jira-extract.json') as data_file:
                sprint_backlog = SprintBacklog.from_dict(json.load(data_file, strict=False))
                doc = sprint_backlog.backlog
                doc = json.loads(doc.T.to_json()).values()
                logger.debug('backlog:\n{}'.format(doc))
                res = db.backlog.insert_many(doc)
                logger.debug('result:\n{}'.format(res))
                with open('./data/backlog-out.json', 'w') as out_file:
                    json.dump(sprint_backlog.issues.to_json(), out_file, ensure_ascii=False)
    except Exception as e:
        logging.error(e, exc_info=True)
