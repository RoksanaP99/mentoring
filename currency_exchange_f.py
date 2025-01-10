import requests
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv
from datetime import datetime, timedelta

API_URL = "https://api.frankfurter.app"

# Function to fetch available currencies
def get_available_currencies():
    response = requests.get(f"{API_URL}/currencies")
    if response.status_code == 200:
        return response.json()
    else:
        print("Error retrieving available currencies.")
        return {}

# Function to fetch exchange rates, including indirect ones
def get_exchange_rate(indirect_currency, source_currency, target_currency):
    try:
        response1 = requests.get(f"{API_URL}/latest", params={"from": source_currency, "to": indirect_currency})
        rate1 = response1.json().get('rates', {}).get(indirect_currency)

        response2 = requests.get(f"{API_URL}/latest", params={"from": indirect_currency, "to": target_currency})
        rate2 = response2.json().get('rates', {}).get(target_currency)

        if rate1 and rate2:
            return rate2 / rate1
    except Exception as e:
        print(f"Error retrieving indirect rate for {source_currency} to {target_currency}: {e}")
    return None

# Function to get current rates
def get_current_rates(base_currency, target_currencies, indirect_currency="USD"):
    rates = {}
    print(f"\nFetching current exchange rates for {base_currency}...")
    for currency in target_currencies:
        try:
            response = requests.get(f"{API_URL}/latest", params={"from": base_currency, "to": currency})
            response.raise_for_status()
            rate = response.json().get('rates', {}).get(currency)
            if rate:
                rates[currency] = rate
                print(f"{base_currency} to {currency}: {rate}")
            else:
                rate = get_exchange_rate(indirect_currency, base_currency, currency)
                if rate:
                    rates[currency] = rate
                    print(f"{base_currency} to {currency} (via {indirect_currency}): {rate}")
        except Exception as e:
            print(f"Failed to retrieve data for {currency}: {e}")
    return rates

# Function to convert currency
def convert_currency(amount, from_currency, to_currency, rates):
    rate = rates.get(to_currency)
    if rate:
        converted_amount = amount * rate
        print(f"{amount} {from_currency} is equal to {converted_amount:.2f} {to_currency}")
        return converted_amount
    else:
        print(f"No conversion rate available for {to_currency}.")
        return None

# RSI Calculation
def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = np.maximum(delta, 0)
    loss = -np.minimum(delta, 0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Moving Averages Calculation
def calculate_moving_averages(data, window_sma=20, window_ema=20):
    sma = data.rolling(window=window_sma).mean()
    ema = data.ewm(span=window_ema, adjust=False).mean()
    return sma, ema

# Historical Data and Analysis
def analyze_currency_trend(pair, days=30):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    response = requests.get(f"{API_URL}/{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}",
                            params={"from": pair[:3], "to": pair[3:]})
    data = response.json().get('rates', {})

    if not data:
        print(f"No data available for {pair}.")
        return None

    dates = pd.to_datetime(list(data.keys()))
    rates = pd.Series([rate[pair[3:]] for rate in data.values()], index=dates, name="Exchange Rate")

    rates_rsi = calculate_rsi(rates)
    sma, ema = calculate_moving_averages(rates)

    print(f"Start rate: {rates.iloc[0]:.2f}, Latest rate: {rates.iloc[-1]:.2f}")
    print(f"RSI: {rates_rsi.iloc[-1]:.2f} (Below 30: Oversold, Above 70: Overbought)")

    if rates_rsi.iloc[-1] < 30:
        print("Potential Buy Signal: RSI indicates the currency is oversold.")
    elif rates_rsi.iloc[-1] > 70:
        print("Potential Sell Signal: RSI indicates the currency is overbought.")
    else:
        print("No clear signal from RSI.")

    plt.figure(figsize=(12, 8))
    plt.plot(rates, label=f'{pair} Exchange Rate', color='blue')
    plt.plot(sma, label='Simple Moving Average (20)', color='green', linestyle='--')
    plt.plot(ema, label='Exponential Moving Average (20)', color='orange', linestyle='--')
    plt.axhline(rates.mean(), color='red', linestyle=':', label='Mean Exchange Rate')
    plt.title(f'{pair} Exchange Rate Analysis')
    plt.xlabel('Date')
    plt.ylabel('Exchange Rate')
    plt.legend()
    plt.show()

    plt.figure(figsize=(12, 6))
    plt.plot(rates_rsi, label='RSI', color='purple')
    plt.axhline(70, color='red', linestyle='--', label='Overbought (70)')
    plt.axhline(30, color='green', linestyle='--', label='Oversold (30)')
    plt.title(f'{pair} RSI Indicator')
    plt.xlabel('Date')
    plt.ylabel('RSI')
    plt.legend()
    plt.show()

# menu
def main():
    base_currency = input("Enter the currency you want to exchange from (e.g., USD, EUR): ").upper()
    target_currencies_input = input("Enter the currencies you want to exchange to (e.g., EUR, GBP, JPY): ")
    target_currencies = [currency.strip().upper() for currency in target_currencies_input.split(',')]

    rates = {}
    while True:
        print("\nMenu:")
        print("1. View current exchange rates")
        print("2. Convert an amount between currencies")
        print("3. Analyze historical data and receive signals (RSI, MA)")
        print("4. Save exchange rates to a CSV file")
        print("5. Exit")

        choice = input("Enter the number of your choice: ")

        if choice == '1':
            rates = get_current_rates(base_currency, target_currencies)
        elif choice == '2':
            amount = float(input("Enter the amount you want to convert: "))
            to_currency = input("Enter the target currency: ").upper()
            convert_currency(amount, base_currency, to_currency, rates)
        elif choice == '3':
            currency_pair = input("What currency pair do you want to analyze? (e.g., USDGBP) ").upper()
            days = int(input("Enter the number of days for analysis (e.g., 30, 60, 90): "))
            analyze_currency_trend(currency_pair, days)
        elif choice == '4':
            rates = get_current_rates(base_currency, target_currencies)
            filename = f"{base_currency}_exchange_rates.csv"
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Currency", "Rate"])
                for currency, rate in rates.items():
                    writer.writerow([currency, rate])
            print(f"Exchange rates saved to {filename}")
        elif choice == '5':
            print("Thank you for using the Currency Converter! Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

main()
