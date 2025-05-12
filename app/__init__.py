from flask import Flask, request
from app.routes import main
import logging

logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main)

    @app.before_request
    def log_request_info():
        logger.info(f"🌐 收到请求: {request.method} {request.path} 来自 {request.remote_addr}")

    @app.after_request
    def log_response_info(response):
        logger.info(f"📤 响应状态: {response.status}")
        return response

    return app
