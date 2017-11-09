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
    # ToDo: remove assignments
    def delete(self, group_id):
        return ApiDataAccessor.get_instance().delete({DataAccessor.CFG_KEY_COLLECTION: DbConstants.PROJECT_TEAM,
                                                      DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_SINGLE,
                                                      DataAccessor.CFG_KEY_WHERE_PARAMS: {
                                                          ParamConstants.PARAM_GROUP: group_id}}), 204

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
    def get(self, parent_id):
        return ApiDataAccessor.get_instance().get({DataAccessor.CFG_KEY_COLLECTION: DbConstants.SCRUM_SUBTASKS,
                                                   DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_MULTI,
                                                   DataAccessor.CFG_KEY_WHERE_PARAMS: {
                                                       ParamConstants.PARAM_ITEM_PARENT: parent_id}})


class TaskDetails(Resource):
    def get(self, task_id):
        return ApiDataAccessor.get_instance().get({DataAccessor.CFG_KEY_COLLECTION: DbConstants.SCRUM_BACKLOG_DETAILS,
                                                   DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_SINGLE,
                                                   DataAccessor.CFG_KEY_WHERE_PARAMS: {
                                                       ParamConstants.PARAM_ITEM_KEY: task_id}})


class SubtaskDetails(Resource):
    def get(self, subtask_id):
        return ApiDataAccessor.get_instance().get({DataAccessor.CFG_KEY_COLLECTION: DbConstants.SCRUM_SUBTASKS_DETAILS,
                                                   DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_SINGLE,
                                                   DataAccessor.CFG_KEY_WHERE_PARAMS: {
                                                       ParamConstants.PARAM_ITEM_KEY: subtask_id}})

# ToDo: group/assignments services should be reviewed as they should trigger validations and KPIs (velocity, etc) review


class Assignment(Resource):
    '''

    @app.route('/assignment', methods=['GET'])
    # @cache.cached(timeout=60)
    def get_assignment():
        return Response(
            response=dumps(db[ApiConstants.SCRUM_ASSIGNMENTS].find_one(request.args, {'_id': False})),
            status=200,
            mimetype="application/json")
    '''

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
