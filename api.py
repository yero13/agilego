from flask import Flask
from flask import Response
from flask import request
from flask_cache import Cache
from bson.json_util import dumps
from db.connect import MongoDb
from flask_cors import CORS
from db.constants import DbConstants


app = Flask(__name__)
CORS(app)
#cache = Cache(app)
db = MongoDb(DbConstants.CFG_DB_SCRUM).connection

# ToDo: generate dinamically based on cfg

@app.route('/sprint-backlog', methods=['GET', 'POST'])
#@cache.cached(timeout=60)
def get_backlog():
    return Response(response=dumps(db[DbConstants.SCRUM_SPRINT_BACKLOG].find({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")

@app.route('/backlog-details', methods=['GET', 'POST'])
#@cache.cached(timeout=60)
def get_backlog_item_details():
    item_key = request.args.get(DbConstants.ITEM_KEY)
    return Response(response=dumps(
        db[DbConstants.SCRUM_BACKLOG_DETAILS].find_one({DbConstants.ITEM_KEY: item_key}, {'_id': False})),
                    status=200,
                    mimetype="application/json")

@app.route('/subtasks', methods=['GET', 'POST'])
#@cache.cached(timeout=60)
def get_subtasks():
    parent_key = request.args.get(DbConstants.ITEM_PARENT)
    return Response(
        response=dumps(db[DbConstants.SCRUM_SUBTASKS].find({DbConstants.ITEM_PARENT: parent_key}, {'_id': False})),
        status=200,
        mimetype="application/json")

@app.route('/subtask-details', methods=['GET', 'POST'])
#@cache.cached(timeout=60)
def get_subtask_details():
    item_key = request.args.get(DbConstants.ITEM_KEY)
    return Response(
        response=dumps(db[DbConstants.SCRUM_SUBTASKS_DETAILS].find_one({DbConstants.ITEM_KEY: item_key}, {'_id': False})),
        status=200,
        mimetype="application/json")



@app.route('/sprint', methods=['GET', 'POST'])
#@cache.cached(timeout=60)
def get_sprint():
    return Response(response=dumps(db[DbConstants.SCRUM_SPRINT].find_one({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")

@app.route('/sprint-timeline', methods=['GET', 'POST'])
#@cache.cached(timeout=60)
def get_sprint_timeline():
    # ToDo: move to constants/separated collection and create constant for timeline
    timeline = db[DbConstants.SCRUM_SPRINT].find_one({}, {'timeline': True, '_id': False})['timeline']
    return Response(response=dumps(timeline),
                    status=200,
                    mimetype="application/json")

@app.route('/team', methods=['GET', 'POST'])
#@cache.cached(timeout=60)
def get_team():
    # ToDo: move to constants/separated collection
    return Response(response=dumps(db[DbConstants.SCRUM_ORG_TEAM].find({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")

@app.route('/assign-task', methods=['GET', 'POST'])
def set_task_assignment():
    #ToDo: assign task to someone (if allowed)
    return NotImplementedError