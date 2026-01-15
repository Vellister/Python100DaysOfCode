import streamlit as st
import pandas as pd
import os
import plotly.express as px

# aegis finance dashboard configuration
st.set_page_config(page_title="aegis finance", layout="wide", page_icon="🛡️")

# main path for the processed reports
reports_dir = r"C:\Users\User\Desktop\dashboard-financeiro\reports"


def load_data():

    files = [f for f in os.listdir(reports_dir) if f.endswith('.csv')]
    if not files:
        return None


    all_chunks = []
    for f in files:
        try:
            temp_df = pd.read_csv(os.path.join(reports_dir, f))
            temp_df.columns = [c.lower() for c in temp_df.columns]
            all_chunks.append(temp_df)
        except Exception:
            continue

    if not all_chunks:
        return None

    df = pd.concat(all_chunks, ignore_index=True)


    date_cols = [c for c in df.columns if 'date' in c or 'dt' in c]
    if date_cols:
        df['date_dt'] = pd.to_datetime(df[date_cols[0]], errors='coerce')

    # rebuilding categories if one-hot encoded by the model
    if 'category' not in df.columns:
        cat_cols = [c for c in df.columns if c.startswith('category_')]
        if cat_cols:
            df['category'] = df[cat_cols].idxmax(axis=1).str.replace('category_', '')

    # mapping xgboost model results
    df['is_fraud_val'] = df['is_fraud'] if 'is_fraud' in df.columns else 0
    df['prob_val'] = df['prob'] if 'prob' in df.columns else 0.0

    return df


st.title("🛡️ aegis finance: intelligence hub")
st.markdown("---")

data = load_data()

if data is not None:
    fraud_data = data[data['is_fraud_val'] == 1]
    total_amt = data['amt'].sum()

    # 1. high-level metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("total processed", f"${total_amt:,.2f}")
    col2.metric("security alerts", len(fraud_data), delta="suspicious", delta_color="inverse")
    col3.metric("system safety", f"{100 - (len(fraud_data) / len(data) * 100) if len(data) > 0 else 100:.1f}%")

    st.markdown("### 🧠 intelligence insights")
    # focus only on timeline and categories as requested
    tab_time, tab_cat = st.tabs(["spending timeline", "category risk"])

    with tab_time:
        if 'date_dt' in data.columns:
            # grouping by date for the line chart
            timeline_df = data.dropna(subset=['date_dt'])
            if not timeline_df.empty:
                timeline = timeline_df.groupby(timeline_df['date_dt'].dt.date)['amt'].sum().reset_index()
                timeline.columns = ['date', 'amount']
                fig_time = px.line(timeline, x='date', y='amount', markers=True, template="plotly_dark")
                st.plotly_chart(fig_time, use_container_width=True)
            else:
                st.info("no valid date data found for timeline chart")
        else:
            st.info("date column not found")

    with tab_cat:
        if 'category' in data.columns:
            # sorted and horizontal category chart for better readability
            cat_sum = data.groupby('category')['amt'].sum().sort_values(ascending=False).head(10).reset_index()
            fig_cat = px.bar(cat_sum, x='amt', y='category', orientation='h', color='amt', template="plotly_dark")
            fig_cat.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
            st.plotly_chart(fig_cat, use_container_width=True)

    # 2. top risk alerts based on xgboost probability
    st.markdown("### 🚨 critical security log")
    if not fraud_data.empty:
        st.dataframe(
            fraud_data.nlargest(10, 'amt')[['date', 'merchant', 'amt', 'prob_val']],
            column_config={
                "amt": st.column_config.NumberColumn("value", format="$%.2f"),
                "prob_val": st.column_config.ProgressColumn("risk score", min_value=0, max_value=1, format="%.2f"),
                "date": "date",
                "merchant": "merchant"
            },
            hide_index=True, use_container_width=True
        )
    else:
        st.success("monitoring active: no critical alerts found at the moment")

    # 3. full audit trail with optimized view
    with st.expander(" full transaction history"):
        st.dataframe(
            data[['date', 'merchant', 'category', 'amt', 'is_fraud_val', 'prob_val']],
            column_config={
                "amt": st.column_config.NumberColumn("amount", format="$%.2f"),
                "prob_val": st.column_config.ProgressColumn("confidence", format="%.2f", min_value=0, max_value=1),
                "is_fraud_val": st.column_config.CheckboxColumn("flagged?")
            },
            use_container_width=True, hide_index=True
        )
else:
    st.info("aegis finance is waiting for data. please run the watcher script first.")
