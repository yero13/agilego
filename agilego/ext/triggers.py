from db.data import Trigger


class OnDeleteGroupTrigger(Trigger):
    def execute(self, input_object, match_params):
        self._logger.info('Trigger is executing {}'.format(__class__.__name__))
