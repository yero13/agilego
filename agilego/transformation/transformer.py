import abc
import logging
from db.data import Accessor, AccessParams
from utils.object import obj_for_name


class Transformer():
    __CFG_KEY_TRANSFORMATION_SETS = 'transformation-sets'

    def __init__(self, cfg):
        self.__cfg = cfg
        self.__logger = logging.getLogger(__class__.__name__)

    def transform_data(self):
        for transform_set in self.__cfg[Transformer.__CFG_KEY_TRANSFORMATION_SETS]:
            self.__logger.info('Processing transformation set {}'.format(transform_set))
            TransformationSet(self.__cfg[Transformer.__CFG_KEY_TRANSFORMATION_SETS][transform_set]).perform()


class TransformationSet:
    __CFG_KEY_DB = 'db'
    __CFG_KEY_SRC_DB = 'src.db'
    __CFG_KEY_DEST_DB = 'dest.db'
    __CFG_KEY_TRANSFORMATIONS = 'transformations'

    # ToDo: define cached objects on this level(?)

    def __init__(self, cfg):
        self.__cfg = cfg
        self.__logger = logging.getLogger(__class__.__name__)
        self.__src_db = self.__cfg[TransformationSet.__CFG_KEY_DB][TransformationSet.__CFG_KEY_SRC_DB]
        self.__dest_db = self.__cfg[TransformationSet.__CFG_KEY_DB][TransformationSet.__CFG_KEY_DEST_DB]

    def perform(self):
        for transformation in self.__cfg[TransformationSet.__CFG_KEY_TRANSFORMATIONS]:
            self.__logger.info('Processing transformation {}'.format(transformation))
            Transformation.factory(self.__cfg[TransformationSet.__CFG_KEY_TRANSFORMATIONS][transformation],
                                   self.__src_db, self.__dest_db).perform(
                self.__cfg[TransformationSet.__CFG_KEY_TRANSFORMATIONS][transformation][
                    Transformation.CFG_KEY_TRANSFORMATION_CFG])


class Transformation:
    # ToDo: class should be refactored  - no logic should be in cfg - it should be in class, params are allowed in cfg
    # ToDo: should be replaced by load/cleanup/save/transform
    __CFG_KEY_TRANSFORMATION = 'transformation'
    #__CFG_KEY_FIELDS = 'fields'
    #__CFG_KEY_SRC_COLLECTION = 'src.collection'
    #__CFG_KEY_DEST_COLLECTION = 'dest.collection'
    __CFG_KEY_TRANSFORMATION_CLASS = 'class'
    CFG_KEY_TRANSFORMATION_CFG = 'cfg'
    __CFG_KEY_LOAD = 'src.db.load'
    _CFG_KEY_LOAD_SRC = 'src'
    __CFG_KEY_TRANSFORM = 'transform'
    __CFG_KEY_CLEANUP = 'dest.db.cleanup'
    _CFG_KEY_CLEANUP_TARGET = 'target'
    __CFG_KEY_SAVE = 'dest.db.save'
    _CFG_KEY_SAVE_DEST = 'dest'

    @staticmethod
    def factory(cfg, src_db, dest_db):
        return obj_for_name(cfg[Transformation.__CFG_KEY_TRANSFORMATION_CLASS])(
            cfg[Transformation.CFG_KEY_TRANSFORMATION_CFG], src_db, dest_db)  # ToDo: wrap into try/catch

    def __init__(self, cfg, src_db, dest_db):
        self.__cfg = cfg
        self._logger = logging.getLogger(__class__.__name__)
        self._src_db = src_db
        self._dest_db = dest_db
        self._transformation = self.__cfg[
            Transformation.__CFG_KEY_TRANSFORMATION] if Transformation.__CFG_KEY_TRANSFORMATION in self.__cfg else None
        #self._fields = self.__cfg[Transformation.__CFG_KEY_FIELDS] if Transformation.__CFG_KEY_FIELDS in self.__cfg else None

    @abc.abstractmethod
    def _cleanup(self, cfg):
        return NotImplemented

    @abc.abstractmethod
    def _load(self, cfg):
        return NotImplemented

    @abc.abstractmethod
    def _save(self, cfg):
        return NotImplemented

    @abc.abstractmethod
    def _transform(self, cfg):
        return NotImplemented

    def perform(self, cfg):
        # ToDo: put into try/catch
        self._load(cfg[Transformation.__CFG_KEY_LOAD])
        self._transform(cfg[Transformation.__CFG_KEY_TRANSFORM])
        self._cleanup(cfg[Transformation.__CFG_KEY_CLEANUP])
        self._save(cfg[Transformation.__CFG_KEY_SAVE])

'''
    @staticmethod
    def _filter_fields(obj, fields):
        return {k:v for k,v in obj.items() if k in fields}
'''


class ManyToOneTransformation(Transformation):
    _CFG_KEY_FUNC = 'func'
    _CFG_KEY_ARGS = 'args'

    def _load(self, cfg):
        self._src = Accessor.factory(self._src_db).get(
            {AccessParams.KEY_COLLECTION: cfg[Transformation._CFG_KEY_LOAD_SRC],
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI})

    def _transform(self, cfg):
        self._res = obj_for_name(cfg[ManyToOneTransformation._CFG_KEY_FUNC])(self._src, cfg[ManyToOneTransformation._CFG_KEY_ARGS])

    def _cleanup(self, cfg):
        Accessor.factory(self._dest_db).delete(
            {AccessParams.KEY_COLLECTION: cfg[Transformation._CFG_KEY_CLEANUP_TARGET],
             AccessParams.KEY_TYPE: AccessParams.TYPE_MULTI,
             AccessParams.KEY_MATCH_PARAMS: {}})

    def _save(self, cfg):
        Accessor.factory(self._dest_db).upsert(
            {AccessParams.KEY_COLLECTION: cfg[Transformation._CFG_KEY_SAVE_DEST],
             AccessParams.KEY_TYPE: AccessParams.TYPE_SINGLE,
             AccessParams.KEY_OBJECT: self._res})


def transformer(func):
    def transformer_wrapper(input, cfg):
        #logger = logging.getLogger(transformer_wrapper.__name__)
        #logger.debug('Performing {} with params {}'.format(func.__name__, cfg))
        return func(input, **cfg)
    return transformer_wrapper

@transformer
def singles2array(input, **kwargs):
    PARAM_FIELD = 'field'

    #logger = logging.getLogger(singles2array.__name__)
    res = []
    field = kwargs.get(PARAM_FIELD)
    for item in input:
        res.append(item[field])
    #logger.debug('{}'.format(res))
    return {field: res}
