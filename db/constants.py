#ToDo: collection name wrapping should be moved to dest field in cfg file
class DbConstants:
    #Destination and collection prefix should be moved to cfg files
    SPRINT_COLLECTION_PREFIX = 'sprint'
    BACKLOG = 'backlog'
    BACKLOG_DETAILS = 'backlog-details'
    SUBTASKS = 'subtasks'
    SUBTASKS_DETAILS = 'substasks-details'
    SPRINT = 'definition'
    ITEM_KEY = 'key'
    ITEM_PARENT = 'parent'

    @staticmethod
    def wrap_db(collection):
        return '{}.{}'.format(DbConstants.SPRINT_COLLECTION_PREFIX, collection)
