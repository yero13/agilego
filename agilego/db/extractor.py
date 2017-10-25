from db.connect import MongoDb

'''
{
	"board": {
		"type": "single",
		"collection": "test.board"
	}
}
'''

class Extractor:
    __CFG_KEY_TYPE = 'type'
    __CFG_KEY_TYPE_SINGLE = 'single'
    __CFG_KEY_TYPE_MULTI = 'multi'
    __CFG_KEY_COLLECTION = 'collection'
    __CFG_KEY_SEARCH_PARAMS = 'where'

    def __init__(self, db):
        self.__db = MongoDb(db).connection

    def __get_single(self, collection, search_params=None):
        return self.__db[collection].find_one(search_params if search_params else {}, {'_id': False})

    def __get_multi(self, collection, search_params=None):
        return self.__db[collection].find(search_params if search_params else {}, {'_id': False})

    def get(self, cfg):
        collection = cfg[Extractor.__CFG_KEY_COLLECTION]
        search_params = cfg[Extractor.__CFG_KEY_SEARCH_PARAMS] if Extractor.__CFG_KEY_SEARCH_PARAMS in cfg else None

        if cfg[Extractor.__CFG_KEY_TYPE] == Extractor.__CFG_KEY_TYPE_SINGLE:
            self.__get_single(collection, search_params)
        elif cfg[Extractor.__CFG_KEY_TYPE] == Extractor.__CFG_KEY_TYPE_MULTI:
            self.__get_multi(collection, search_params)
