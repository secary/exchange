import logging.config
import uuid
from config.logger_config import LOGGING_CONFIG, trace_ids
import os

# 获取项目根目录（Jervis.py 所在目录的上一级）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "app", "prediction", "models", "RateLSTM")

# 日志配置
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("jervis")

# 设置 trace_id（和 Flask 请求无关时也初始化一个）
trace_id = os.getenv("TRACE_ID_JERVIS") or f"JERVIS-{uuid.uuid4()}"
trace_ids["jervis"].set(trace_id)
logger.info(f"🔁 启动预测任务，TRACE_ID={trace_id}")

import pandas as pd
import numpy as np
import torch
import time
import io
import base64
import matplotlib.pyplot as plt

from app.prediction.methods import fetch_history, build_sequences, split, load_latest_model, evaluate_metrics, scale, preprocess
from sqlalchemy.orm import sessionmaker
from config.settings import get_engine, get_currency_code, CURRENCIES # 你已有这个
from app.models import Prediction # 你的 Prediction ORM

def insert_predictions(df: pd.DataFrame):
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        for _, row in df.iterrows():
            entry = Prediction(
                Date=row["Date"],
                Currency=row["Currency"],
                Predicted_rate=row["Predicted_Rates"],
                Locals=row["Locals"]
            )
            session.merge(entry)  # merge避免主键重复插入报错
        session.commit()
        logger.info("✅ 数据成功导入 prediction 表")
    except Exception as e:
        session.rollback()
        logger.error("❌ 导入失败:", e)
    finally:
        session.close()


def main(currency: str, days: int=7):
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = load_latest_model(MODEL_DIR, currency, device)
    
    currency = currency.upper()
    df = preprocess(fetch_history(currency, 30))
    data = scale(df[['Rate']])

    seq = 48
    # X, y = build_sequences(data, seq)
    # X_train, y_train, X_test, y_test = split(X, y, 0.8)


    # preds = scale(model.predict(X_test).cpu().numpy(), inverse=True)
    # trues = scale(y_test.cpu().numpy(), inverse=True)
    # dates = df.index[seq + len(X_train):]

    # df_predict = pd.DataFrame({
    #     "Date": dates,
    #     "Currency": currency,
    #     "Rates": trues.flatten(),
    #     "Predicted_Rates": preds.flatten(),
    #     "Locals": time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime())
    # })
    
    # Generate future predictions
    future_steps = days * seq
    last_seq = data[-seq:].copy()
    future_scaled = []

    model.eval()
    for _ in range(future_steps):
        inp = torch.tensor(last_seq[np.newaxis, ...], dtype=torch.float32).to(device)
        with torch.no_grad():
            pred = model(inp).cpu().numpy().flatten()
        future_scaled.append(pred[0])
        last_seq = np.vstack([last_seq[1:], pred.reshape(1, 1)])

    future_scaled = np.array(future_scaled).reshape(-1, 1)
    future = scale(future_scaled, inverse=True)
    step = df.index[1] - df.index[0]
    future_dates = [df.index[-1] + (i+1)*step for i in range(future_steps)]

    df_forecast = pd.DataFrame({
        "Date": future_dates,
        "Currency": currency,
        "Predicted_Rates": future.flatten(),
        "Locals": time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime())
    })
    
    
    logger.info(f"🔮 未来{days}内{currency}预测完成，共 {len(df_forecast)} 条")
    return df_forecast


if __name__ == "__main__":
    try:
        for currency in CURRENCIES:
            currency_en = get_currency_code(currency)
            if not currency_en:
                logger.warning(f"⚠️ {currency}未存在于数据库内")
            if len(fetch_history(currency_en, 30)) < 500:
                pass
                logger.warning(f"⚠️ 当前{currency}数据不足，暂不预测")
            else:
                main(currency_en)
                logger.info(f"🔮 {currency}预测完成")
    except Exception as e:
        logger.exception(f"❌ 出现错误：{e}")  # 包含堆栈 trace_id
   