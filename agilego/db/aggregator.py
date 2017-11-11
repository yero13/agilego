from db.accessor import DataAccessor


class DataAggregator(DataAccessor):
    def __aggregate(self, collection, group_field, group_function, aggregate_field, match_params=None):
        try:
            pipe = [
                {'$match': match_params},
                #{'$set': {'{}'.format(aggregate_field): ParseInt()}}
                {'$group': {'_id': '${}'.format(group_field),
                            'aggregate': {'${}'.format(group_function): '${}'.format(aggregate_field)}}}
                #{'$group': {'_id': '${}'.format(group_field), 'aggregate': {'${}'.format(group_function): '${}'.format(aggregate_field)}}}
            ]
            self._logger.debug('pipe {}'.format(pipe))
            return list(self._db[collection].aggregate(pipeline=pipe)) #['result']
        except Exception as e:
            self._logger.error(e, exc_info=True)
            raise e


    def sum(self, cfg):
        collection = cfg[DataAccessor.CFG_KEY_COLLECTION]
        match_params = cfg[DataAccessor.CFG_KEY_MATCH_PARAMS] if DataAccessor.CFG_KEY_MATCH_PARAMS in cfg else None
        aggregate_field = 'whrs'
        group_field = 'employee'

        res = self.__aggregate(collection, group_field, 'sum', aggregate_field, match_params)
        self._logger.debug('>a>g>g>r>e>g>a>t>e> {}'.format(res))