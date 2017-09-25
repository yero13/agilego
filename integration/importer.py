from integration.integrator import Integrator
from integration.request import ImportRequest


class Importer(Integrator):
    __CFG_KEY_REQUEST_DEST = 'dest'

    def _process_request(self, request_id, request_type, request_cfg):
        request_dest = self._cfg[Integrator._CFG_KEY_REQUESTS][request_id][Importer.__CFG_KEY_REQUEST_DEST]
        self._db[request_dest].drop()
        result = ImportRequest.factory(request_cfg, self._login, self._pswd, request_type, self._mappings).result
        self._logger.debug(result)
        if isinstance(result, dict):
            res = self._db[request_dest].insert_one(result)
            self._logger.info('collection: {} data {} is saved'.format(request_dest, result))
        elif isinstance(result, list):
            self._db[request_dest].insert_many([item for item in result])
            self._logger.info('collection: {} {:d} items are saved'.format(request_dest, len(result)))
        else:
            raise NotImplementedError('{} - request is not supported'.format(request_type))
