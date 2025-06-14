# tasks/finance/currency.py
import requests
from datetime import datetime

def get_exchange_rate(from_currency, to_currency):
    # Using a free API for exchange rates
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}"
        response = requests.get(url)
        data = response.json()
        
        if 'rates' in data and to_currency.upper() in data['rates']:
            return data['rates'][to_currency.upper()]
        else:
            print(f"Could not find exchange rate for {from_currency} to {to_currency}")
            return None
            
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return None

def convert_currency(amount, from_currency, to_currency):
    rate = get_exchange_rate(from_currency, to_currency)
    
    if rate is not None:
        converted_amount = amount * rate
        print(f"{amount} {from_currency.upper()} = {converted_amount:.2f} {to_currency.upper()}")
        print(f"Exchange rate: 1 {from_currency.upper()} = {rate:.4f} {to_currency.upper()}")
        print(f"(Rate as of {datetime.now().strftime('%Y-%m-%d')})")
        return converted_amount
    return None

def list_common_currencies():
    common_currencies = [
        ("USD", "US Dollar"),
        ("EUR", "Euro"),
        ("GBP", "British Pound"),
        ("JPY", "Japanese Yen"),
        ("CAD", "Canadian Dollar"),
        ("AUD", "Australian Dollar"),
        ("INR", "Indian Rupee"),
        ("CNY", "Chinese Yuan"),
        ("BRL", "Brazilian Real"),
        ("ZAR", "South African Rand")
    ]
    
    print("\nCommon Currencies:")
    for code, name in common_currencies:
        print(f"{code} - {name}")