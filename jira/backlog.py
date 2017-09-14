import json
from .request import Request, Field


class SprintBacklogRequest(Request):
    # ToDo: move to cfg constants
    __CFG_SPRINT_BACKLOG_REQUEST = './cfg/jira-sprint-backlog-request.json'
    __KEY_BACKLOG_ITEMS = 'issues'

    def __init__(self, login, pswd):
        with open(SprintBacklogRequest.__CFG_SPRINT_BACKLOG_REQUEST) as cfg_file:
            Request.__init__(self, json.load(cfg_file, strict=False), login, pswd, is_multipage=True)

    def _parse_response(self, response, out_data):
        backlog = {}
        Field._parse_field(response, self._response_cfg[SprintBacklogRequest.__KEY_BACKLOG_ITEMS], backlog)
        for issue in backlog[SprintBacklogRequest.__KEY_BACKLOG_ITEMS]:
            out_data.update({issue[Field.FIELD_KEY]:issue})
            self._logger.debug('issue: {}'.format(issue))
        return out_data

