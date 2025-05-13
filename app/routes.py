import os
import logging

logger = logging.getLogger("api")
logger.info("✅ 初始化 API 路由")
logger_auto = logging.getLogger("auto")

from flask import Blueprint, jsonify, request, render_template
from app.services.fetcher import get_exchange_rate
from app.services.storage import store_data
from config.settings import WEBSITE, CURRENCIES, get_engine
from app.models import History, Threshold
from sqlalchemy.orm import sessionmaker
from app.models import AutomationSwitch
from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlalchemy.sql import over
from sqlalchemy import Integer
from datetime import datetime, timedelta

main = Blueprint("main", __name__)
Session = sessionmaker(bind=get_engine())

@main.route("/", methods=["GET"])
def index():
    return render_template("index.html")

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

@main.route("/api/switch/status", methods=["GET"])
def get_switch_status():
    logger.info("访问了 /api/switch/status 获取当前自动化状态")
    session = Session()
    try:
        switch = session.query(AutomationSwitch).filter_by(key="auto_enabled").first()
        status_str = "开启" if (switch and switch.value) else "关闭"
        return jsonify({"status": status_str})
    finally:
        session.close()


@main.route("/api/switch/toggle", methods=["POST"])
def toggle_switch():
    logger.info("访问了 /api/switch/toggle 切换自动化状态")
    session = Session()
    try:
        switch = session.query(AutomationSwitch).filter_by(key="auto_enabled").first()
        if switch:
            switch.value = not switch.value
        else:
            switch = AutomationSwitch(key="auto_enabled", value=True)
            session.add(switch)
        session.commit()
        status_str = "开启" if switch.value else "关闭"
        logger.info(f"✅ 自动化开关已设置为：{status_str}")
        logger_auto.info(f"✅ 自动化开关已设置为：{status_str}")
        return jsonify({"status": status_str})
    except Exception as e:
        session.rollback()
        logger.error(f"切换自动化开关失败: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@main.route("/api/latest", methods=["GET"])
def get_latest_rates():
    logger.info("访问了 /api/latest 获取最新汇率")
    session = Session()
    try:
        # 定义 row_number 窗口函数分组排名
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

        # 只取每组的第一名（即每个货币最新记录）
        results = session.query(subquery).filter(subquery.c.rnk == 1).all()

        data = [
            {
                "Date": row.Date.strftime("%Y-%m-%d %H:%M:%S"),
                "Currency": row.Currency,
                "Rate": row.Rate
            }
            for row in results
        ]
        return jsonify(data)
    finally:
        session.close()

@main.route("/api/history/chart", methods=["GET"])
def api_history_chart():
    logger.info("访问了 /api/history/chart 获取历史数据")
    session = Session()
    try:
        since = datetime.now() - timedelta(days=30)
        records = (
            session.query(History)
            .filter(History.Date >= since)
            .order_by(History.Date.asc())
            .all()
        )
        data = {}
        for row in records:
            data.setdefault(row.Currency, []).append({
                "date": row.Date.strftime("%Y-%m-%d"),
                "rate": row.Rate
            })
        return jsonify(data)
    finally:
        session.close()
        
@main.route("/history", methods=["GET"])
def history_page():
    return render_template("history.html")