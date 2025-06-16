from loguru import logger
import os
import sys
import contextvars
from datetime import datetime

# 日志目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# trace_id 上下文变量池
trace_ids = {
    "janus": contextvars.ContextVar("janus_trace_id", default="-"),
    "jervis": contextvars.ContextVar("jervis_trace_id", default="-"),
    "javelin": contextvars.ContextVar("javelin_trace_id", default="-"),
}

# ✅ 控制台 sink，带 trace_id，仅输出 WARNING 及以上
def safe_sink(msg):
    record = msg.record
    module_name = record["extra"].get("name", "unknown")
    trace_id = trace_ids.get(module_name, contextvars.ContextVar("unknown", default="-")).get()
    log_line = (
        f"{record['time'].strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} "
        f"[{record['level'].name}] {record['name']} [{trace_id}]: {record['message']}\n"
    )
    print(log_line, end="", file=sys.stderr if record["level"].no >= 30 else sys.stdout)

def file_sink_factory(module_prefix):
    def sink(msg):
        record = msg.record
        if record["extra"].get("name") != module_prefix:
            return
        trace_id = trace_ids.get(module_prefix, contextvars.ContextVar("unknown", default="-")).get()
        log_line = (
            f"{record['time'].strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} "
            f"[{record['level'].name}] {record['extra'].get('display', record['name'])} [{trace_id}]: {record['message']}\n"
        )
        log_file = os.path.join(LOG_DIR, f"{module_prefix.capitalize()}.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_line)
    return sink

# ✅ 清除默认 sink，避免污染
logger.remove()

# ✅ 控制台仅 WARNING 以上，带 trace_id
logger.add(safe_sink, level="INFO")

# ✅ 各模块写入文件（不带 trace_id）
logger.add(file_sink_factory("janus"), level="DEBUG")
logger.add(file_sink_factory("jervis"), level="DEBUG")
logger.add(file_sink_factory("javelin"), level="DEBUG")


from glob import glob

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

def find_logs_by_trace_id(trace_id: str):
    """
    根据 trace_id 搜索所有日志文件中包含该 trace_id 的日志行
    :param trace_id: 如 "JERVIS-xxxx" 或 "JANUS-abc123"
    :return: List[str] 匹配的日志行
    """
    result_lines = []
    for logfile in glob(os.path.join(LOG_DIR, "*.log")):
        with open(logfile, encoding="utf-8") as f:
            for line in f:
                if f"[{trace_id}]" in line:
                    result_lines.append(line.strip())
    return result_lines

if __name__ == "__main__":
    logs = find_logs_by_trace_id(trace_id=input("Input the trace id for debug: "))
    for line in logs:
        print(line)