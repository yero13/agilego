from services.constants import ApiConstants

teams = [
	{
		"group": "BA",
		"components": ["BA"],
		"employees": [{"name":"fbyero", "displayName": "roman.yepifanov"}, {"name":"yero13", "displayName": "Roman Yepifanov"}]
	},
	{
		"group": "FE",
		"components": ["FE", "HTML"],
		"employees": [{"name":"Karl.Munchhausen", "displayName": "Karl.Munchhausen.2012"}]
	},
	{
		"group": "BE",
		"components": ["BE", "INT"],
		"employees": [{"name":"yero13", "displayName": "Roman Yepifanov"}]
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
