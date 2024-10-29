import numpy as np
import yfinance as yf
import csv
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from forex_python.converter import CurrencyRates, CurrencyCodes

# Create an instance of CurrencyRates and CurrencyCodes
currency_rates = CurrencyRates()
currency_codes = CurrencyCodes()

#menu

def menu():
    print("Welcome to the Currency Converter!")
    print("How can I assist you today?")
    print("1. View current exchange rates")
    print("2. Convert an amount between currencies")
    print("3. Analyze historical data and receive signals")
    print("4. Place a stop order")
    print("5. Place a limit order")
    print("6. Save exchange rates to a CSV file")
    print("7. Exit the application")

def main():
    while True:
        menu()
        choice = input("Enter the number of your choice: ")

        if choice == '1':
            get_current_rates(base_currency, target_currencies)
        elif choice == '2':
            amount = float(input("Enter the amount you want to convert: "))
            to_currency = input("Enter the target currency: ").upper()
            convert_currency(amount, base_currency, to_currency)
        elif choice == '3':
            currency_pair = input("What currency pair do you want to analyze? ")
            data = get_forex_data(currency_pair)
            if data is not None:
                data['RSI'] = calculate_rsi(data)
                print(data[['Close', 'RSI']])
                if data['RSI'].iloc[-1] < 30:
                    print("Potential Buy Signal")
                elif data['RSI'].iloc[-1] > 70:
                    print("Potential Sell Signal")
                else:
                    print("No clear signal")
        elif choice == '4':
            currency_pair = input("Enter the currency pair for the stop order: ")
            stop_order(currency_pair)
        elif choice == '5':
            currency_pair = input("Enter the currency pair for the limit order: ")
            limit_order(currency_pair)
        elif choice == '6':
            current_rates = get_current_rates(base_currency, target_currencies)
            save_data_to_csv(current_rates)
        elif choice == '7':
            print("Thank you for using the Currency Converter! Goodbye!")
        else:
            print ("please try again, invalid choice. Input the number 1-7")
main()            
# 1. Ask for the currencies
base_currency = input("Enter the currency you want to exchange from (e.g., USD, EUR): ").upper()
target_currencies_input = input("Enter the currencies you want to exchange to (e.g., EUR, GBP, JPY): ") #ERROR Failed to retrieve data for USD: Expecting value: line 1 column 1 (char 0)

# Split the input string into a list; iterate over each element; eliminate whitespace
target_currencies_list = target_currencies_input.split(',')
target_currencies = [currency.strip().upper() for currency in target_currencies_list]
print(target_currencies)

# Get the exchange rate
def get_current_rates(base_currency, target_currencies):
    print(f"Current exchange rates for {base_currency}:")
    rates = {}
    for currency in target_currencies:
        try:
            rate = currency_rates.get_rate(base_currency, currency)
            rates[currency] = rate
            print(f"{base_currency} to {currency}: {rate}")
        except Exception as e:
            print(f"Failed to retrieve data for {currency}: {e}")
    return rates

current_rates = get_current_rates(base_currency, target_currencies)

# 2. Convert the amount
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
        print(f"The latest rate is above the average rate. It might be a good time to exchange {pair[:3]} to {pair[3:]} now.")
    elif latest_rate < average_rate:
        print(f"The latest rate is below the average rate. It might be better to wait before exchanging {pair[:3]} to {pair[3:]}.")
    else:
        print(f"The latest rate is equal to the average rate. {pair[:3]} to {pair[3:]}.")

    # Plot a chart showing the rates
    plt.plot(close_prices.index, close_prices.values)
    plt.title(f'Exchange Rate Trend for {pair} over Last {days} Days')
    plt.xlabel('Date')
    plt.ylabel('Exchange Rate')
    plt.show()

# RSI
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
    print("RSI is a momentum oscillator that measures the speed and change of price movements.It ranges from 0 to 100 and is typically used to identify overbought or oversold conditions.An RSI below 30 is considered oversold (potential buy signal), while an RSI above 70 is considered overbought (potential sell signal).An RSI around 50 indicates a neutral market.")

def get_forex_data(pair, days=30):
    data = yf.download(pair, period=f'{days}d', interval='1d')
    if data.empty:
        print(f"No data available for {pair}.")
        return None
    return data

# Example usage
currency_pair = input("what currency pair do you want to analyse ") #ERROR
#No data available for USDEUR.
#[*********************100%***********************]  1 of 1 completed

#1 Failed download:
#['USDEUR']: YFPricesMissingError('$%ticker%: possibly delisted; no price data found  (period=30d) (Yahoo error = "No data found, symbol may be delisted")')

data = get_forex_data(currency_pair)

if data is not None:
    data['RSI'] = calculate_rsi(data)
    print(data[['Close', 'RSI']])

    # Generating signals based on RSI
    if data['RSI'].iloc[-1] < 30:
        print("Potential Buy Signal")
    elif data['RSI'].iloc[-1] > 70:
        print("Potential Sell Signal")
    else:
        print("No clear signal")

# Analyze currency trend

def get_current_price(pair):
    data = yf.download(pair, period='1d', interval='1m')
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
#limit order loop
def limit_order (pair, limit_price, amount):
# ask for the ccy and stop price and amount
    base_currency = input("Enter the currency you want to exchange from (e.g., USD, EUR): ").upper()
    target_currency = input("Enter the currency you want to exchange to (e.g., EUR, GBP, JPY): ")
    limit_price = input("Enter the limit price")
    amount = input("Enter the amount")
    while True:
        current_price = get_current_price(pair)
        if limit_price <= current_price:
            print (f" Execute the limit order")
        break

# Save data to CSV
def save_data_to_csv(data, filename='exchange_rates.csv'):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Currency Pair', 'Rate'])
        for currency, rate in data.items():
            writer.writerow([f"{base_currency} to {currency}", rate])
    print(f"Data saved to {filename}")

# Plot data to chart function
def plot_data_to_chart(data):
    plt.plot(data)
