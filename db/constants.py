class DbConstants:
    SPRINT_COLLECTION_PREFIX = 'sprint'
    BACKLOG = 'backlog'
    BACKLOG_DETAILS = 'backlog-details'
    SUBTASKS = 'subtasks'
    SUBTASKS_DETAILS = 'substasks-details'
    ITEM_KEY = 'key'
    ITEM_PARENT = 'parent'

    @staticmethod
    def wrap_db(collection):
        return '{}.{}'.format(DbConstants.SPRINT_COLLECTION_PREFIX, collection)
