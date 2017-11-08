from db.accessor import DataAccessor
from flask_restful import Resource, request
from services.constants import DbConstants, ParamConstants
from utils.env import get_env_params


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
    def delete(self, group_id):
        return ApiDataAccessor.get_instance().delete({DataAccessor.CFG_KEY_COLLECTION: DbConstants.PROJECT_TEAM,
                                                      DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_SINGLE,
                                                      DataAccessor.CFG_KEY_WHERE_PARAMS: {
                                                          ParamConstants.PARAM_GROUP: group_id}}), 204
    def post(self):
        group = request.get_json()
        return ApiDataAccessor.get_instance().upsert({DataAccessor.CFG_KEY_COLLECTION: DbConstants.PROJECT_TEAM,
                                                      DataAccessor.CFG_KEY_TYPE: DataAccessor.CFG_TYPE_SINGLE,
                                                      DataAccessor.CFG_KEY_OBJECT: group,
                                                      DataAccessor.CFG_KEY_WHERE_PARAMS: {
                                                          ParamConstants.PARAM_GROUP: group[ParamConstants.PARAM_GROUP]}}), 201

'''
@app.route('/group-update', methods=['POST'])
def update_group():
    # ToDo: update group assignments + remove group
    group = json.loads(request.data)
    return Response(response=dumps(
        {(db[ApiConstants.PROJECT_TEAM].update_one({ApiConstants.PARAM_GROUP: group[ApiConstants.PARAM_GROUP]},
                                                   {"$set": group}, upsert=True)).upserted_id}),
        status=204,
        mimetype="application/json")
'''

