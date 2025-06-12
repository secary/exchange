import logging
import uuid
import logging.config  # ✅ 加载日志配置模块
from flask import Flask, request, g
from app.routes import main
from config.logger_config import LOGGING_CONFIG, trace_ids  # ✅ 自定义日志配置和 trace_id 存储

# 初始化日志配置
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("javelin")

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main)

    @app.before_request
    def log_request_info():
        # 获取或生成 trace_id
        trace_id = request.headers.get("X-Trace-ID") or f"JAVELIN-{uuid.uuid4()}"
        g.trace_id = trace_id
        trace_ids["javelin"].set(trace_id)  # 设置 context variable
        logger.info(f"🌐 收到请求: {request.method} {request.path} 来自 {request.remote_addr}")

    @app.after_request
    def log_response_info(response):
        logger.info(f"📤 响应状态: {response.status}")
        if hasattr(g, "trace_id"):
            response.headers["X-Trace-ID"] = g.trace_id
        return response

    return app
