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
db = MongoDb().connection

@app.route('/backlog', methods=['GET', 'POST'])
#@cache.cached(timeout=60)
def backlog():
    resp = Response(response=dumps(db[DbConstants.wrap_db(DbConstants.BACKLOG)].find()),
                    status=200,
                    mimetype="application/json")
    return resp

@app.route('/backlog-details', methods=['GET', 'POST'])
#@cache.cached(timeout=60)
def backlog_item_details():
    item_key = request.args.get(DbConstants.ITEM_KEY)
    resp = Response(response=dumps(db[DbConstants.wrap_db(DbConstants.BACKLOG_DETAILS)].find_one({DbConstants.ITEM_KEY: item_key})),
                    status=200,
                    mimetype="application/json")
    return resp

@app.route('/subtasks', methods=['GET', 'POST'])
#@cache.cached(timeout=60)
def subtasks():
    parent_key = request.args.get(DbConstants.ITEM_PARENT)
    resp = Response(response=dumps(db[DbConstants.wrap_db(DbConstants.SUBTASKS)].find({DbConstants.ITEM_PARENT: parent_key})),
                    status=200,
                    mimetype="application/json")
    return resp