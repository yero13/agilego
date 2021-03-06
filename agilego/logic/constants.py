class DbConstants:
    CFG_DB_SCRUM_API = 'db_scrum_api'
    SCRUM_SPRINT = 'sprint.definition'
    SCRUM_SPRINT_TIMELINE = 'sprint.timeline'
    SCRUM_SPRINT_BACKLOG = 'sprint.backlog'
    SCRUM_SPRINT_BACKLOG_PLAIN = 'sprint.backlog_plain'
    SCRUM_BACKLOG_LINKS = 'sprint.backlog_links'
    SCRUM_ALLOCATIONS = 'sprint.allocations'
    PROJECT_TEAM = 'project.team'
    PROJECT_EMPLOYEES = 'project.employees'
    PROJECT_COMPONENTS = 'project.components'
    GANTT_LINKS = 'baseline.gantt_links'
    GANTT_TASKS = 'baseline.gantt_tasks'
    ACTUAL_DATE = 'actual.status.date'
    ACTUAL_DISCREPENCIES = 'actual.issues.discrepencies'


class RestConstants:
    ROUTE_SPRINT = '/sprint'
    ROUTE_SPRINT_TIMELINE = '{}/timeline'.format(ROUTE_SPRINT)
    ROUTE_BACKLOG = '/backlog'
    ROUTE_TASK = '/task'
    ROUTE_ALLOCATION = '/allocation'
    ROUTE_COMPONENTS = '/components'
    ROUTE_TEAM = '/team'
    ROUTE_EMPLOYEES = '/employees'
    ROUTE_GROUP = '/group'
    ROUTE_ALLOCATIONS = '/allocations'
    ROUTE_ALLOCATION_VALIDATION = '{}/validate'.format(ROUTE_ALLOCATION)
    ROUTE_GANTT_TASKS = '/gantt/tasks'
    ROUTE_GANTT_LINKS = '/gantt/links'
    ROUTE_PLAN_VS_ACTUAL = '/plan-vs-actual'
    ROUTE_ACTUAL_DATE = '{}/date'.format(ROUTE_PLAN_VS_ACTUAL)
    ROUTE_ACTUAL_DISCREPENCIES = '{}/discrepencies'.format(ROUTE_PLAN_VS_ACTUAL)


class ParamConstants:
    PARAM_ITEM_KEY = 'key'
    PARAM_ITEM_PARENT = 'parent'
    PARAM_DATE = 'date'
    PARAM_GROUP = 'group'
    PARAM_EMPLOYEE = 'employee'
    PARAM_EMPLOYEES = 'employees'
    PARAM_EMPLOYEE_NAME = 'name'
    PARAM_COMPONENT = 'component'
    PARAM_TIMELINE = 'timeline'
    PARAM_WHRS = 'whrs'
    PARAM_CAPACITY = 'capacity'
    PARAM_TYPE = 'type'
    PARAM_SUBTASKS = 'subtasks'


class MatchConstants:
    TYPE_STORY = 'Story'
    TYPE_BUG = 'Bug'
