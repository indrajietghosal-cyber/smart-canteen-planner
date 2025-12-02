# ---------------------------------------------------------
# SMART CANTEEN DASHBOARD
# This Streamlit app integrates 3 ML models:
# 1. Demand Prediction
# 2. Wait Time Prediction
# 3. Prep Level Classification
# ---------------------------------------------------------

import streamlit as st
import pandas as pd
from logic import get_recommendation

def color_prep_level(level):
    if level == "High":
        return "🔴 **High**"
    elif level == "Medium":
        return "🟠 **Medium**"
    else:
        return "🟢 **Low**"


# ---- Page config ----
st.set_page_config(
    page_title="Smart Canteen Planner",
    layout="wide"
)

st.title("🍽️ Smart Canteen Demand & Prep Planner")

# ---- About Section ----
st.markdown(
    """
    <div style="padding: 10px; background-color: #f7f7f7; border-radius: 8px; margin-bottom: 20px;">
        <h3 style="margin-bottom: 5px;">📘 About This Application</h3>
        <p style="margin-top: 0px; font-size: 16px;">
            This Smart Canteen application integrates three machine learning models:
            <ul>
                <li><b>Demand Forecasting Model</b> – predicts expected plates per item.</li>
                <li><b>Wait Time Prediction Model</b> – estimates queue wait time based on staffing & counters.</li>
                <li><b>Prep Level Classifier</b> – recommends High/Medium/Low prep level for each menu item.</li>
            </ul>
            It helps canteen managers optimize operations, reduce wastage, and improve service efficiency.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---- Team Details ----
st.markdown(
    """
    <div style="padding: 10px; background-color: #eef6ff; border-radius: 8px; margin-bottom: 20px;">
        <h4>👥 Project Team</h4>
        <ul>
            <li>Balakrishnan — B2025069</li>
            <li>Dhiraj Patil — B2025073</li>
            <li>Divyanshu Chadda — B2025074</li>
            <li>Indrajiet Ghosal — B2025080</li>
            <li>Jayaram Movva — B2025082</li>
            <li>Aman Aryan — B2025089</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True
)

st.write(
    "Use the controls in the sidebar to get predictions for demand, wait time, "
    "and preparation levels for canteen items."
)

# ---------------- SIDEBAR: CONTEXT INPUTS ----------------
st.sidebar.header("🕒 Time Slot & Operations")

day_of_week = st.sidebar.selectbox("Day of Week", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
time_slot = st.sidebar.selectbox("Time Slot", ["Breakfast", "Lunch", "Snacks", "Dinner"])

is_exam_week = st.sidebar.checkbox("Exam Week?")
special_event_flag = st.sidebar.checkbox("Special Event on Campus?")
weather = st.sidebar.selectbox("Weather", ["Normal", "Rainy"])

queue_length = st.sidebar.number_input("Current Queue Length", 0, 200, 10)
active_counters = st.sidebar.number_input("Active Counters", 1, 10, 2)
staff_count = st.sidebar.number_input("Staff Count", 1, 20, 5)
avg_prep_time = st.sidebar.number_input("Avg Prep Time (minutes)", 1.0, 30.0, 5.0)

st.sidebar.markdown("---")
st.sidebar.header("🍛 Menu / Financial (Single Item View)")

item = st.sidebar.selectbox("Menu Item (single-item view)", ["Idli", "Dosa", "Samosa", "Chai", "Coffee", "Fried Rice"])

historical_orders = st.sidebar.number_input("Historical Orders (avg)", 0, 500, 50)
item_popularity = st.sidebar.slider("Item Popularity (0–1)", 0.0, 1.0, 0.5)

profit_margin = st.sidebar.slider("Profit Margin Score (0–1)", 0.0, 1.0, 0.6)
ingredient_availability = st.sidebar.slider("Ingredient Availability (0–1)", 0.0, 1.0, 0.9)
prep_time = st.sidebar.number_input("Prep Time (minutes)", 1.0, 30.0, 7.0)
wastage_history = st.sidebar.slider("Wastage History Score (0–1)", 0.0, 1.0, 0.2)

get_reco = st.sidebar.button("✅ Get Recommendations")

# ---------------- MAIN LAYOUT: TABS ----------------
tab_single, tab_all = st.tabs(["🔹 Single Item View", "🔸 All Items Overview"])

if get_reco:
    # Common inputs packed into a dict
    base_input = {
        "day_of_week": day_of_week,
        "time_slot": time_slot,
        "is_exam_week": int(is_exam_week),
        "special_event_flag": int(special_event_flag),
        "weather": weather,
        "queue_length": queue_length,
        "active_counters": active_counters,
        "staff_count": staff_count,
        "avg_prep_time": avg_prep_time,
        "historical_orders": historical_orders,
        "item_popularity": item_popularity,
        "profit_margin": profit_margin,
        "ingredient_availability": ingredient_availability,
        "prep_time": prep_time,
        "wastage_history": wastage_history,
    }

    # ---------- SINGLE ITEM VIEW ----------
    with tab_single:
        st.subheader("📊 Recommendation Card – Single Item")

        single_input = base_input.copy()
        single_input["item"] = item

        demand_pred, wait_pred, prep_level = get_recommendation(single_input)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Predicted Demand (plates)", f"{demand_pred:.1f}")
        with col2:
            st.metric("Expected Wait Time (min)", f"{wait_pred:.1f}")
        with col3:
            st.markdown(f"**Prep Level:** {color_prep_level(prep_level)}")

        st.markdown("---")
        st.caption(
            "This view uses the selected menu item and financial parameters from the sidebar "
            "to generate a detailed recommendation."
        )

    # ---------- ALL ITEMS OVERVIEW ----------
    with tab_all:
        st.subheader("🍽️ Overview – All Menu Items for This Time Slot")

        items_list = ["Idli", "Dosa", "Samosa", "Chai", "Coffee", "Fried Rice"]
        rows = []

        for it in items_list:
            item_input = base_input.copy()
            item_input["item"] = it

            # Small variation per item so they don't look identical
            if it in ["Chai", "Coffee"] and time_slot == "Snacks":
                item_input["historical_orders"] = historical_orders + 20
                item_input["item_popularity"] = min(1.0, item_popularity + 0.1)
            elif it in ["Idli", "Dosa"] and time_slot == "Breakfast":
                item_input["historical_orders"] = historical_orders + 15
            else:
                item_input["historical_orders"] = historical_orders

            d_pred, w_pred, p_level = get_recommendation(item_input)

            rows.append({
                "Item": it,
                "Predicted Demand (plates)": round(d_pred, 1),
                "Expected Wait Time (min)": round(w_pred, 1),
                "Prep Level": p_level,
            })

        for r in rows:
            r["Prep Level"] = color_prep_level(r["Prep Level"])

        df = pd.DataFrame(rows)

        st.dataframe(df, use_container_width=True)

        st.markdown("#### 📈 Demand by Item")
        st.bar_chart(df.set_index("Item")["Predicted Demand (plates)"])

        st.caption(
            "This overview shows predicted demand and recommended preparation level for each item "
            "for the selected time slot and operational conditions."
        )

else:
    with tab_single:
        st.info("Use the sidebar to set parameters and click **'Get Recommendations'**.")
    with tab_all:
        st.info("Once you generate recommendations, an overview of all items will appear here.")