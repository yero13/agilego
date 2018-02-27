from logic.gannt import GanntGraph
import logging.config
import json

CFG_LOG_GRAPH = './cfg/log/graph-logging-config.json'

if __name__ == '__main__':
    with open(CFG_LOG_GRAPH) as logging_cfg_file:
        logging.config.dictConfig(json.load(logging_cfg_file, strict=False))
        logger = logging.getLogger(__name__)
    try:
        logger.info('Init graph builder')
        g = GanntGraph()
        logger.debug('----> {}'.format(g.toString()))
    except Exception as e:
        logging.error(e, exc_info=True)


