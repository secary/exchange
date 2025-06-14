from loguru import logger
import os
import sys
import contextvars
from datetime import datetime

# 日志目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# trace_id 上下文变量池（默认 "-"）
trace_ids = {
    "janus": contextvars.ContextVar("janus_trace_id", default="-"),
    "jervis": contextvars.ContextVar("jervis_trace_id", default="-"),
    "javelin": contextvars.ContextVar("javelin_trace_id", default="-"),
}

# ✅ 控制台 sink（完全自定义，防止颜色解析器触发 `<td>` 报错）
def safe_sink(msg):
    record = msg.record
    module_name = record["extra"].get("name", "unknown")
    trace_id = trace_ids.get(module_name, contextvars.ContextVar("unknown", default="-")).get()
    log_line = (
        f"{record['time'].strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} "
        f"[{record['level'].name}] {record['name']} [trace_id={trace_id}]: {record['message']}\n"
    )
    print(log_line, end="", file=sys.stderr if record["level"].no >= 30 else sys.stdout)

# ✅ 文件 sink 工厂（根据绑定字段 name 精确写入）
def file_sink_factory(module_prefix):
    def sink(msg):
        record = msg.record
        if record["extra"].get("name") != module_prefix:
            return
        trace_id = trace_ids.get(module_prefix, contextvars.ContextVar("unknown", default="-")).get()
        log_line = (
            f"{record['time'].strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} "
            f"[{record['level'].name}] {record['name']} [trace_id={trace_id}]: {record['message']}\n"
        )
        log_file = os.path.join(LOG_DIR, f"{module_prefix.capitalize()}.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_line)
    return sink

# ✅ 移除默认 handler，避免污染
logger.remove()

# ✅ 添加自定义控制台 sink
logger.add(safe_sink, level="WARNING")

# ✅ 为每个模块添加文件 sink
logger.add(file_sink_factory("janus"), level="DEBUG")
logger.add(file_sink_factory("jervis"), level="DEBUG")
logger.add(file_sink_factory("javelin"), level="DEBUG")
