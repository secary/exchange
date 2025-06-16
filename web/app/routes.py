import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import os
import uuid
from loguru import logger
from config.logger_config import trace_ids

# 设置 trace_id（适用于主进程或脚本执行）
trace_id = os.getenv("TRACE_ID_JAVELIN") or f"JAVELIN-{uuid.uuid4()}"
trace_ids["javelin"].set(trace_id)

# 绑定 loguru logger（确保日志输出至 Javelin.log）
logger = logger.bind(name="javelin")


from flask import Blueprint, jsonify, request, render_template
# from main.fetcher import get_exchange_rate
# from main.storage import store_data
from config.settings import WEBSITE, CURRENCIES, get_engine
from utils.models import History, Threshold, Prediction, AutomationSwitch
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, and_
from datetime import datetime, timedelta

main = Blueprint("main", __name__)
Session = sessionmaker(bind=get_engine())

@main.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# @main.route("/api/fetch", methods=["POST"])
# def api_fetch():
#     logger.info("触发 /api/fetch 抓取汇率数据")
#     try:
#         data = get_exchange_rate(WEBSITE, CURRENCIES)
#         store_data(data)
#         return jsonify({"message": "抓取并存储成功", "data": data})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
    
@main.route("/api/history", methods=["GET"])
def api_history():
    logger.info("访问了 /api/history 查看历史记录")
    session = Session()
    try:
        currency = request.args.get("currency")
        query = session.query(History)
        if currency:
            query = query.filter(History.Currency == currency)
        results = query.order_by(History.Date.desc()).limit(100).all()
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

# @main.route("/api/switch/status", methods=["GET"])
# def get_switch_status():
#     logger.info("访问了 /api/switch/status 获取当前自动化状态")
#     session = Session()
#     try:
#         switch = session.query(AutomationSwitch).filter_by(key="auto_enabled").first()
#         status_str = "开启" if (switch and switch.value) else "关闭"
#         return jsonify({"status": status_str})
#     finally:
#         session.close()


# @main.route("/api/switch/toggle", methods=["POST"])
# def toggle_switch():
#     logger.info("访问了 /api/switch/toggle 切换自动化状态")
#     session = Session()
#     try:
#         switch = session.query(AutomationSwitch).filter_by(key="auto_enabled").first()
#         if switch:
#             switch.value = not switch.value
#         else:
#             switch = AutomationSwitch(key="auto_enabled", value=True)
#             session.add(switch)
#         session.commit()
#         status_str = "开启" if switch.value else "关闭"
#         logger.info(f"✅ 自动化开关已设置为：{status_str}")
#         return jsonify({"status": status_str})
#     except Exception as e:
#         session.rollback()
#         logger.error(f"切换自动化开关失败: {e}")
#         return jsonify({"error": str(e)}), 500
#     finally:
#         session.close()

@main.route("/api/latest", methods=["GET"])
def get_latest_rates():
    logger.info("访问了 /api/latest 获取最新汇率")
    session = Session()
    try:
        # 1️⃣ 获取每种货币的最新一条历史记录
        row_number = func.row_number().over(
            partition_by=History.Currency,
            order_by=History.Date.desc()
        ).label("rnk")

        subquery = session.query(
            History.Date,
            History.Currency,
            History.Rate,
            row_number
        ).subquery()

        latest_history = session.query(subquery).filter(subquery.c.rnk == 1).all()

        response = []

        # 2️⃣ 为每个历史记录找到相邻预测记录
        for row in latest_history:
            predicted = session.query(Prediction).filter(
                and_(
                    Prediction.Currency == row.Currency,
                    Prediction.Date >= row.Date
                )
            ).order_by(Prediction.Date.asc()).first()

            response.append({
                "Date": row.Date.strftime("%Y-%m-%d %H:%M:%S"),
                "Currency": row.Currency,
                "Rate": row.Rate,
                "PredictedRate": predicted.Predicted_rate if predicted else None,
                "PredictionDate": predicted.Date.strftime("%Y-%m-%d %H:%M:%S") if predicted else None
            })

        return jsonify(response)

    finally:
        session.close()

@main.route("/api/history/chart", methods=["GET"])
def api_history_chart():
    logger.info("访问了 /api/history/chart 获取历史+预测数据")
    session = Session()
    try:
        now = datetime.now()
        since = now - timedelta(days=30)

        # 读取历史记录
        history_rows = session.query(History).filter(History.Date >= since).all()
        from sqlalchemy.sql import func

        # 获取每种货币的最早一条未来预测
        subq = (
            session.query(
                Prediction.Currency,
                func.min(Prediction.Date).label("min_date")
            )
            .filter(Prediction.Date >= datetime.now())
            .group_by(Prediction.Currency)
            .subquery()
        )

        prediction_rows = (
            session.query(Prediction)
            .join(subq, (Prediction.Currency == subq.c.Currency) & (Prediction.Date == subq.c.min_date))
            .all()
        )
        
        # 整理为 Currency -> datetime -> value
        from collections import defaultdict

        history_map = defaultdict(dict)
        for row in history_rows:
            timestamp = row.Date.replace(second=0, microsecond=0)
            history_map[row.Currency][timestamp] = row.Rate

        prediction_map = defaultdict(dict)
        for row in prediction_rows:
            timestamp = row.Date.replace(second=0, microsecond=0)
            prediction_map[row.Currency][timestamp] = row.Predicted_rate

        # 汇总所有时间点
        response = {}
        for currency in set(list(history_map.keys()) + list(prediction_map.keys())):
            all_times = sorted(set(history_map[currency].keys()) | set(prediction_map[currency].keys()))
            merged = []
            for dt in all_times:
                rate = history_map[currency].get(dt)
                predicted = None if rate is not None else prediction_map[currency].get(dt)
                merged.append({
                    "datetime": dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "rate": rate,
                    "predicted": predicted
                })
            response[currency] = merged

        return jsonify(response)

    finally:
        session.close()
        
@main.route("/history", methods=["GET"])
def history_page():
    return render_template("history.html")