import pandas as pd
import joblib
import pdfplumber

model_path = r"C:\Users\User\Desktop\dashboard-financeiro\data\models\xgboost_fraud_model.pkl"
features_path = r"C:\Users\User\Desktop\dashboard-financeiro\data\models\model_features.pkl"
pdf_path = r"C:\Users\User\Desktop\dashboard-financeiro\reports\fake_statement_01.pdf"


def run_fraud_detection():
    model = joblib.load(model_path)
    model_features = joblib.load(features_path)

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        table = page.extract_table()
        df = pd.DataFrame(table[1:], columns=table[0])

    df.columns = [col.lower() for col in df.columns]

    if 'description' in df.columns:
        df = df.rename(columns={'description': 'merchant'})
    if 'amount ($)' in df.columns:
        df = df.rename(columns={'amount ($)': 'amt'})

    df['amt'] = df['amt'].astype(float)
    df['date_dt'] = pd.to_datetime(df['date'])
    df['hour'] = df['date_dt'].dt.hour
    df['day_of_week'] = df['date_dt'].dt.dayofweek
    df['month'] = df['date_dt'].dt.month

    df['gender'] = 'F'
    df_processed = pd.get_dummies(df, columns=['category', 'gender'])

    df_final = df_processed.reindex(columns=model_features, fill_value=0)

    probs = model.predict_proba(df_final)[:, 1]
    predictions = (probs >= 0.7).astype(int)

    df['is_fraud_prediction'] = predictions
    df['fraud_probability'] = probs

    frauds_found = df[df['is_fraud_prediction'] == 1]

    if not frauds_found.empty:
        print(f"alert: detected {len(frauds_found)} suspicious transactions")
        print(frauds_found[['date', 'merchant', 'amt', 'fraud_probability']])
    else:
        print("clean: no suspicious transactions found")


if __name__ == "__main__":
    run_fraud_detection()
