# 🛡️ Aegis Finance: AI-Powered Fraud Detection Pipeline

Aegis Finance is an automated financial security ecosystem that monitors bank statements, detects fraudulent patterns using Machine Learning, and sends real-time alerts.

## 🚀 Overview
The project automates the entire flow of financial auditing:
1. **Extraction**: Monitors email inbox (IMAP) for new PDF invoices.
2. **Intelligence**: Processes transactions through a trained **XGBoost** model.
3. **Alerting**: Sends immediate notifications via **Telegram Bot** for suspicious activities.
4. **Visualization**: Provides an interactive **Streamlit** dashboard for spending analysis and security logs.

## 🧠 Machine Learning Core
The heart of Aegis is a Gradient Boosting model (XGBoost) trained on highly imbalanced retail transaction data. 
- **Key Metrics**: Achieved a PR-AUC of 0.87.
- **Features**: Analyzes transaction amount, category, hour of the day, and day of the week to identify anomalies.

## 🛠️ Tech Stack
- **Language**: Python 3.10+
- **AI/ML**: XGBoost, Scikit-learn, Pandas, Joblib
- **Automation**: IMAPlib (Email), PDFPlumber (Data Extraction)
- **Interface**: Streamlit, Plotly
- **Security**: Python-dotenv (Environment Variables)
- **Alerts**: Telegram Bot API

## 📁 Project Structure
- `src/app.py`: Streamlit dashboard interface.
- `src/watcher.py`: Background engine for email monitoring and ML inference.
- `data/models/`: Saved model weights and feature configurations.
- `reports/`: Storage for processed invoices and generated logs.

## 🔧 Setup
1. Clone the repository.
2. Create a `.env` file with your `EMAIL_USER`, `EMAIL_PASS`, `TELEGRAM_TOKEN`, and `CHAT_ID`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Run the watcher: `python src/watcher.py`.
5. Start the dashboard: `streamlit run src/app.py`.

## 🛡️ Security
This project follows industry standards for data protection, using environment variables for sensitive credentials and ignoring local reports and configuration files in version control.
