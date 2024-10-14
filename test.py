import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from forex_python.converter import CurrencyRates, CurrencyCodes

# Create an instance of CurrencyRates and CurrencyCodes
currency_rates = CurrencyRates()
currency_codes = CurrencyCodes()
#1 Ask for the currencies
base_currency = input("Enter the currency you want to exchange from (e.g., USD, EUR): ").upper()
target_currencies_input = input("Enter the currencies you want to exchange to (e.g., EUR, GBP, JPY): ")

# Split the input string into a list;  iterate over each element; eliminate
target_currencies_list = target_currencies_input.split(',')
target_currencies = []
for currency in target_currencies_list:
    t_currency = currency.upper()
    target_currencies.append(t_currency)
print(target_currencies)
#get the exchange rate
def get_current_rates(base_currency, target_currencies):
    print(f"Current exchange rates for {base_currency}:")
    rates = {}
    for currency in target_currencies:
        try:
            rate = currency_rates.get_rate(base_currency, currency)
            rates[currency] = rate
            print(f"{base_currency} to {currency}: {rate}")
        except Exception as e:
            print(f"Failed to retrieve data for {currency}: {e}")#Failed to retrieve data for CHF: Expecting value: line 1 column 1 (char 0)
    return rates

current_rates = get_current_rates(base_currency, target_currencies)

# 2. convert the amount
def convert_currency(amount, from_currency, to_currency):
    try:
        rate = currency_rates.get_rate(from_currency, to_currency)
        converted_amount = amount * rate
        print(f"{amount} {from_currency} is equal to {converted_amount:.2f} {to_currency}")
    except Exception as e:
        print(f"An error occurred during conversion: {e}")

# 3. Analyze Historical Data to Suggest if It's a Good Time for an Exchange
def analyze_currency_trend(pair, days=30):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    data = yf.download(pair,
                       start=start_date.strftime('%Y-%m-%d'),
                       end=end_date.strftime('%Y-%m-%d'),
                       interval='1d')  # Daily data
    if data.empty:
        print(f"No data available for {pair}.")
        return None

    close_prices = data['Close']
    latest_rate = close_prices.iloc[-1]
    historical_rate = close_prices.iloc[0]

    print(f"Start rate: {historical_rate}, Latest rate: {latest_rate}")
    average_rate = close_prices.mean()

    if latest_rate > average_rate:
        print(f"The latest rate is above the average rate. It might be a good time to exchange {pair[:3]} to {pair[3:]} now.") # the first three characters of the string pair
    elif latest_rate < average_rate:
        print(f"The latest rate is below the average rate. It might be better to wait before exchanging {pair[:3]} to {pair[3:]}.")
    else:
        print(f"The latest rate is equal to the average rate. {pair[:3]} to {pair[3:]}.")
##4
def get_current_price(pair):
    data = yf.download(pair, period='1d', interval='1m')
    #if not data.empty:
        #return data['Close'].iloc[-1]  # Return the latest closing price
   # return None  # Return None if there's no data
#stop order loop
def stop_order(pair, stop_price, amount):
    # ask for the ccy and stop price and amount
    base_currency = input("Enter the currency you want to exchange from (e.g., USD, EUR): ").upper()
    target_currency = input("Enter the currency you want to exchange to (e.g., EUR, GBP, JPY): ")
    stop_price = input("Enter the stop price")
    amount = input("Enter the amount")
    while True:
        current_price = get_current_price(pair)
        if current_price >= stop_price:
            print(f"Execute the stop order")
        break


