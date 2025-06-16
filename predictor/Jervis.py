import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from loguru import logger
import uuid
from config.logger_config import trace_ids
# 设置 trace_id（独立运行时使用 uuid；也支持从环境变量传入）
trace_id = os.getenv("TRACE_ID_JERVIS") or f"JERVIS-{uuid.uuid4()}"
trace_ids["jervis"].set(trace_id)

# ✅ 绑定 loguru 的 name 字段，用于日志分类输出
logger = logger.bind(name="jervis")

# 获取项目根目录（Jervis.py 所在目录的上一级）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models", "RateLSTM")

import pandas as pd
import numpy as np
import torch
import time

from methods import fetch_history, load_latest_model, scale, preprocess
from sqlalchemy.orm import sessionmaker
from config.settings import get_engine, get_currency_code, CURRENCIES # 你已有这个
from utils.models import Prediction # 你的 Prediction ORM


def insert_predictions(df: pd.DataFrame):
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # # 1️⃣ 清空 prediction 表
        session.query(Prediction).delete()

        # 2️⃣ 批量插入新数据
        records = [
            Prediction(
                Date=row["Date"],
                Currency=row["Currency"],
                Predicted_rate=row["Predicted_Rates"],
                Locals=row["Locals"]
            ) for _, row in df.iterrows()
        ]
        session.bulk_save_objects(records)
        session.commit()
        logger.info(f"✅ 成功写入 {len(records)} 条预测数据")

    except Exception as e:
        session.rollback()
        logger.error(f"❌ 导入 prediction 表失败: {e}")

    finally:
        session.close()


def lstm_predict(currency: str, days: int=7):
    
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

def main():
    try:
        all_results = []  # ⬅️ 存储所有币种的预测结果

        for currency in CURRENCIES:
            currency_en = get_currency_code(currency)
            if not currency_en:
                logger.warning(f"⚠️ {currency}未存在于数据库内")
                continue

            if len(fetch_history(currency_en, 30)) < 500:
                logger.warning(f"⚠️ 当前{currency}数据不足，暂不预测")
                continue

            result = lstm_predict(currency_en)
            if result is not None and not result.empty:
                all_results.append(result)
                logger.info(f"🔮 {currency}预测完成，共 {len(result)} 条")
            else:
                logger.warning(f"⚠️ {currency}预测结果为空")

        # 🔗 合并所有币种的预测结果为一个 DataFrame
        if all_results:
            merged_df = pd.concat(all_results, ignore_index=True)
            logger.info(f"✅ 所有币种预测合并完成，共 {len(merged_df)} 条")

            # ✍️ 写入数据库
            insert_predictions(merged_df)
        else:
                logger.warning("⚠️ 没有任何币种的预测结果被生成")

    except Exception as e:
        logger.exception(f"❌ 出现错误：{e}")


if __name__ == "__main__":
    logger.info("Nice to meet you. Lucky Jervis、来たわ!")
    main()
   