from cfg import jira_cfg
from request import Request, Field
import json


class SprintDefinitionRequest(Request):
    def __init__(self, login, pswd):
        with open(jira_cfg[__class__.__name__]) as cfg_file:
            Request.__init__(self, json.load(cfg_file, strict=False), login, pswd, is_multipage=False)

    def _parse_response(self, response, out_data):
        Field.parse_field(response, self._response_cfg, out_data)
        self._logger.debug('{}'.format(out_data))
        return out_data
