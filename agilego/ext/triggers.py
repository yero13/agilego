from framework.db.data import Trigger, CRUD
from framework.utils.json import JSONUtils
from framework.utils.aggregator import Aggregator
from logic.constants import ParamConstants, DbConstants
from logic.gantt import Task


class OnDeleteGroupTrigger(Trigger):
    def execute(self, input_object, match_params):
        assignments = CRUD.read_multi(self._db, DbConstants.SCRUM_ASSIGNMENTS,
                                       {ParamConstants.PARAM_GROUP: match_params[ParamConstants.PARAM_GROUP]})
        items_set = set()
        for assignment in assignments:
            items_set.add(assignment[ParamConstants.PARAM_ITEM_KEY])
        CRUD.delete_multi(self._db, DbConstants.SCRUM_ASSIGNMENTS, match_params)
        # update gantt
        for item in items_set:
            CRUD.upsert_single(self._db, DbConstants.GANTT_TASKS, Task.create_task(item), {Task.TASK_ID: item})


class OnUpsertGroupTrigger(Trigger):
    def execute(self, input_object, match_params):
        exist_group = CRUD.read_single(self._db, self._collection, match_params)
        diff = JSONUtils.diff(exist_group, input_object)
        if ParamConstants.PARAM_GROUP in diff:
            CRUD.upsert_multi(self._db, DbConstants.SCRUM_ASSIGNMENTS,
                               {ParamConstants.PARAM_GROUP: input_object[ParamConstants.PARAM_GROUP]},
                               {ParamConstants.PARAM_GROUP: exist_group[ParamConstants.PARAM_GROUP]})
        if ParamConstants.PARAM_EMPLOYEES in diff:
            capacity = Aggregator.agg_single_func(input_object[ParamConstants.PARAM_EMPLOYEES],
                                                  ParamConstants.PARAM_CAPACITY, 'sum')
            input_object[ParamConstants.PARAM_CAPACITY] = int(capacity) if capacity else 0
        if ParamConstants.PARAM_EMPLOYEES in diff and JSONUtils.DIFF_DELETE in diff[ParamConstants.PARAM_EMPLOYEES]:
            for employee in diff[ParamConstants.PARAM_EMPLOYEES][JSONUtils.DIFF_DELETE]:
                # delete assignments
                assignments = CRUD.read_multi(self._db, DbConstants.SCRUM_ASSIGNMENTS,
                                               {ParamConstants.PARAM_GROUP: exist_group[ParamConstants.PARAM_GROUP],
                                                ParamConstants.PARAM_EMPLOYEE: employee[
                                                    ParamConstants.PARAM_EMPLOYEE_NAME]})
                items_set = set()
                for assignment in assignments:
                    items_set.add(assignment[ParamConstants.PARAM_ITEM_KEY])
                CRUD.delete_multi(self._db, DbConstants.SCRUM_ASSIGNMENTS,
                                  {ParamConstants.PARAM_GROUP: exist_group[ParamConstants.PARAM_GROUP],
                                   ParamConstants.PARAM_EMPLOYEE: employee[ParamConstants.PARAM_EMPLOYEE_NAME]})
                # update gantt
                for item in items_set:
                    CRUD.upsert_single(self._db, DbConstants.GANTT_TASKS, Task.create_task(item), {Task.TASK_ID: item})


class OnUpsertDeleteAssignment(Trigger):
    def execute(self, input_object, match_params):
        id = match_params[ParamConstants.PARAM_ITEM_KEY]
        CRUD.upsert_single(self._db, DbConstants.GANTT_TASKS, Task.create_task(id), {Task.TASK_ID: id})
