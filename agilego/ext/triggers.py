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
        if ParamConstants.PARAM_EMPLOYEES in diff and JSONUtils.DIFF_DELETE in diff[ParamConstants.PARAM_EMPLOYEES]:
            for employee in diff[ParamConstants.PARAM_EMPLOYEES][JSONUtils.DIFF_DELETE]:
                CRUD.delete_multi(self._db, DbConstants.SCRUM_ASSIGNMENTS,
                                  {ParamConstants.PARAM_GROUP: exist_group[ParamConstants.PARAM_GROUP],
                                   ParamConstants.PARAM_EMPLOYEE: employee[ParamConstants.PARAM_EMPLOYEE_NAME]})


class OnUpsertDeleteAssignment(Trigger):
    def execute(self, input_object, match_params):
        id = match_params[ParamConstants.PARAM_ITEM_KEY]
        task = Task.create_task(id)
        CRUD.upsert_single(self._db, DbConstants.GANTT_TASKS, task, {Task.TASK_ID: id})

