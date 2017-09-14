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
        response = self.__perform_request()
        self._parse_response(response, self.__response_values)

    def __perform_multi_request(self):
        while True:
            response = self.__perform_request()
            self._parse_response(response, self.__response_values)
            total = int(response[Request.__KEY_PARAM_TOTAL])
            max_results = int(response[Request.__KEY_PARAM_MAX_RESULTS])
            start_at = int(response[Request.__KEY_PARAM_START_AT])
            start_at += max_results
            if start_at < total:
                self.__request_cfg[Request.__KEY_REQUEST_DATA].update({Request.__KEY_PARAM_START_AT: start_at})
                continue
            break

    def __get_request_params(self):
        self.__request_url = self.__request_cfg[Request.__KEY_REQUEST_URL]
        self.__request_data = self.__request_cfg[
            Request.__KEY_REQUEST_DATA] if Request.__KEY_REQUEST_DATA in self.__request_cfg else None

    def __perform_request(self):
        request_url = self.__request_cfg[Request.__KEY_REQUEST_URL]
        request_data = self.__request_cfg[
            Request.__KEY_REQUEST_DATA] if Request.__KEY_REQUEST_DATA in self.__request_cfg else None
        self._logger.info('request {} from {}'.format(request_data, request_url))
        # ToDo: implement post/get methods
        response = requests.get(request_url,
                                request_data, # for post - json.dumps(self.__request_data),
                                headers={"Content-Type": "application/json"},
                                auth=HTTPBasicAuth(self.__login, self.__pswd),
                                verify=True)
        if not response.ok:
            response.raise_for_status()
        return json.loads(response.content, strict=False)

    @abc.abstractmethod
    def _parse_response(self, response, out_data):
        """
        Parses response into out_data
        :param response: JSON response
        :param out_data: dictionary
        :return: out_data
        """
        return NotImplemented
