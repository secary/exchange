import os
import uuid
from loguru import logger
from config.logger_config import trace_ids

trace_id = f"JAVELIN-{uuid.uuid4()}"
trace_ids["javelin"].set(trace_id)

# ✅ 绑定 loguru logger，写入 Javelin.log
logger = logger.bind(name="javelin")
logger.info("HMS Javelin、抜錨します.")

from app import create_app
# 创建 Flask 应用
app = create_app()

# ✅ 启动 Flask
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
