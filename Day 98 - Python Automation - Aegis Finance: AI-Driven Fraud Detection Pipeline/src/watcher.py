import imaplib
import email
import os
import pandas as pd
import joblib
import pdfplumber
import requests
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
IMAP_SERVER = os.getenv("IMAP_SERVER")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

MODEL_PATH = r"C:\Users\User\Desktop\dashboard-financeiro\data\models\xgboost_fraud_model.pkl"
FEATURES_PATH = r"C:\Users\User\Desktop\dashboard-financeiro\data\models\model_features.pkl"
SAVE_DIR = r"C:\Users\User\Desktop\dashboard-financeiro\reports"


def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception:
        pass


def process_invoice(pdf_path):
    model = joblib.load(MODEL_PATH)
    model_features = joblib.load(FEATURES_PATH)

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        table = page.extract_table()
        df = pd.DataFrame(table[1:], columns=table[0])

    df.columns = [col.lower() for col in df.columns]
    if 'description' in df.columns: df = df.rename(columns={'description': 'merchant'})
    if 'amount ($)' in df.columns: df = df.rename(columns={'amount ($)': 'amt'})

    df['amt'] = df['amt'].astype(float)
    # forcing standard format to avoid parsing issues later
    df['date_dt'] = pd.to_datetime(df['date'], errors='coerce')
    df['hour'] = df['date_dt'].dt.hour
    df['day_of_week'] = df['date_dt'].dt.dayofweek
    df['month'] = df['date_dt'].dt.month
    df['gender'] = 'F'

    df_processed = pd.get_dummies(df, columns=['category', 'gender'])
    df_final = df_processed.reindex(columns=model_features, fill_value=0)

    probs = model.predict_proba(df_final)[:, 1]
    df['is_fraud'] = (probs >= 0.7).astype(int)
    df['prob'] = probs

    # saving with explicit date formatting
    csv_name = f"processed_{os.path.basename(pdf_path).replace('.pdf', '.csv')}"
    df.to_csv(os.path.join(SAVE_DIR, csv_name), index=False, date_format='%Y-%m-%d %H:%M:%S')

    frauds = df[df['is_fraud'] == 1]
    for _, row in frauds.iterrows():
        msg = f"🚨 aegis alert: fraud at {row['merchant']} | ${row['amt']:.2f} | risk: {row['prob']:.2%}"
        send_telegram_alert(msg)


def check_email():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")
        _, messages = mail.search(None, '(UNSEEN SUBJECT "Invoice")')
        for num in messages[0].split():
            _, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart': continue
                if part.get('Content-Disposition') is None: continue
                filename = part.get_filename()
                if filename and filename.endswith(".pdf"):
                    filepath = os.path.join(SAVE_DIR, filename)
                    with open(filepath, "wb") as f:
                        f.write(part.get_payload(decode=True))
                    process_invoice(filepath)
        mail.close()
        mail.logout()
    except Exception as e:
        print(f"sync error: {e}")


if __name__ == "__main__":
    check_email()
