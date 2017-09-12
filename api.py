from flask import Flask
from flask import Response
#import json
from bson.json_util import dumps
from db.connect import db
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

app.config['MONGO_DBNAME'] = 'agilego'
app.config['MONGO_HOST'] = '127.0.0.1'
app.config['MONGO_PORT'] = 27017
app.config['MONGO_USER'] = 'agilego'
app.config['MONGO_PASSWORD'] = '1'

class Issue1():
    def __init__(self):
        self.key = 'AGILEGO-1'
        self.priority = 'Highest'
        self.type = 'Story'

    def output(self):
        return {
            'key': self.key,
            'priority': self.priority,
            'type': self.type
        }

@app.route('/backlog', methods=['GET', 'POST'])
def backlog():
    d = db['backlog'].find()
    print('d'.format(d))
    #d = json.dumps(Issue1().find())
    resp = Response(response=dumps(d),
                    status=200,
                    mimetype="application/json")
    return resp
