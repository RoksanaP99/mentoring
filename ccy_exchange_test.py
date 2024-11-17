
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
#Mocking With unittest.mock
import unittest
from unittest.mock import patch #patch decorator from unittest.mock to replace requests.get with a mock object
import requests
class TestGetAvailableCurrencies(unittest.TestCase):
    @patch('requests.get')  # Mock 'requests.get'
    def test_get_available_currencies_success(self, mock_get):
        # Arrange: Simulate a successful API response
        mock_get.return_value.status_code = 200  # Fake status code
        mock_get.return_value.json.return_value = {"PLN": "US Dollar", "EUR": "NOK"}
        result = get_available_currencies()
        self.assertEqual(result, {"PLN": "US Dollar", "EUR": "NOK"})
if __name__ == '__main__':
    unittest.main()