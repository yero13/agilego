class DbConstants:
    CFG_DB_SCRUM_API = 'db_scrum_api'
    SCRUM_SPRINT = 'sprint.definition'
    SCRUM_SPRINT_TIMELINE = 'sprint.timeline'
    SCRUM_SPRINT_BACKLOG = 'sprint.backlog'
    SCRUM_ASSIGNMENTS = 'sprint.assignments'
    PROJECT_TEAM = 'project.team'
    PROJECT_EMPLOYEES = 'project.employees'
    PROJECT_COMPONENTS = 'project.components'


class RestConstants:
    ROUTE_SPRINT = '/sprint'
    ROUTE_SPRINT_TIMELINE = '{}/timeline'.format(ROUTE_SPRINT)
    ROUTE_BACKLOG = '/backlog'
    ROUTE_TASK = '/task'
    ROUTE_SUBTASKS = '/subtasks'
    ROUTE_SUBTASK = '/subtask'
    ROUTE_ASSIGNMENT = '/assignment'
    ROUTE_COMPONENTS = '/components'
    ROUTE_TEAM = '/team'
    ROUTE_EMPLOYEES = '/employees'
    ROUTE_GROUP = '/group'
    ROUTE_ASSIGNMENTS = '/assignments'
    ROUTE_ASSIGNMENT_VALIDATION = '{}/validate'.format(ROUTE_ASSIGNMENT)


class ParamConstants:
    PARAM_ITEM_KEY = 'key'
    PARAM_ITEM_PARENT = 'parent'
    PARAM_DATE = 'date'
    PARAM_GROUP = 'group'
    PARAM_EMPLOYEE = 'employee'
    PARAM_COMPONENT = 'component'
    PARAM_TIMELINE = 'timeline'
    PARAM_WHRS = 'whrs'
    PARAM_TYPE = 'type'


class MatchConstants:
    TYPE_STORY = 'Story'
    TYPE_BUG = 'Bug'