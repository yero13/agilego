from db.accessor import DataAccessor
from flask_restful import Resource, request
from services.constants import DbConstants, ParamConstants
from utils.env import get_env_params
from bson.objectid import ObjectId


class ApiDataAccessor(DataAccessor):
    @staticmethod
    def get_instance():
        return DataAccessor(get_env_params()[DbConstants.CFG_DB_SCRUM_API])


class Backlog(Resource):
    def get(self):
        return ApiDataAccessor.get_instance().get({DataAccessor.CFG_KEY_COLLECTION: DbConstants.SCRUM_SPRINT_BACKLOG,
                       DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_MULTI})


class Sprint(Resource):
    def get(self):
        return ApiDataAccessor.get_instance().get({DataAccessor.CFG_KEY_COLLECTION: DbConstants.SCRUM_SPRINT,
                       DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_SINGLE})


class SprintTimeline(Resource):
    def get(self):
        found = ApiDataAccessor.get_instance().get({DataAccessor.CFG_KEY_COLLECTION: DbConstants.SCRUM_SPRINT_TIMELINE,
                       DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_SINGLE})
        return ([] if (not found or not ParamConstants.PARAM_TIMELINE in found) else found[ParamConstants.PARAM_TIMELINE])


class ComponentList(Resource):
    def get(self):
        found = ApiDataAccessor.get_instance().get({DataAccessor.CFG_KEY_COLLECTION: DbConstants.PROJECT_COMPONENTS,
                       DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_SINGLE})
        return ([] if (not found or not ParamConstants.PARAM_COMPONENT in found) else found[ParamConstants.PARAM_COMPONENT])


class GroupList(Resource):
    def get(self):
        return ApiDataAccessor.get_instance().get({DataAccessor.CFG_KEY_COLLECTION: DbConstants.PROJECT_TEAM,
                       DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_MULTI})


class EmployeeList(Resource):
    def get(self):
        return ApiDataAccessor.get_instance().get({DataAccessor.CFG_KEY_COLLECTION: DbConstants.PROJECT_EMPLOYEES,
                       DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_MULTI})


class Group(Resource):
    def delete(self, group):
        # ToDo: move dependencies cleanup to separated class
        accessor = ApiDataAccessor.get_instance()
        accessor.delete({DataAccessor.CFG_KEY_COLLECTION: DbConstants.SCRUM_ASSIGNMENTS,
                         DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_MULTI,
                         DataAccessor.CFG_KEY_WHERE_PARAMS: {
                             ParamConstants.PARAM_GROUP: group}})
        return accessor.delete({DataAccessor.CFG_KEY_COLLECTION: DbConstants.PROJECT_TEAM,
                                DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_SINGLE,
                                DataAccessor.CFG_KEY_WHERE_PARAMS: {
                                                          ParamConstants.PARAM_GROUP: group}}), 204

    # ToDo: implement diff -u group_to_update vs existing group and trigger corresponding changes
    # ToDo: remove assignments if delete employee
    def post(self):
        group = request.get_json()
        return ApiDataAccessor.get_instance().upsert({DataAccessor.CFG_KEY_COLLECTION: DbConstants.PROJECT_TEAM,
                                                      DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_SINGLE,
                                                      DataAccessor.CFG_KEY_OBJECT: group,
                                                      DataAccessor.CFG_KEY_WHERE_PARAMS: {
                                                          ParamConstants.PARAM_GROUP: group[ParamConstants.PARAM_GROUP]}}), 201

class AssignmentList(Resource):
    def get(self):
        return ApiDataAccessor.get_instance().get({DataAccessor.CFG_KEY_COLLECTION: DbConstants.SCRUM_ASSIGNMENTS,
                       DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_MULTI})


class SubtaskList(Resource):
    def get(self, task_key):
        return ApiDataAccessor.get_instance().get({DataAccessor.CFG_KEY_COLLECTION: DbConstants.SCRUM_SUBTASKS,
                                                   DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_MULTI,
                                                   DataAccessor.CFG_KEY_WHERE_PARAMS: {
                                                       ParamConstants.PARAM_ITEM_PARENT: task_key}})


class TaskDetails(Resource):
    def get(self, task_key):
        return ApiDataAccessor.get_instance().get({DataAccessor.CFG_KEY_COLLECTION: DbConstants.SCRUM_BACKLOG_DETAILS,
                                                   DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_SINGLE,
                                                   DataAccessor.CFG_KEY_WHERE_PARAMS: {
                                                       ParamConstants.PARAM_ITEM_KEY: task_key}})


class SubtaskDetails(Resource):
    def get(self, subtask_key):
        return ApiDataAccessor.get_instance().get({DataAccessor.CFG_KEY_COLLECTION: DbConstants.SCRUM_SUBTASKS_DETAILS,
                                                   DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_SINGLE,
                                                   DataAccessor.CFG_KEY_WHERE_PARAMS: {
                                                       ParamConstants.PARAM_ITEM_KEY: subtask_key}})

# ToDo: group/assignments services should be reviewed as they should trigger validations and KPIs (velocity, etc) review

class Assignment(Resource):
    def get(self, key, date, group, employee):
        return ApiDataAccessor.get_instance().get({DataAccessor.CFG_KEY_COLLECTION: DbConstants.SCRUM_ASSIGNMENTS,
                                                   DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_SINGLE,
                                                   DataAccessor.CFG_KEY_WHERE_PARAMS: {
                                                       ParamConstants.PARAM_ITEM_KEY: key,
                                                       ParamConstants.PARAM_DATE: date,
                                                       ParamConstants.PARAM_GROUP: group,
                                                       ParamConstants.PARAM_EMPLOYEE: employee}})

    def post(self):
        assignment_details = request.get_json()
        return ApiDataAccessor.get_instance().upsert({DataAccessor.CFG_KEY_COLLECTION: DbConstants.SCRUM_ASSIGNMENTS,
                                                      DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_SINGLE,
                                                      DataAccessor.CFG_KEY_OBJECT: assignment_details,
                                                      DataAccessor.CFG_KEY_WHERE_PARAMS: {
                                                          ParamConstants.PARAM_ITEM_KEY: assignment_details[ParamConstants.PARAM_ITEM_KEY],
                                                          ParamConstants.PARAM_DATE: assignment_details[ParamConstants.PARAM_DATE],
                                                          ParamConstants.PARAM_GROUP: assignment_details[ParamConstants.PARAM_GROUP],
                                                          ParamConstants.PARAM_EMPLOYEE: assignment_details[ParamConstants.PARAM_EMPLOYEE]}}), 201

    def delete(self, assignment_id):
        return ApiDataAccessor.get_instance().delete({DataAccessor.CFG_KEY_COLLECTION: DbConstants.SCRUM_ASSIGNMENTS,
                                                      DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_SINGLE,
                                                      DataAccessor.CFG_KEY_WHERE_PARAMS: {
                                                          '_id': ObjectId(assignment_id)}}), 204
