import time
import requests, json
import sys
import datetime
import os
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

botToken = os.getenv("BOTTOKEN")
chatID = os.getenv('CHATID')
addresslist = [] #input your address
frequency = 2 #minutes
usdtAddress = 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'


def telegram_send(message):
    chat_id = chatID
    bot = Bot(token=botToken)
    bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')


def getTronResult(address:str, limit=5): 
    #default check the latest 5 transactions
    
    url = requests.get(f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20?limit={limit}&contract_address={usdtAddress}")
    text = url.text
    data = json.loads(text)
    print(data)
    data = data['data']
    return data

def check(jsonReturn):
    CheckStartTime = time.time()-(60*frequency) # 1minute
    #print(CheckStartTime)
    CheckStartTime = CheckStartTime*1000

    for result in jsonReturn:
        print('checking')

        if result['block_timestamp'] > CheckStartTime:
            txid = result['transaction_id']
            txidLink = f'<a href="https://tronscan.io/#/transaction/{txid}">{txid}</a>'
            
            sendFrom = result['from']
            sendTo = result['to']
            
            decimals = result['token_info']['decimals']
            value = int(result['value'])
            
            amount = value / 10**decimals
            
            ts = result['block_timestamp']/1000
            datetime = time.strftime('%A, %Y-%m-%d %H:%M:%S', time.localtime(ts))
            
            
            if sendFrom in addresslist:
                telegram_send(f"<b>📤Outgoing Transaction Notice</b>\n====\n<b>Txid:</b> {txidLink}\n<b>Send From:</b>\n{sendFrom}\n<b>Send To:</b>\n{sendTo}\n<b>Amuount:</b> {amount:,}\n<b>Date Time:</b> {datetime}")
                
                
            elif sendTo in addresslist:
                telegram_send(f"<b>📥Incoming Transaction Notice</b>\n====\n<b>Txid:</b> {txidLink}\n<b>Send From:</b>\n{sendFrom}\n<b>Send To:</b>\n{sendTo}\n<b>Amuount:</b> {amount:,}\n<b>Date Time:</b> {datetime}")
                
                
            else: 
                telegram_send(f"<b>Transaction Notice</b>\n====\n<b>Txid:</b> {txidLink}\n<b>Send From:</b>\n{sendFrom}\n<b>Send To:</b>\n{sendTo}\n<b>Amuount:</b> {amount:,}\n<b>Date Time:</b> {datetime}")



if __name__ == "__main__":
    try:
        print(addresslist)
        for i in addresslist:
            addr = getTronResult(i)
            check(addr)
    except Exception as e:
        telegram_send(f'Error\n{e}')
        