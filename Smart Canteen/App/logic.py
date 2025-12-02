import joblib
import pandas as pd
from pathlib import Path

# Resolve project root (smart_canteen/)
ROOT_DIR = Path(__file__).resolve().parents[1]

MODEL_DEMAND_PATH = ROOT_DIR / "models" / "model_demand.pkl"
MODEL_WAIT_PATH   = ROOT_DIR / "models" / "model_waittime.pkl"
MODEL_PREP_PATH   = ROOT_DIR / "models" / "model_prep_level.pkl"

# Load models once at import
model_demand = joblib.load(MODEL_DEMAND_PATH)
model_wait   = joblib.load(MODEL_WAIT_PATH)
model_prep   = joblib.load(MODEL_PREP_PATH)


def get_recommendation(input_dict):
    """
    input_dict: plain Python dict with all required fields.
    Returns: (demand_pred, wait_pred, prep_level)
    """

    # 1) Demand prediction (MODEL 1)
    X1 = pd.DataFrame([{
        "day_of_week":        input_dict["day_of_week"],
        "time_slot":          input_dict["time_slot"],
        "item":               input_dict["item"],
        "historical_orders":  input_dict["historical_orders"],
        "item_popularity":    input_dict["item_popularity"],
        "is_exam_week":       input_dict["is_exam_week"],
        "special_event_flag": input_dict["special_event_flag"],
        "weather":            input_dict["weather"],
    }])

    demand_pred = float(model_demand.predict(X1)[0])

    # 2) Wait time prediction (MODEL 2)
    X2 = pd.DataFrame([{
        "queue_length":   input_dict["queue_length"],
        "active_counters": input_dict["active_counters"],
        "staff_count":    input_dict["staff_count"],
        "avg_prep_time":  input_dict["avg_prep_time"],
        "time_slot":      input_dict["time_slot"],
    }])

    wait_pred = float(model_wait.predict(X2)[0])

    # 3) Prep level prediction (MODEL 3)
    # Here we actually use predicted demand as one of the inputs
    X3 = pd.DataFrame([{
        "historical_orders":       input_dict["historical_orders"],
        "profit_margin":           input_dict["profit_margin"],
        "ingredient_availability": input_dict["ingredient_availability"],
        "prep_time":               input_dict["prep_time"],
        "item_popularity":         input_dict["item_popularity"],
        "wastage_history":         input_dict["wastage_history"],
    }])

    prep_level = model_prep.predict(X3)[0]

    return demand_pred, wait_pred, prep_level
