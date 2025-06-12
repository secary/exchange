import os
import logging
import contextvars

# 日志目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# trace_id 上下文变量池（默认都是 "-"）
trace_ids = {
    "janus": contextvars.ContextVar("janus_trace_id", default="-"),
    "jervis": contextvars.ContextVar("jervis_trace_id", default="-"),
    "javelin": contextvars.ContextVar("javelin_trace_id", default="-"),
}

# 注入 trace_id 的日志过滤器
class TraceIdFilter(logging.Filter):
    def __init__(self, module_name):
        self.module_name = module_name


    def filter(self, record):
        try:
            record.trace_id = trace_ids[self.module_name].get()
        except LookupError:
            record.trace_id = "-"
        return True


# 配置字典
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s [trace_id=%(trace_id)s]: %(message)s"
        }
    },

    "filters": {
        "janus_trace": {
            "()": TraceIdFilter,
            "module_name": "janus"
        },
        "jervis_trace": {
            "()": TraceIdFilter,
            "module_name": "jervis"
        },
        "javelin_trace": {
            "()": TraceIdFilter,
            "module_name": "javelin"
        },
        # fallback，用于控制台和未显式指定模块的 logger
        "default_trace": {
            "()": TraceIdFilter,
            "module_name": "janus"
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "default",
            "filters": ["default_trace"]  # ✅ 给控制台注入默认 trace_id
        },
        "janus_file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "Janus.log"),
            "level": "DEBUG",
            "formatter": "default",
            "filters": ["janus_trace"],
            "encoding": "utf-8"
        },
        "jervis_file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "Jervis.log"),
            "level": "DEBUG",
            "formatter": "default",
            "filters": ["jervis_trace"],
            "encoding": "utf-8"
        },
        "javelin_file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "Javelin.log"),
            "level": "DEBUG",
            "formatter": "default",
            "filters": ["javelin_trace"],
            "encoding": "utf-8"
        }
    },

    "loggers": {
        "janus": {
            "handlers": ["console", "janus_file"],
            "level": "DEBUG",
            "propagate": False
        },
        "jervis": {
            "handlers": ["console", "jervis_file"],
            "level": "DEBUG",
            "propagate": False
        },
        "javelin": {
            "handlers": ["console", "javelin_file"],
            "level": "DEBUG",
            "propagate": False
        }
    },

    "root": {
        "handlers": ["console"],
        "level": "WARNING"
    }
}
