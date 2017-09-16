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

@app.route('/sprint-backlog', methods=['GET', 'POST'])
#@cache.cached(timeout=60)
def backlog():
    return Response(response=dumps(db[DbConstants.SCRUM_SPRINT_BACKLOG].find({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")

@app.route('/backlog-details', methods=['GET', 'POST'])
#@cache.cached(timeout=60)
def backlog_item_details():
    item_key = request.args.get(DbConstants.ITEM_KEY)
    return Response(response=dumps(
        db[DbConstants.SCRUM_BACKLOG_DETAILS].find_one({DbConstants.ITEM_KEY: item_key}, {'_id': False})),
                    status=200,
                    mimetype="application/json")

@app.route('/subtasks', methods=['GET', 'POST'])
#@cache.cached(timeout=60)
def subtasks():
    parent_key = request.args.get(DbConstants.ITEM_PARENT)
    return Response(
        response=dumps(db[DbConstants.SCRUM_SUBTASKS].find({DbConstants.ITEM_PARENT: parent_key}, {'_id': False})),
        status=200,
        mimetype="application/json")

@app.route('/sprint', methods=['GET', 'POST'])
#@cache.cached(timeout=60)
def sprint():
    return Response(response=dumps(db[DbConstants.SCRUM_SPRINT].find_one({}, {'_id': False})),
                    status=200,
                    mimetype="application/json")
