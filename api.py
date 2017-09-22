from flask import Flask
from flask import Response
from flask import request
from flask_cache import Cache
from bson.json_util import dumps
import json
from db.connect import MongoDb
from flask_cors import CORS
from db.constants import DbConstants

app = Flask(__name__)
CORS(app)
#cache = Cache(app)
db = MongoDb(DbConstants.CFG_DB_SCRUM).connection

@app.route('/sprint-backlog', methods=['GET'])
#@cache.cached(timeout=60)
def get_backlog():
    return Response(response=dumps(db[DbConstants.SCRUM_SPRINT_BACKLOG].find({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")

@app.route('/backlog-details', methods=['GET'])
#@cache.cached(timeout=60)
def get_backlog_item_details():
    item_key = request.args.get(DbConstants.ISSUE_KEY)
    return Response(response=dumps(
        db[DbConstants.SCRUM_BACKLOG_DETAILS].find_one({DbConstants.ISSUE_KEY: item_key}, {'_id': False})),
        status=200,
        mimetype="application/json")

@app.route('/subtasks', methods=['GET'])
#@cache.cached(timeout=60)
def get_subtasks():
    parent_key = request.args.get(DbConstants.ISSUE_PARENT)
    return Response(
        response=dumps(db[DbConstants.SCRUM_SUBTASKS].find({DbConstants.ISSUE_PARENT: parent_key}, {'_id': False})),
        status=200,
        mimetype="application/json")

@app.route('/subtask-details', methods=['GET'])
#@cache.cached(timeout=60)
def get_subtask_details():
    issue_key = request.args.get(DbConstants.ISSUE_KEY)
    return Response(
        response=dumps(db[DbConstants.SCRUM_SUBTASKS_DETAILS].find_one({DbConstants.ISSUE_KEY: issue_key}, {'_id': False})),
        status=200,
        mimetype="application/json")

@app.route('/sprint', methods=['GET'])
#@cache.cached(timeout=60)
def get_sprint():
    return Response(response=dumps(db[DbConstants.SCRUM_SPRINT].find_one({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")

@app.route('/sprint-timeline', methods=['GET'])
#@cache.cached(timeout=60)
def get_sprint_timeline():
    # ToDo: move to constants/separated collection and create constant for timeline
    return Response(response=dumps(db[DbConstants.SCRUM_SPRINT].find_one({}, {'timeline': True, '_id': False})),
                    status=200,
                    mimetype="application/json")

@app.route('/team', methods=['GET'])
#@cache.cached(timeout=60)
def get_team():
    # ToDo: move to constants/separated collection
    return Response(response=dumps(db[DbConstants.SCRUM_ORG_TEAM].find({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")

@app.route('/assignments', methods=['GET'])
#@cache.cached(timeout=60)
def get_assignments():
    return Response(response=dumps(db[DbConstants.SCRUM_ASSIGNMENTS].find({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")

@app.route('/assignment', methods=['GET'])
#@cache.cached(timeout=60)
def get_assignment():
    issue_key = request.args.get(DbConstants.ISSUE_KEY)
    assignment_date = request.args.get(DbConstants.ASSIGNMENT_DATE)
    assignment_group = request.args.get(DbConstants.ASSIGNMENT_GROUP)
    assignment_employee = request.args.get(DbConstants.ASSIGNMENT_EMPLOYEE)
    return Response(
        response=dumps(db[DbConstants.SCRUM_ASSIGNMENTS].find_one(
            {DbConstants.ISSUE_KEY: issue_key, DbConstants.ASSIGNMENT_DATE: assignment_date,
             DbConstants.ASSIGNMENT_GROUP: assignment_group, DbConstants.ASSIGNMENT_EMPLOYEE: assignment_employee},
            {'_id': False})),
        status=200,
        mimetype="application/json")

@app.route('/assign', methods=['POST'])
def assign():
    #ToDo: assign validation/warnings
    # ToDo: update estimates
    assignment = json.loads(request.data)
    return Response(response=dumps({(db[DbConstants.SCRUM_ASSIGNMENTS].update_one(
        {DbConstants.ISSUE_KEY: assignment[DbConstants.ISSUE_KEY],
         DbConstants.ASSIGNMENT_DATE: assignment[DbConstants.ASSIGNMENT_DATE],
         DbConstants.ASSIGNMENT_GROUP: assignment[DbConstants.ASSIGNMENT_GROUP],
         DbConstants.ASSIGNMENT_EMPLOYEE: assignment[DbConstants.ASSIGNMENT_EMPLOYEE]}, {"$set": assignment},
        upsert=True)).upserted_id}),
                    status=200,
                    mimetype="application/json")

@app.route('/assignment-remove', methods=['POST'])
def remove_assignment():
    # ToDo: update estimates
    assignment = json.loads(request.data)
    return Response(response=dumps({(db[DbConstants.SCRUM_ASSIGNMENTS].delete_one(
        {DbConstants.ISSUE_KEY: assignment[DbConstants.ISSUE_KEY],
         DbConstants.ASSIGNMENT_DATE: assignment[DbConstants.ASSIGNMENT_DATE],
         DbConstants.ASSIGNMENT_GROUP: assignment[DbConstants.ASSIGNMENT_GROUP],
         DbConstants.ASSIGNMENT_EMPLOYEE: assignment[DbConstants.ASSIGNMENT_EMPLOYEE]})).deleted_count}),
                    status=200,
                    mimetype="application/json")
