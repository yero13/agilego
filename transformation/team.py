from services.constants import ApiConstants

teams = [
	{
		"group": "BA",
		"components": ["BA"],
		"employees": ["fbyero", "yero13"]
	},
	{
		"group": "FE",
		"components": ["FE", "HTML"],
		"employees": ["Karl.Munchhausen"]
	},
	{
		"group": "BE",
		"components": ["BE", "INT"],
		"employees": ["yero13"]
	},
	{
		"group": "QA",
		"components": [],
		"employees": []
	}
]


# ToDo: implement loading from JIRA and editing page in Agilego.ts
class Team():
    def __init__(self):
        return

    def to_db(self, db):
        db[ApiConstants.SCRUM_ORG_TEAM].remove()  # ToDo: move to clean-up
        db[ApiConstants.SCRUM_ORG_TEAM].insert_many(teams)
