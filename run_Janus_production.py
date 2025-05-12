import logging
from app import create_app
from waitress import serve
from config.logger_config import LOGGING_CONFIG

# 初始化日志
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

logger.info("✅ 正在初始化 Flask 应用...")

app = create_app()

logger.info("✅ Flask 应用初始化完成，启动 waitress 服务")

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)
