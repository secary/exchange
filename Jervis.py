import pandas as pd
import numpy as np
import torch
import time
import io
import base64
import matplotlib.pyplot as plt

from app.prediction.methods import fetch_history, build_sequences, split, load_latest_model, evaluate_metrics, scale, preprocess

from sqlalchemy.orm import sessionmaker
from config.settings import get_engine  # 你已有这个
from app.models import Prediction  # 你的 Prediction ORM

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
        print("✅ 数据成功导入 prediction 表")
    except Exception as e:
        session.rollback()
        print("❌ 导入失败:", e)
    finally:
        session.close()


def lstm_plot(df_predict, df_forecast, currency: str, days: int = 7) -> str:
    plt.figure(figsize=(14, 6))
    plt.plot(df_predict["Date"], df_predict["Rates"], label="Actual", linewidth=2)
    plt.plot(df_predict["Date"], df_predict["Predicted_Rates"], label="Predicted", linewidth=2)
    plt.plot(df_forecast["Date"], df_forecast["Predicted_Rates"], label="Forecast", linestyle="--")
    plt.xlabel("Date")
    plt.ylabel("Exchange Rate")
    plt.title(f"{currency.upper()} Exchange Rate Prediction + {days}-Day Forecast")
    plt.legend()
    plt.grid()
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)

    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    return img_base64  # 可直接嵌入 HTML

def main(currency: str, days: int=7):
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_dir = "./app/prediction/models/RateLSTM"
    model = load_latest_model(model_dir, currency, device)
    
    currency = currency.upper()
    df = preprocess(fetch_history(currency, 30))
    data = scale(df[['Rate']])

    seq = 48
    X, y = build_sequences(data, seq)
    X_train, y_train, X_test, y_test = split(X, y, 0.8)


    preds = scale(model.predict(X_test).cpu().numpy(), inverse=True)
    trues = scale(y_test.cpu().numpy(), inverse=True)
    dates = df.index[seq + len(X_train):]

    df_predict = pd.DataFrame({
        "Date": dates,
        "Currency": currency,
        "Rates": trues.flatten(),
        "Predicted_Rates": preds.flatten(),
        "Locals": time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime())
    })
    
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
    
    
    plot = lstm_plot(df_predict, df_forecast, currency)
    
    return df_forecast


if __name__ == "__main__":
    # currency = input("Please input the currecy for forecast: ").upper()
    aud = main('aud')
    insert_predictions(aud)
    jpy = main('jpy')
    insert_predictions(jpy)


   