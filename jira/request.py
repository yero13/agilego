import logging
import abc
import requests
from requests.auth import HTTPBasicAuth
import json
import jsonschema
from jsonschema import validate
from datetime import datetime


class Field:
    FIELD_KEY = 'key'
    FIELD_EXT_ID = 'ext_id'
    FIELD_TYPE = 'type'
    FIELD_SUBITEMS = 'fields'
    FIELD_EXPLICIT = 'explicit'
    FIELD_OPTIONAL = 'optional'
    FIELD_MATCH = 'match'

    TYPE_ARRAY = 'array'
    TYPE_OBJECT = 'object'
    TYPE_STRING = 'string'
    TYPE_DATE = 'date'
    TYPE_DATETIME = 'datetime'
    TYPE_INT = 'int'
    TYPE_FLOAT = 'float'

    @staticmethod
    def is_complex_type(type):
        return type in [Field.TYPE_ARRAY, Field.TYPE_OBJECT]

    @staticmethod
    def get_casted_value(type, value):
        if not value:
            return value
        if type == Field.TYPE_STRING:
            return value
        elif type == Field.TYPE_DATE: # ToDo: set template for date
            return datetime.strptime(value, '%Y-%m-%d').date().isoformat()
        elif type == Field.TYPE_DATETIME: # ToDo: set template for datetime
            return datetime.strptime(value[0:10], '%Y-%m-%d').date().isoformat() # 2017-09-18T18:53:00.000Z
        elif type == Field.TYPE_INT:
            return int(value)
        elif type == Field.TYPE_FLOAT:
            return float(value)

    @staticmethod
    def is_match(pattern, field):
        if pattern is None:
            return True
        try:
            validate(field, pattern)
            return True
        except jsonschema.ValidationError:
            return False

    @staticmethod
    def _parse_field(data, field_cfg, target, is_optional=False):
        field_type = field_cfg[Field.FIELD_TYPE]
        field_key = field_cfg[Field.FIELD_KEY] if Field.FIELD_KEY in field_cfg else None
        field_ext_id = field_cfg[Field.FIELD_EXT_ID] if Field.FIELD_EXT_ID in field_cfg else field_key
        if field_type == Field.TYPE_ARRAY:
            target.update({field_ext_id: []})
            field_value = data[field_key]
            field_pattern = field_cfg[Field.FIELD_MATCH] if Field.FIELD_MATCH in field_cfg else None
            if Field.FIELD_SUBITEMS in field_cfg:
                subfield = next(iter(field_cfg[Field.FIELD_SUBITEMS].values()))  # only one field within array is allowed
                for item in field_value:
                    if Field.is_match(field_pattern, item):
                        Field._parse_field(item, subfield, target[field_ext_id])
            else:
                target[field_ext_id] = field_value
        elif field_type == Field.TYPE_OBJECT:
            is_explicit = field_cfg[Field.FIELD_EXPLICIT] if Field.FIELD_EXPLICIT in field_cfg else False
            is_optional = field_cfg[Field.FIELD_OPTIONAL] if Field.FIELD_OPTIONAL in field_cfg else False
            if field_key:
                try:
                    field_value = data[field_key]
                except KeyError:
                    if is_optional:
                        field_value = None
                    else:
                        raise
            else: # noname object
                field_value = data  # working with the same item
            if is_explicit:
                obj_exp = {}
                if isinstance(target, dict):  # add to object
                    target.update({field_ext_id: obj_exp})
                else:  # add to array
                    target.append(obj_exp)
            for subfield in field_cfg[Field.FIELD_SUBITEMS]:
                Field._parse_field(field_value, field_cfg[Field.FIELD_SUBITEMS][subfield],
                                  obj_exp if is_explicit else target, is_optional)
        else:  # other types
            try:
                field_value = data[field_key]
            except TypeError:
                if is_optional:
                    field_value = None
                else:
                    raise
            casted_value = Field.get_casted_value(field_type, field_value)
            if isinstance(target, dict):  # add to object
                target.update({field_ext_id: casted_value})
            else:  # add to array
                target.append(casted_value)

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
        self._logger = logging.getLogger(__class__.__name__)
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
