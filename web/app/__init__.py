import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import uuid
from loguru import logger
from flask import Flask, request, g
from app.routes import main
from config.logger_config import trace_ids  # ✅ 自定义日志配置和 trace_id 存储

# 初始化日志配置
logger = logger.bind(name="javelin")

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main)

    @app.before_request
    def log_request_info():
        trace_id = request.headers.get("X-Trace-ID") or f"JAVELIN-{uuid.uuid4()}"
        g.trace_id = trace_id
        trace_ids["javelin"].set(trace_id)

        logger.bind(trace_id=trace_id).info(f"🌐 收到请求: {request.method} {request.path} 来自 {request.remote_addr}")

    @app.after_request
    def log_response_info(response):
        trace_id = g.get("trace_id", "-")
        logger.bind(trace_id=trace_id).info(f"📤 响应状态: {response.status}")
        response.headers["X-Trace-ID"] = trace_id
        return response

    return app
