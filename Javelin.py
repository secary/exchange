import logging
import uuid
import logging.config  # ✅ 加上这一行
from config.logger_config import LOGGING_CONFIG, trace_ids

# 设置 trace_id
trace_id = f"JAVELIN-{uuid.uuid4()}"
trace_ids["javelin"].set(trace_id)

# 配置日志
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("javelin")

logger.info("✅ 正在初始化 Flask 应用...")

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)