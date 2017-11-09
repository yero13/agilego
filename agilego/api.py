from services.entities import Sprint, Backlog, SprintTimeline, ComponentList, GroupList, EmployeeList, Group, \
    AssignmentList, SubtaskList, TaskDetails, Assignment, SubtaskDetails
from flask_restful import Api
from flask import Flask
from flask_cors import CORS
from services.constants import RestConstants

app = Flask(__name__)
api = Api(app)
CORS(app)

api.add_resource(Sprint, RestConstants.ROUTE_SPRINT)
api.add_resource(Backlog, RestConstants.ROUTE_SPRINT_BACKLOG)
api.add_resource(SprintTimeline, RestConstants.ROUTE_SPRINT_TIMELINE)
api.add_resource(ComponentList, RestConstants.ROUTE_COMPONENTS)
api.add_resource(GroupList, RestConstants.ROUTE_TEAM)
api.add_resource(EmployeeList, RestConstants.ROUTE_EMPLOYEES)
api.add_resource(Group, RestConstants.ROUTE_GROUP, '{}/<group_id>'.format(RestConstants.ROUTE_GROUP))
api.add_resource(AssignmentList, RestConstants.ROUTE_ASSIGNMENTS)
api.add_resource(SubtaskList, '{}/<parent_id>{}'.format(RestConstants.ROUTE_TASK, RestConstants.ROUTE_SUBTASKS))
api.add_resource(TaskDetails, '{}/<task_id>'.format(RestConstants.ROUTE_TASK))
api.add_resource(Assignment, RestConstants.ROUTE_ASSIGNMENT, '{}/<assignment_id>'.format(RestConstants.ROUTE_ASSIGNMENT))
api.add_resource(SubtaskDetails, '{}/<subtask_id>'.format(RestConstants.ROUTE_SUBTASK))

