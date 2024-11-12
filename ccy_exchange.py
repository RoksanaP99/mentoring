import requests
import matplotlib.pyplot as plt
import csv
from datetime import datetime, timedelta
import pandas as pd

API_URL = "https://api.frankfurter.app"

def get_available_currencies():
    response = requests.get(f"{API_URL}/currencies")
    if response.status_code == 200:
        return response.json()
    else:
        print("Error retrieving available currencies.")
        return {}

base_currency = input("Enter the currency you want to exchange from (e.g., USD, EUR): ").upper()
target_currencies_input = input("Enter the currencies you want to exchange to (e.g., EUR, GBP, JPY): ")
target_currencies = [currency.strip().upper() for currency in target_currencies_input.split(',')]

#indirect ccy
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
#get ccy rates
def get_current_rates(base_currency, target_currencies, indirect_currency="USD"):
    rates = {}
    print(f"Current exchange rates for {base_currency}:")
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

#convert

def convert_currency(amount, from_currency, to_currency, rates):
    rate = rates.get(to_currency)
    if rate:
        converted_amount = amount * rate
        print(f"{amount} {from_currency} is equal to {converted_amount:.2f} {to_currency}")
        return converted_amount
    else:
        print(f"No conversion rate available for {to_currency}.")
        return None

#trend

import matplotlib.pyplot as plt

def analyze_currency_trend(pair, days=30):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    response = requests.get(f"{API_URL}/{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}",
                            params={"from": pair[:3], "to": pair[3:]})
    data = response.json().get('rates', {})

    if not data:
        print(f"No data available for {pair}.")
        return None

    # Extract date and closing price
    dates = []
    close_prices = []
    for date, rate in sorted(data.items()):
        dates.append(date)
        close_prices.append(rate[pair[3:]])

    # Convert close_prices to pandas Series
    close_prices = pd.Series(close_prices)

    # Convert dates to pandas DatetimeIndex
    dates = pd.to_datetime(dates)

    # Now you can use iloc for indexing
    latest_rate = close_prices.iloc[-1]
    average_rate = close_prices.mean()

    print(f"Start rate: {close_prices.iloc[0]}, Latest rate: {latest_rate}")

    if latest_rate > average_rate:
        print(f"The latest rate is above the average rate. Might be a good time to exchange {pair[:3]} to {pair[3:]}.")
    elif latest_rate < average_rate:
        print(
            f"The latest rate is below the average rate. Might be better to wait before exchanging {pair[:3]} to {pair[3:]}.")
    else:
        print(f"The latest rate equals the average rate for {pair[:3]} to {pair[3:]}.")

    # Plotting the trend
    plt.plot(dates, close_prices, label=f"{pair} Close Price")
    plt.axhline(y=average_rate, color="r", linestyle="--", label="Average Rate")
    plt.title(f'Exchange Rate Trend for {pair} over Last {days} Days')
    plt.xlabel('Date')
    plt.ylabel('Exchange Rate')
    plt.legend()
    plt.show()

#csv
def save_rates_to_csv(rates, base_currency):
    filename = f"{base_currency}_exchange_rates.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Currency", "Rate"])
        for currency, rate in rates.items():
            writer.writerow([currency, rate])
    print(f"Exchange rates saved to {filename}")


def get_current_price(pair):
    """
    Retrieves the current price of the specified currency pair using the Frankfurter API.
    :param pair: String representing the currency pair (e.g., "USDGBP").
    :return: Latest exchange rate or None if data is unavailable.
    """
    base_currency = pair[:3]  # Extract the base currency (e.g., "USD" from "USDGBP")
    target_currency = pair[3:]  # Extract the target currency (e.g., "GBP" from "USDGBP")

    try:
        # Fetch the latest price for the base to target currency pair
        response = requests.get(f"{API_URL}/latest", params={"from": base_currency, "to": target_currency})
        response.raise_for_status()
        rate = response.json().get("rates", {}).get(target_currency)

        if rate:
            return rate
        else:
            print(f"No current price data available for {pair}.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching current price for {pair}: {e}")
        return None
# Stop order
def stop_order(pair, stop_price, amount):
    stop_price = float(stop_price)
    amount = float(amount)
    while True:
        current_price = get_current_price(pair)
        if current_price and current_price >= stop_price:
            print(f"Executing stop order at {current_price} for {amount} units.")
            break

# Limit order
def limit_order(pair, limit_price, amount):
    limit_price = float(limit_price)
    amount = float(amount)
    while True:
        current_price = get_current_price(pair)
        if current_price and current_price <= limit_price:
            print(f"Executing limit order at {current_price} for {amount} units.")
            break

# Menu

def menu():
    print("Welcome to the Currency Converter!")
    print("1. View current exchange rates")
    print("2. Convert an amount between currencies")
    print("3. Analyze historical data and receive signals")
    print("4. Save exchange rates to a CSV file")
    print("5. Exit")

def main():
    while True:
        menu()
        choice = input("Enter the number of your choice: ")

        if choice == '1':
            rates = get_current_rates(base_currency, target_currencies)
        elif choice == '2':
            amount = float(input("Enter the amount you want to convert: "))
            to_currency = input("Enter the target currency: ").upper()
            convert_currency(amount, base_currency, to_currency, rates)
        elif choice == '3':
            currency_pair = input("What currency pair do you want to analyze? (e.g., USDGBP) ")
            analyze_currency_trend(currency_pair)
        elif choice == '4':
            rates = get_current_rates(base_currency, target_currencies)
            save_rates_to_csv(rates, base_currency)
        elif choice == '5':
            print("Thank you for using the Currency Converter! Goodbye!")
            break
        else:
            print("Please try again, invalid choice. Input the number 1-5.")

main()

