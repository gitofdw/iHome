# -*- coding:utf-8 -*-
from ihome import redis_store

from . import api
import logging


@api.route('/index')
def index():
    # redis_store.set("name", "itcast")
    logging.fatal("Fatal Message")
    logging.error("Error Message")
    logging.warn("Warn Message")
    logging.info("Info Message")
    logging.debug("Debug Message")
    return 'index'
