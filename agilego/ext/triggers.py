from framework.db.data import Trigger, CRUD
from framework.utils.json import JSONUtils
from logic.constants import ParamConstants, DbConstants
from logic.gantt import Task


class OnDeleteGroupTrigger(Trigger):
    def execute(self, input_object, match_params):
        CRUD.delete_multi(self._db, DbConstants.SCRUM_ASSIGNMENTS, match_params)


class OnUpsertGroupTrigger(Trigger):
    def execute(self, input_object, match_params):
        exist_group = CRUD.read_single(self._db, self._collection, match_params)
        diff = JSONUtils.diff(exist_group, input_object)
        import logging
        logging.debug('----->{}'.format(diff))
        if ParamConstants.PARAM_GROUP in diff:
            CRUD.upsert_multi(self._db, DbConstants.SCRUM_ASSIGNMENTS,
                               {ParamConstants.PARAM_GROUP: input_object[ParamConstants.PARAM_GROUP]},
                               {ParamConstants.PARAM_GROUP: exist_group[ParamConstants.PARAM_GROUP]})
        if ParamConstants.PARAM_EMPLOYEES in diff and JSONUtils.DIFF_DELETE in diff[ParamConstants.PARAM_EMPLOYEES]:
            for employee in diff[ParamConstants.PARAM_EMPLOYEES][JSONUtils.DIFF_DELETE]:
                assignmennts = CRUD.read_multi(self._db, DbConstants.SCRUM_ASSIGNMENTS,
                                               {ParamConstants.PARAM_GROUP: exist_group[ParamConstants.PARAM_GROUP],
                                                ParamConstants.PARAM_EMPLOYEE: employee[
                                                    ParamConstants.PARAM_EMPLOYEE_NAME]})
                items_set = set()
                for assignment in assignmennts:
                    items_set.add(assignment[ParamConstants.PARAM_ITEM_KEY])
                CRUD.delete_multi(self._db, DbConstants.SCRUM_ASSIGNMENTS,
                                  {ParamConstants.PARAM_GROUP: exist_group[ParamConstants.PARAM_GROUP],
                                   ParamConstants.PARAM_EMPLOYEE: employee[ParamConstants.PARAM_EMPLOYEE_NAME]})
                # ToDo: update gantt
                # ToDo: update capacity


class OnUpsertDeleteAssignment(Trigger):
    def execute(self, input_object, match_params):
        id = match_params[ParamConstants.PARAM_ITEM_KEY]
        task = Task.create_task(id)
        CRUD.upsert_single(self._db, DbConstants.GANTT_TASKS, task, {Task.TASK_ID: id})

