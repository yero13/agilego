from .request import Request
import json


class SprintDefinitionRequest(Request):
    # ToDo: move to CfgConstants
    __CFG_SPRINT_DEFINITION_REQUEST = './cfg/sprint-definition-request.json'

    def __init__(self, login, pswd):
        with open(SprintDefinitionRequest.__CFG_SPRINT_DEFINITION_REQUEST) as cfg_file:
            Request.__init__(self, json.load(cfg_file, strict=False), login, pswd, is_multipage=False)

    def _parse_response(self, response, out_data):
        self._logger.debug('+++{}'.format(response))