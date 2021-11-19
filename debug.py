"""
debug.py
Usage:
```
from debug import get_logger
log = get_logger("default")
```
"""

__version__ = "2021.07.23"

import os
import sys
import traceback
import logging
import logging.config
import yaml
from flask import Response, jsonify, render_template
import functools

basedir = os.path.dirname(os.path.realpath(__file__))
global loggers
loggers = {}

logging_set_up = False

logs_dir = os.path.join(basedir, 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)


def setup_logging(
        default_path=os.path.join(basedir, 'config', 'logger.yaml'),
        default_level=logging.INFO,
        env_key='LOG_CFG',
        logname=None
):
    """
    Setup logging configuration
    """
    caller = sys._getframe(1).f_globals.get('__name__')
    if caller != "debug":
        print("DEBUG.PY - setup_logging - WARNING - Deprecated use of debug.py by {}".format(caller))

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())

        for handler, data in config['handlers'].items():
            if 'filename' in data:
                logpath = os.path.join(logs_dir, config['handlers'][handler]['filename'])
                print(
                    "DEBUG.PY - setup_logging - Setting up logger '{}' requested by ({}), filepath is set to: {}; ".format(
                        handler,
                        caller,
                        logpath))
                config['handlers'][handler]['filename'] = logpath

        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def get_logger(name):
    caller = sys._getframe(1).f_globals.get('__name__')
    global loggers
    if loggers.get(name):
        print("DEBUG.PY - get_logger - ({}) requested logger '{}', using existing logger.".format(caller, name))
        return loggers.get(name)
    else:
        print("DEBUG.PY - get_logger - ({}) requested logger '{}', setting up new logger. ({})".format(caller, name,
                                                                                                       list(
                                                                                                           loggers.keys())))
        logger = logging.getLogger(name)
        loggers[name] = logger
        return logger


log = get_logger("default")


def catch_errors(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            log.error(f"Error in function {f.__name__}: {str(e)}", exc_info=True)
            return None

    return wrapped


def catch_errors_json(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": str(e), "traceback": traceback.format_exc()})

    return wrapped


def catch_errors_html(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            return render_template("error.html", error=str(e), details=traceback.format_exc())

    return wrapped


if not logging_set_up:
    setup_logging()
