from db.constants import DbConstants

teams = [
	{
		"group": "BA",
		"components": ["BA"],
		"resources": ["fbyero"]
	},
	{
		"group": "FE",
		"components": ["FE", "HTML"],
		"resources": ["Karl.Munchhausen"]
	},
	{
		"group": "BE",
		"components": ["BE", "INT"],
		"resources": ["yero13"]
	},
	{
		"group": "QA",
		"components": [],
		"resources": []
	}
]


# ToDo: implement loading from JIRA and editing page in Agilego.ts
class Team():
    def __init__(self):
        return

    def to_db(self, db):
        db[DbConstants.SCRUM_ORG_TEAM].remove()  # ToDo: move to clean-up
        db[DbConstants.SCRUM_ORG_TEAM].insert_many(teams)