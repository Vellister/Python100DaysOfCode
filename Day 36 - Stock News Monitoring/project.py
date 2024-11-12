import os
import html
import requests
from newsapi import NewsApiClient
from twilio.rest import Client
from datetime import datetime, timedelta

today = datetime.now()


def get_previous_date(date):
    if date.weekday() == 0:
        return date - timedelta(days=3)
    elif date.weekday() == 6:
        return date - timedelta(days=2)
    return date - timedelta(days=1)


day = get_previous_date(today)
last_date = f'{day.year}-{day.month}-{day.day}'
day = get_previous_date(day)
before_last_date = f'{day.year}-{day.month}-{day.day}'
today = f'{today.year}-{today.month}-{today.day}'

account_sid = os.environ["TWILIO_SID"]
auth_token = os.environ["TWILIO_TOKEN"]
client = Client(account_sid, auth_token)

twilio_number = os.environ["TWILIO_NUMBER"]
my_number = os.environ["MY_NUMBER"]

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
ALPHAVANTAGE_URL = "https://www.alphavantage.co/query"
NEWS_URL = "https://newsapi.org/v2/everything"

stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "outputsize": "compact",
    "apikey": os.environ["ALPHAVANTAGE_API_KEY"]
}

response = requests.get(ALPHAVANTAGE_URL, params=stock_params)
response.raise_for_status()
stock_data = response.json()

close_yesterday = float(stock_data["Time Series (Daily)"][last_date]["4. close"])
close_today = float(stock_data["Time Series (Daily)"][before_last_date]["4. close"])
abs_percentage = abs((close_today - close_yesterday) * 100 / close_yesterday)
if abs_percentage >= 5:
    news_api = NewsApiClient(api_key=os.environ["NEWS_API_KEY"])
    all_articles = news_api.get_everything(q=COMPANY_NAME, from_param=last_date,
                                           to=today, language='en')

    articles = all_articles["articles"][:3]
    news = ""
    for article in articles:
        if close_today > close_yesterday:
            arrow = '🔺'
        else:
            arrow = '🔻'
        title = f"\n{STOCK}: {arrow} {abs_percentage:.0f}%"
        headline = html.unescape(article["title"])
        brief = html.unescape(article["description"])

        news += title
        news += f"HEADLINE: {headline}\n"
        news += f"BRIEF: {brief}\n\n"
        message = client.messages.create(body=news, from_=twilio_number, to=my_number)
