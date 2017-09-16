import json
from cfg import jira_cfg
from request import Request, Field


class SprintBacklogRequest(Request):
    def __init__(self, login, pswd):
        with open(jira_cfg[__class__.__name__]) as cfg_file:
            Request.__init__(self, json.load(cfg_file, strict=False), login, pswd, is_multipage=True)

    def _parse_response(self, response, out_data):
        backlog = []
        Field.parse_field(response, self._response_cfg[self._content_root], backlog)
        for issue in backlog:
            out_data.update({issue[Field.FIELD_KEY]:issue})
            self._logger.debug('issue: {}'.format(issue))
        return out_data

