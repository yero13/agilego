from flask import Flask
from flask import Response
#import json
from bson.json_util import dumps
from db.connect import MongoDb
from flask_cors import CORS
from scrum.sprint import Sprint


app = Flask(__name__)
CORS(app)
db = MongoDb().connection

@app.route('/backlog', methods=['GET', 'POST'])
def backlog():
    resp = Response(response=dumps(db[Sprint.BACKLOG].find()),
                    status=200,
                    mimetype="application/json")
    return resp

