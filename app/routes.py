from flask import Blueprint, jsonify, request
from app.services.fetcher import get_exchange_rate
from app.services.storage import store_data
from config.settings import WEBSITE, CURRENCIES, get_engine
from app.models import History, Threshold
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger("api")
logger.info("✅ 初始化 API 路由")
main = Blueprint("main", __name__)
Session = sessionmaker(bind=get_engine())

@main.route("/", methods=["GET"])
def index():
    logger.info("访问了 / 根路径")
    return jsonify({
        "message": "🌐 欢迎使用Janus API 服务",
        "endpoints": {
            "/api/fetch": "POST - 手动抓取汇率数据",
            "/api/history": "GET - 查看历史记录",
            "/api/logs/latest": "GET - 查看最新日志",
            "/api/config": "GET/POST - 查看或更新监控配置"
        }
    })

@main.route("/api/fetch", methods=["POST"])
def api_fetch():
    logger.info("触发 /api/fetch 抓取汇率数据")
    try:
        data = get_exchange_rate(WEBSITE, CURRENCIES)
        store_data(data)
        return jsonify({"message": "抓取并存储成功", "data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route("/api/history", methods=["GET"])
def api_history():
    logger.info("访问了 /api/history 查看历史记录")
    session = Session()
    try:
        results = session.query(History).order_by(History.Date.desc()).limit(50).all()
        data = [
            {
                "Date": row.Date.strftime("%Y-%m-%d %H:%M:%S"),
                "Currency": row.Currency,
                "Rate": row.Rate,
                "Locals": row.Locals
            } for row in results
        ]
        return jsonify(data)
    finally:
        session.close()

@main.route("/api/logs/latest", methods=["GET"])
def api_logs_latest():
    logger.info("访问了 /api/logs/latest 查看最新日志")
    log_path = os.path.join(os.path.dirname(__file__), "..", "logs", "Janus.log")
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()[-50:]
        logger.info("读取最新50条日志")
        return jsonify({"log": "".join(lines)})
    except Exception as e:
        logger.error(f"读取日志文件失败: {e}")
        return jsonify({"error": str(e)}), 500

@main.route("/api/config", methods=["GET"])
def api_config_get():
    logger.info("访问了 /api/config 查看监控配置")
    session = Session()
    try:
        thresholds = session.query(Threshold).all()
        return jsonify([
            {"Currency": t.Currency, "Upper": t.Upper, "Lower": t.Lower}
            for t in thresholds
        ])
    finally:
        session.close()

@main.route("/api/config", methods=["POST"])
def api_config_post():
    logger.info("访问了 /api/config 更新监控配置")
    data = request.get_json()
    if not data or "Currency" not in data:
        logger.error("请求中缺少 Currency 字段")
        return jsonify({"error": "请求中缺少 Currency 字段"}), 400

    session = Session()
    try:
        t = session.query(Threshold).filter_by(Currency=data["Currency"]).first()
        if t:
            t.Upper = data.get("Upper", t.Upper)
            t.Lower = data.get("Lower", t.Lower)
        else:
            t = Threshold(
                Currency=data["Currency"],
                Upper=data.get("Upper"),
                Lower=data.get("Lower")
            )
            session.add(t)
        session.commit()
        logger.info(f"更新了 {t.Currency} 的监控配置: 上限 {t.Upper}, 下限 {t.Lower}")
        return jsonify({"message": "配置已更新", "Currency": t.Currency, "Upper": t.Upper, "Lower": t.Lower})
    except Exception as e:
        session.rollback()
        logger.error(f"更新监控配置失败: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
