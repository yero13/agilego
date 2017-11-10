from services.entities import Sprint, Backlog, SprintTimeline, ComponentList, GroupList, EmployeeList, Group, \
    AssignmentList, SubtaskList, TaskDetails, Assignment, SubtaskDetails
from flask_restful import Api
from flask import Flask
from flask_cors import CORS
from services.constants import RestConstants
import json
import logging.config

CFG_LOG_API = './cfg/log/api-logging-config.json'

app = Flask(__name__)
with open(CFG_LOG_API) as log_cfg_file:
    logging.config.dictConfig(json.load(log_cfg_file, strict=False))

api = Api(app)
CORS(app)

api.add_resource(Sprint, RestConstants.ROUTE_SPRINT)
api.add_resource(SprintTimeline, RestConstants.ROUTE_SPRINT_TIMELINE)
api.add_resource(Backlog, RestConstants.ROUTE_BACKLOG)
api.add_resource(TaskDetails, '{}/<task_key>'.format(RestConstants.ROUTE_TASK))
api.add_resource(SubtaskList, '{}/<task_key>{}'.format(RestConstants.ROUTE_TASK, RestConstants.ROUTE_SUBTASKS))
api.add_resource(SubtaskDetails, '{}/<subtask_key>'.format(RestConstants.ROUTE_SUBTASK))
api.add_resource(ComponentList, RestConstants.ROUTE_COMPONENTS)
api.add_resource(GroupList, RestConstants.ROUTE_TEAM)
api.add_resource(EmployeeList, RestConstants.ROUTE_EMPLOYEES)
api.add_resource(Group, RestConstants.ROUTE_GROUP, '{}/<group>'.format(RestConstants.ROUTE_GROUP))
api.add_resource(AssignmentList, RestConstants.ROUTE_ASSIGNMENTS)
api.add_resource(Assignment, RestConstants.ROUTE_ASSIGNMENT, '{}/<key>,<date>,<group>,<employee>'.format(RestConstants.ROUTE_ASSIGNMENT), '{}/<assignment_id>'.format(RestConstants.ROUTE_ASSIGNMENT))

