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
# cache = Cache(app)
db = MongoDb(ApiConstants.CFG_DB_SCRUM_API).connection


@app.route('/sprint-backlog', methods=['GET'])
# @cache.cached(timeout=60)
def get_backlog():
    return Response(response=dumps(db[ApiConstants.SCRUM_SPRINT_BACKLOG].find({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")


@app.route('/backlog-details', methods=['GET'])
# @cache.cached(timeout=60)
def get_backlog_item_details():
    item_key = request.args.get(ApiConstants.PARAM_ITEM_KEY)
    return Response(response=dumps(
        db[ApiConstants.SCRUM_BACKLOG_DETAILS].find_one({ApiConstants.PARAM_ITEM_KEY: item_key}, {'_id': False})),
        status=200,
        mimetype="application/json")


@app.route('/subtasks', methods=['GET'])
# @cache.cached(timeout=60)
def get_subtasks():
    parent_key = request.args.get(ApiConstants.PARAM_ITEM_PARENT)
    return Response(
        response=dumps(
            db[ApiConstants.SCRUM_SUBTASKS].find({ApiConstants.PARAM_ITEM_PARENT: parent_key}, {'_id': False})),
        status=200,
        mimetype="application/json")


@app.route('/subtask-details', methods=['GET'])
# @cache.cached(timeout=60)
def get_subtask_details():
    issue_key = request.args.get(ApiConstants.PARAM_ITEM_KEY)
    return Response(
        response=dumps(
            db[ApiConstants.SCRUM_SUBTASKS_DETAILS].find_one({ApiConstants.PARAM_ITEM_KEY: issue_key}, {'_id': False})),
        status=200,
        mimetype="application/json")


@app.route('/sprint', methods=['GET'])
# @cache.cached(timeout=60)
def get_sprint():
    return Response(response=dumps(db[ApiConstants.SCRUM_SPRINT].find_one({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")


@app.route('/sprint-timeline', methods=['GET'])
# @cache.cached(timeout=60)
def get_sprint_timeline():
    found = db[ApiConstants.SCRUM_SPRINT_TIMELINE].find_one({}, {'_id': False})
    return Response(response=dumps(found[ApiConstants.PARAM_TIMELINE] if ApiConstants.PARAM_TIMELINE in found else []),
                    status=200,
                    mimetype="application/json")


@app.route('/team', methods=['GET'])
# @cache.cached(timeout=60)
def get_team():
    return Response(response=dumps(db[ApiConstants.PROJECT_TEAM].find({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")


@app.route('/employees', methods=['GET'])
# @cache.cached(timeout=60)
def get_employees():
    return Response(response=dumps(db[ApiConstants.PROJECT_EMPLOYEES].find({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")


@app.route('/components', methods=['GET'])
# @cache.cached(timeout=60)
def get_components():
    found = db[ApiConstants.PROJECT_COMPONENTS].find_one({}, {'_id': False})
    return Response(response=dumps(found[ApiConstants.PARAM_COMPONENT] if ApiConstants.PARAM_COMPONENT in found else []),
                    status=200,
                    mimetype="application/json")


@app.route('/assignments', methods=['GET'])
# @cache.cached(timeout=60)
def get_assignments():
    return Response(response=dumps(db[ApiConstants.SCRUM_ASSIGNMENTS].find({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")


@app.route('/assignment', methods=['GET'])
# @cache.cached(timeout=60)
def get_assignment():
    return Response(
        response=dumps(db[ApiConstants.SCRUM_ASSIGNMENTS].find_one(request.args, {'_id': False})),
        status=200,
        mimetype="application/json")


# ToDo: below listed services should be reviewed as they should trigger validations and KPIs (velocity, etc) review


@app.route('/assign', methods=['POST'])
def assign():
    # ToDo: assign validation/warnings -> services
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


@app.route('/assignments-remove', methods=['POST'])
def remove_assignments():
    # ToDo: update estimates -> services
    params = json.loads(request.data)
    return Response(response=dumps({db[ApiConstants.SCRUM_ASSIGNMENTS].delete_many(params).deleted_count}),
                    status=204,
                    mimetype="application/json")


# ToDo: implement diff -u group_to_update vs existing group and trigger corresponding changes


@app.route('/group-remove', methods=['POST'])
def remove_group():
    # ToDo: remove group assignments + remove group
    group = json.loads(request.data)
    return Response(response=dumps({(db[ApiConstants.PROJECT_TEAM].delete_one(
        {ApiConstants.PARAM_GROUP: group[ApiConstants.PARAM_GROUP]})).deleted_count}), status=204,
                    mimetype="application/json")


@app.route('/group-update', methods=['POST'])
def update_group():
    # ToDo: update group assignments + remove group
    group = json.loads(request.data)
    return Response(response=dumps(
        {(db[ApiConstants.PROJECT_TEAM].update_one({ApiConstants.PARAM_GROUP: group[ApiConstants.PARAM_GROUP]},
                                                   {"$set": group}, upsert=True)).upserted_id}),
        status=204,
        mimetype="application/json")
