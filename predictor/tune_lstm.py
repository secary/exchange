import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from loguru import logger
import uuid
from config.logger_config import trace_ids

# ✅ 绑定 loguru 的 name 字段，用于日志分类输出
script_name = os.path.splitext(os.path.basename(__file__))[0]
logger = logger.bind(name="jervis", display=script_name)
# 设置 trace_id（独立运行时使用 uuid；也支持从环境变量传入）
trace_id = os.getenv("TRACE_ID_JERVIS") or f"JERVIS-{uuid.uuid4()}"
trace_ids["jervis"].set(trace_id)

import torch
from sklearn.metrics import mean_squared_error
from typing import List, Dict, Any
from datetime import datetime

from methods import preprocess, fetch_history, build_sequences, scale, split
from models.lstm import RateLSTM  # ✅ 保持绝对路径
from config.settings import get_currency_code, CURRENCIES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models", "RateLSTM")


def grid_search_lstm(
    X: torch.Tensor,
    y: torch.Tensor,
    currency: str,
    device: str,
    epoch_candidates: List[int],
    batch_candidates: List[int],
    lr_candidates: List[float],
    save_dir: str
) -> Dict[str, Any]:
    """
    用于 RateLSTM 的网格搜索调参，并将最优模型保存到 save_dir。
    """
    os.makedirs(save_dir, exist_ok=True)

    # 拆分训练/验证集
    n_total = len(X)
    n_val = int(n_total * 0.2)
    X_train, X_val = X[:-n_val], X[-n_val:]
    y_train, y_val = y[:-n_val], y[-n_val:]

    best_mse = float('inf')
    best_cfg = {}

    for epochs in epoch_candidates:
        for batch_size in batch_candidates:
            for lr in lr_candidates:
                model = RateLSTM().to(device)
                model.train_model(X_train, y_train, epochs, batch_size, lr, device)

                # 验证集评估
                val_preds = model.predict(X_val.to(device)).cpu().numpy().flatten()
                val_trues = y_val.cpu().numpy().flatten()
                mse = mean_squared_error(val_trues, val_preds)

                logger.info(f"epochs={epochs}, batch={batch_size}, lr={lr:.4e} → val MSE={mse:.6f}")

                if mse < best_mse:
                    best_mse = mse
                    timestamp = datetime.now().strftime("%Y%m%d")
                    model_path = os.path.join(save_dir, f"{model.__class__.__name__}_{currency}_{timestamp}.pth")
                    model.save(model_path)

                    best_cfg = {
                        "epochs": epochs,
                        "batch_size": batch_size,
                        "lr": lr,
                        "val_mse": mse,
                        "model_path": model_path
                    }

    logger.info(f"\n✅ Best config saved to {best_cfg['model_path']}: {best_cfg}")
    return best_cfg


def main(currency: str, model_dir=MODEL_DIR):
    data = fetch_history(currency, days=30)
    data = preprocess(data)
    data_scaled = scale(data[['Rate']])

    X, y = build_sequences(data_scaled, seq_len=48)
    X_train, y_train, _ , _ = split(X, y, train_ratio=0.8)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    best_config = grid_search_lstm(
        X=X_train,
        y=y_train,
        currency=currency,
        device=device,
        epoch_candidates=[50, 100],
        batch_candidates=[32, 64],
        lr_candidates=[1e-2, 1e-3, 1e-4],
        save_dir=model_dir
    )

    logger.info(f"✅ Done. Best model saved to: {best_config['model_path']}")

if __name__ == "__main__":
    try:
        for currency in CURRENCIES:
            currency_en = get_currency_code(currency)
            if not currency_en:
                logger.warning(f"⚠️ {currency}未存在于数据库内")
            if len(fetch_history(currency_en, 30)) < 500:
                pass
                logger.warning(f"⚠️ 当前{currency}数据不足，暂不训练")
            else:
                logger.info(f"🔁 启动{currency_en}汇率LSTM调优，TRACE_ID={trace_id}")
                main(currency_en)
                logger.info(f"🔮 {currency}LSTM预测调优完成")
    except Exception as e:
        logger.exception(f"❌ 出现错误：{e}")  # 包含堆栈 trace_id
   