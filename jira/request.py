import logging
import abc
import requests
from requests.auth import HTTPBasicAuth
import json


class Request():
    """
    Requests data from Jira. Parses response data accordingly to given rules
    """

    __KEY_REQUEST = 'request'
    __KEY_REQUEST_URL = 'url'
    __KEY_REQUEST_DATA = 'data'

    __KEY_PARAM_TOTAL = 'total'
    __KEY_PARAM_START_AT = 'startAt'
    __KEY_PARAM_MAX_RESULTS = 'maxResults'

    _KEY_RESPONSE = 'response'

    def __init__(self, cfg, login, pswd, is_multipage=False):
        self._logger = logging.getLogger(__name__)
        self.__login = login
        self.__pswd = pswd
        self.__is_multipage = is_multipage
        self.__request_cfg = cfg[Request.__KEY_REQUEST]
        self._response_cfg = cfg[Request._KEY_RESPONSE]
        self.__response_values = {}
        self._logger.debug('\n{}'.format(self._response_cfg))
        self.__perform_multi_request() if self.__is_multipage else self.__perform_single_request()

    @property
    def result(self):
        return self.__response_values

    def __perform_single_request(self):
        # ToDo:
        return NotImplemented

    def __perform_multi_request(self):
        while True:
            request_url = self.__request_cfg[Request.__KEY_REQUEST_URL]
            request_data = self.__request_cfg[Request.__KEY_REQUEST_DATA]
            self._logger.info('request {} from {}'.format(request_data, request_url))
            response = requests.post(request_url,
                                     json.dumps(request_data),
                                     headers={"Content-Type": "application/json"},
                                     auth=HTTPBasicAuth(self.__login, self.__pswd),
                                     verify=True)
            if not response.ok:
                response.raise_for_status()
            response = json.loads(response.content, strict=False)
            self._parse_response(response, self.__response_values)
            total = int(response[Request.__KEY_PARAM_TOTAL])
            max_results = int(response[Request.__KEY_PARAM_MAX_RESULTS])
            start_at = int(response[Request.__KEY_PARAM_START_AT])
            start_at += max_results
            if start_at < total:
                request_data.update({Request.__KEY_PARAM_START_AT: start_at})
                continue
            break

    @abc.abstractmethod
    def _parse_response(self, response, out_data):
        """
        Parses response into out_data
        :param response: JSON response
        :param out_data: dictionary
        :return: out_data
        """
        return NotImplemented
