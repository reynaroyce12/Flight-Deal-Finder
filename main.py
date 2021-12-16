import os
import requests
from datetime import *
from dateutil.relativedelta import *
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('API_KEY')
account_sid = os.getenv('ACCOUNT_SID')
auth_token = os.getenv('AUTH_TOKEN')
from_num = os.getenv('FROM_NUM')
to_num = os.getenv('TO_NUM')

sheety_endpoint = 'https://api.sheety.co/b92cd03a1abe1e5baea51d691366a176/flightDeals/prices'
tequila_endpoint = 'https://tequila-api.kiwi.com/v2/search'

tequila_header = {
    "apikey": api_key
}

sheety_response = requests.get(url=sheety_endpoint)
sheet_data = sheety_response.json()
prices = sheet_data['prices']

tomorrow = date.today() + relativedelta(days=1)
tomorrow = tomorrow.strftime('%d/%m/%Y').replace("-", "/")
six_months = date.today() + relativedelta(months=+6)
six_months = six_months.strftime('%d/%m/%Y').replace("-", "/")

for i in range(len(prices)):
    code = sheet_data['prices'][i]['iataCode']

    params = {
        "fly_from": "LON",
        "fly_to": f"{code}",
        "dateFrom": f"{tomorrow}",
        "dateTo": f"{six_months}",
        "curr": "GBP"
    }

    response = requests.get(url=tequila_endpoint, headers=tequila_header, params=params)
    tequila_data = response.json()

    for dictionary in prices:
        if tequila_data['data'][i]['price'] < dictionary['lowestPrice']:
            from_place = tequila_data['data'][i]['flyFrom']
            to_place = tequila_data['data'][i]['flyTo']
            to_city = tequila_data['data'][i]['cityTo']
            offer_price = tequila_data['data'][i]['price']

            client = Client(account_sid, auth_token)
            message = client.messages \
                .create(
                    body=f"Low price alert!💰 Only £{offer_price} to fly from London-{from_place}"
                         f"to {to_city}-{to_place}"
                         f" from {tomorrow} to {six_months} ✈️",
                    from_=f"{from_num}",
                    to=f"{to_num}"
                )
            print(message.status)
