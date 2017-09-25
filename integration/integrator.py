import logging
from db.connect import MongoDb
import abc


class Integrator():
    _CFG_KEY_DB = 'db'
    _CFG_KEY_REQUESTS = 'requests'
    _CFG_KEY_REQUEST_CFG_FILE = 'cfg'
    _CFG_KEY_REQUEST_TYPE = 'type'
    _CFG_KEY_MAPPING = 'mapping'

    def __init__(self, cfg, login, pswd):
        self._cfg = cfg
        self._login = login
        self._pswd = pswd
        self._logger = logging.getLogger(__class__.__name__)
        self._db = MongoDb(cfg[Integrator._CFG_KEY_DB]).connection
        self._mappings = self._cfg[
            Integrator._CFG_KEY_MAPPING] if Integrator._CFG_KEY_MAPPING in self._cfg else None

    def perform(self):
        for request in self._cfg[Integrator._CFG_KEY_REQUESTS]:
            request_type = self._cfg[Integrator._CFG_KEY_REQUESTS][request][Integrator._CFG_KEY_REQUEST_TYPE]
            request_cfg = self._cfg[Integrator._CFG_KEY_REQUESTS][request][Integrator._CFG_KEY_REQUEST_CFG_FILE]
            self._process_request(request, request_type, request_cfg)

    @abc.abstractmethod
    def _process_request(self, request_id, request_type, request_cfg):
        return NotImplemented
