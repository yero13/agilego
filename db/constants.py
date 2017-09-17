#ToDo: collection name wrapping should be moved to dest field in cfg file
class DbConstants:
    CFG_DB_JIRA = 'jira'
    JIRA_BACKLOG = 'backlog'
    JIRA_SPRINT = 'sprint'

    CFG_DB_SCRUM = 'scrum'
    SCRUM_SPRINT = 'sprint.definition'
    SCRUM_SPRINT_BACKLOG = 'sprint.backlog'
    SCRUM_BACKLOG_DETAILS = 'sprint.backlog-details'
    SCRUM_SUBTASKS = 'sprint.subtasks'
    SCRUM_SUBTASKS_DETAILS = 'sprint.subtasks-details'

    # ToDo: move to API constants?
    ITEM_KEY = 'key'
    ITEM_PARENT = 'parent'
