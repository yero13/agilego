import json

from bson.json_util import dumps
from flask import Flask
from flask import Response
from flask import request
from flask_cors import CORS

from services.constants import ApiConstants
from db.connect import MongoDb

app = Flask(__name__)
CORS(app)
#cache = Cache(app)
db = MongoDb(ApiConstants.CFG_DB_SCRUM_API).connection


@app.route('/sprint-backlog', methods=['GET'])
#@cache.cached(timeout=60)
def get_backlog():
    return Response(response=dumps(db[ApiConstants.SCRUM_SPRINT_BACKLOG].find({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")


@app.route('/backlog-details', methods=['GET'])
#@cache.cached(timeout=60)
def get_backlog_item_details():
    item_key = request.args.get(ApiConstants.PARAM_ITEM_KEY)
    return Response(response=dumps(
        db[ApiConstants.SCRUM_BACKLOG_DETAILS].find_one({ApiConstants.PARAM_ITEM_KEY: item_key}, {'_id': False})),
        status=200,
        mimetype="application/json")


@app.route('/subtasks', methods=['GET'])
#@cache.cached(timeout=60)
def get_subtasks():
    parent_key = request.args.get(ApiConstants.PARAM_ITEM_PARENT)
    return Response(
        response=dumps(db[ApiConstants.SCRUM_SUBTASKS].find({ApiConstants.PARAM_ITEM_PARENT: parent_key}, {'_id': False})),
        status=200,
        mimetype="application/json")


@app.route('/subtask-details', methods=['GET'])
#@cache.cached(timeout=60)
def get_subtask_details():
    issue_key = request.args.get(ApiConstants.PARAM_ITEM_KEY)
    return Response(
        response=dumps(db[ApiConstants.SCRUM_SUBTASKS_DETAILS].find_one({ApiConstants.PARAM_ITEM_KEY: issue_key}, {'_id': False})),
        status=200,
        mimetype="application/json")


@app.route('/sprint', methods=['GET'])
#@cache.cached(timeout=60)
def get_sprint():
    return Response(response=dumps(db[ApiConstants.SCRUM_SPRINT].find_one({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")


@app.route('/sprint-timeline', methods=['GET'])
#@cache.cached(timeout=60)
def get_sprint_timeline():
    # ToDo: move to constants/separated collection and create constant for timeline
    return Response(response=dumps(db[ApiConstants.SCRUM_SPRINT_TIMELINE].find_one({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")


@app.route('/team', methods=['GET'])
#@cache.cached(timeout=60)
def get_team():
    return Response(response=dumps(db[ApiConstants.PROJECT_TEAM].find({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")


@app.route('/employees', methods=['GET'])
#@cache.cached(timeout=60)
def get_employees():
    return Response(response=dumps(db[ApiConstants.PROJECT_EMPLOYEES].find({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")

@app.route('/components', methods=['GET'])
#@cache.cached(timeout=60)
def get_components():
    return Response(response=dumps(db[ApiConstants.PROJECT_COMPONENTS].find({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")


@app.route('/assignments', methods=['GET'])
#@cache.cached(timeout=60)
def get_assignments():
    return Response(response=dumps(db[ApiConstants.SCRUM_ASSIGNMENTS].find({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")


@app.route('/assignment', methods=['GET'])
#@cache.cached(timeout=60)
def get_assignment():
    issue_key = request.args.get(ApiConstants.PARAM_ITEM_KEY)
    assignment_date = request.args.get(ApiConstants.PARAM_DATE)
    assignment_group = request.args.get(ApiConstants.PARAM_GROUP)
    assignment_employee = request.args.get(ApiConstants.PARAM_EMPLOYEE)
    return Response(
        response=dumps(db[ApiConstants.SCRUM_ASSIGNMENTS].find_one(
            {ApiConstants.PARAM_ITEM_KEY: issue_key, ApiConstants.PARAM_DATE: assignment_date,
             ApiConstants.PARAM_GROUP: assignment_group, ApiConstants.PARAM_EMPLOYEE: assignment_employee},
            {'_id': False})),
        status=200,
        mimetype="application/json")


@app.route('/assign', methods=['POST'])
def assign():
    #ToDo: assign validation/warnings -> services
    # ToDo: update estimates -> services
    assignment = json.loads(request.data)
    return Response(response=dumps({(db[ApiConstants.SCRUM_ASSIGNMENTS].update_one(
        {ApiConstants.PARAM_ITEM_KEY: assignment[ApiConstants.PARAM_ITEM_KEY],
         ApiConstants.PARAM_DATE: assignment[ApiConstants.PARAM_DATE],
         ApiConstants.PARAM_GROUP: assignment[ApiConstants.PARAM_GROUP],
         ApiConstants.PARAM_EMPLOYEE: assignment[ApiConstants.PARAM_EMPLOYEE]}, {"$set": assignment},
        upsert=True)).upserted_id}),
                    status=204,
                    mimetype="application/json")


@app.route('/assignment-remove', methods=['POST'])
def remove_assignment():
    # ToDo: update estimates -> services
    assignment = json.loads(request.data)
    return Response(response=dumps({(db[ApiConstants.SCRUM_ASSIGNMENTS].delete_one(
        {ApiConstants.PARAM_ITEM_KEY: assignment[ApiConstants.PARAM_ITEM_KEY],
         ApiConstants.PARAM_DATE: assignment[ApiConstants.PARAM_DATE],
         ApiConstants.PARAM_GROUP: assignment[ApiConstants.PARAM_GROUP],
         ApiConstants.PARAM_EMPLOYEE: assignment[ApiConstants.PARAM_EMPLOYEE]})).deleted_count}),
                    status=204,
                    mimetype="application/json")


@app.route('/group-remove', methods=['POST'])
def remove_group():
    # ToDo: remove group assignments + remove group
    return


@app.route('/group-upsert', methods=['POST'])
def upsert_group():
    # ToDo: update group assignments + remove group
    return


