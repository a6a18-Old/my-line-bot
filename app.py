import requests
import re
import random
import configparser
from bs4 import BeautifulSoup
from flask import Flask, request, abort
from imgurpython import ImgurClient

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('d9vni23HMrx9az1UDeIfbJakTOAaVTslK4tqNyWxSRgmj6zTaswif5tegG2tvqOnCBtxnSPKe6nRfXe4M17s7olhVeP32AThNIR+T616SLS771J9irXZhgUduz3sr83rNOGg7QcpH0hFogGJyOExhgdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('2f853d54aa4d83fe5c408b7cab17b9be')

header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
}


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def apple_news():
    target_url = 'https://tw.appledaily.com/new/realtime'
    print('Start parsing appleNews....')
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    for index, data in enumerate(soup.select('.rtddt a'), 0):
        if index == 5:
            return content
        link = data['href']
        content += '{}\n\n'.format(link)
    return content

def ptt_news():
    url = 'https://www.pttweb.cc/hot/news/today'
    bbs_url = 'https://www.pttweb.cc'
    news_list = []

    html = requests.get(url, headers=header)
    soup = BeautifulSoup(html.text, 'html.parser')
    ptt_news = soup.select('div.e7-right-top-container.e7-no-outline-all-descendants a.e7-article-default')
    ptt_news = ptt_news[0:10]

    content = ''   # line只能傳入單純字串的型態，要把資料轉成str在一個一個串接上去。
    for news_item in ptt_news:
        content = content + news_item.text + "\n" + bbs_url + news_item['href'] + "\n\n"

    return content

def yahoo():
    url = 'https://www.dcard.tw/f/sex'

    html = requests.get(url, headers=header)

    soup = BeautifulSoup(html.text, 'html.parser')
    titles = soup.select('h3')

    href = soup.select('div.PostList_entry_1rq5Lf a.PostEntry_root_V6g0rd')
    a = href[0].get("href")
    return a

def yahoo_new():
    url = 'https://news.google.com/topics/CAAqKggKIiRDQkFTRlFvSUwyMHZNRGx1YlY4U0JYcG9MVlJYR2dKVVZ5Z0FQAQ?hl=zh-TW&gl=TW&ceid=TW%3Azh-Hant'
    header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
    }
    html = requests.get(url, headers=header)
    soup = BeautifulSoup(html.text, 'html.parser')
    article = soup.select('article h3 a')
    a = article[0].text
    b = 'https://news.google.com' + article[0].get("href")[1:]
    content = a + '\n' + b
    return content
    

    
    
# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("event.reply_token:", event.reply_token)
    print("event.message.text:", event.message.text)

    if event.message.text == "蘋果即時新聞":
        content = apple_news()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    
    if event.message.text == "yahoo":
        content = yahoo()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
        
    if event.message.text == "yahoo新聞":
        content = yahoo_new()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

    if event.message.text == "ptt新聞":
        content = ptt_news()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
     
    if event.message.text == "動畫新番":
        content = 'https://anime1.me/2020年冬季新番'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    
import os
if __name__ == "__main__":
    #port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
