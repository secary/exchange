import logging.config
import os

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)  # 自动创建 logs 目录

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard"
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filename": os.path.join(LOG_DIR, "Janus.log"),
            "encoding": "utf-8"
        },
        "auto_file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filename": os.path.join(LOG_DIR, "auto.log"),
            "encoding": "utf-8"
        },
        "api_file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filename": os.path.join(LOG_DIR, "api.log"),
            "encoding": "utf-8"
        },
        "services_file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "filename": os.path.join(LOG_DIR, "services.log"),
            "encoding": "utf-8"
        },
        "error_file": {
            "class": "logging.FileHandler",
            "level": "ERROR",
            "formatter": "standard",
            "filename": os.path.join(LOG_DIR, "error.log"),
            "encoding": "utf-8"
        }
    },
    
    "loggers": {
        "app": {
            "handlers": ["console", "file", "error_file"],
            "level": "INFO",
            "propagate": False
        },
        "auto": {
            "handlers": ["console", "auto_file"],
            "level": "INFO",
            "propagate": False
        },
        "api": {
            "handlers": ["api_file", "error_file"],
            "level": "INFO",
            "propagate": False
        },
        "error": {
            "handlers": ["error_file"],
            "level": "ERROR",
            "propagate": False
        },
        "app.services": {
            "handlers": ["services_file", "error_file"],
            "level": "DEBUG",
            "propagate": True
        },
        "matplotlib.font_manager": {
            "handlers": [],
            "level": "ERROR",
            "propagate": False
        }
    },

    "root": {
        "handlers": ["console", "file", "error_file"],
        "level": "DEBUG"
    }
}
