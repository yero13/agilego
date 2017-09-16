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



    #Destination and collection prefix should be moved to cfg files
    """
    SPRINT_COLLECTION_PREFIX = 'sprint'
    BACKLOG = 'backlog'
    BACKLOG_DETAILS = 'backlog-details'
    SUBTASKS = 'subtasks'
    SUBTASKS_DETAILS = 'substasks-details'
    SPRINT = 'definition'
    """
    # ToDo: move to API constants?
    ITEM_KEY = 'key'
    ITEM_PARENT = 'parent'

    @staticmethod
    def wrap_db(collection):
        return '{}.{}'.format('sprint', collection)
