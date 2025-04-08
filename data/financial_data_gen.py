#!/usr/bin/env python3
# Financial Transaction Dataset Generator with Realistic Data Issues

import csv
import random
import datetime
import string
from typing import List, Dict, Any, Optional, Union

# Configuration
NUM_RECORDS = 1500
OUTPUT_FILE = 'financial_transactions.csv'
ERROR_RATE = 0.05  # 5% of records will have some issue

# Transaction types
TRANSACTION_TYPES = ['deposit', 'withdrawal', 'transfer', 'payment', 'refund', 'fee', 'interest']

# Categories
CATEGORIES = [
    'groceries', 'dining', 'entertainment', 'utilities', 'housing', 'transportation',
    'healthcare', 'education', 'shopping', 'travel', 'charity', 'income', 'investment',
    'savings', 'insurance', 'taxes', 'miscellaneous'
]

# Currencies (predominantly USD with some international transactions)
CURRENCIES = ['USD', 'USD', 'USD', 'USD', 'USD', 'EUR', 'GBP', 'CAD', 'JPY', 'AUD']

# Status options
STATUSES = ['completed', 'pending', 'failed', 'disputed', 'reversed']

# Merchants (some common ones, plus some generic)
MERCHANTS = [
    'Amazon', 'Walmart', 'Target', 'Costco', 'Whole Foods', 'Uber', 'Uber Eats', 
    'DoorDash', 'Spotify', 'Netflix', 'AT&T', 'Verizon', 'Comcast', 'PG&E',
    'Chevron', 'Shell', 'CVS', 'Walgreens', 'Starbucks', 'McDonalds',
    'Home Depot', 'Lowes', 'Apple', 'Best Buy', 'Direct Deposit - Employer',
    'Venmo', 'PayPal', 'Zelle', 'Chase', 'Bank of America', 'Wells Fargo',
    'American Express', 'Visa', 'Mastercard', 'Southwest Airlines',
    'Delta Airlines', 'Airbnb', 'Hilton Hotels', 'Marriott Hotels'
]

# Locations/Branches
LOCATIONS = [
    'New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX', 'Phoenix, AZ',
    'Philadelphia, PA', 'San Antonio, TX', 'San Diego, CA', 'Dallas, TX', 'San Jose, CA',
    'Austin, TX', 'Jacksonville, FL', 'Fort Worth, TX', 'Columbus, OH', 'Charlotte, NC',
    'San Francisco, CA', 'Indianapolis, IN', 'Seattle, WA', 'Denver, CO', 'Boston, MA',
    'Online', 'Mobile App', 'ATM', 'Phone Banking', 'Branch'
]

# Helper functions
def random_choice(arr):
    return random.choice(arr)

def random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_days = random.randrange(days_between_dates)
    random_seconds = random.randrange(86400)  # Seconds in a day
    return start_date + datetime.timedelta(days=random_days, seconds=random_seconds)

def format_date(date):
    return date.strftime("%Y-%m-%d %H:%M:%S")

# Function to introduce errors based on error rate
def maybe_corrupt(value, error_rate):
    if random.random() < error_rate:
        error_type = random.random()
        
        if error_type < 0.3:
            # Return None or empty
            return None if random.random() < 0.5 else ""
        
        elif error_type < 0.6 and isinstance(value, str) and value:
            # Typo/corruption for string values
            pos = random.randint(0, len(value) - 1)
            return value[:pos] + random.choice(string.ascii_lowercase) + value[min(pos + 1, len(value)):]
        
        elif error_type < 0.8:
            # Wrong data type
            if isinstance(value, (int, float)):
                return str(value)  # Convert to string
            elif isinstance(value, str) and value.replace('.', '', 1).isdigit():
                return value + 'x'  # Add non-numeric character
        
        else:
            # Extreme value for numbers
            if isinstance(value, (int, float)):
                return value * 1000 if random.random() < 0.5 else -value
    
    return value

def generate_transactions():
    # Generate customer IDs (200 unique customers)
    customer_ids = [f"CUST{str(i + 1001).zfill(6)}" for i in range(200)]
    
    # Generate account numbers
    def generate_account_number():
        return f"ACCT-{random.randint(10000000, 99999999)}"
    
    # Generate accounts (some customers will have multiple accounts)
    accounts = {}
    for cust_id in customer_ids:
        num_accounts = 1 if random.random() < 0.5 else (2 if random.random() < 0.8 else 3)
        accounts[cust_id] = [generate_account_number() for _ in range(num_accounts)]
    
    # Track balances for each account
    account_balances = {}
    
    # Helper to get or initialize balance
    def get_balance(account_number):
        if account_number not in account_balances:
            # Initialize with random balance between $1000 and $10000
            account_balances[account_number] = 1000 + random.random() * 9000
        return account_balances[account_number]
    
    # Date range for transactions
    start_date = datetime.datetime(2023, 1, 1)
    end_date = datetime.datetime(2023, 12, 31)
    
    # Create header and transactions
    header = [
        'transaction_id',
        'timestamp',
        'customer_id',
        'account_number',
        'transaction_type',
        'amount',
        'currency',
        'balance_after',
        'status',
        'merchant',
        'category',
        'location'
    ]
    
    transactions = []
    
    # Generate records
    for i in range(NUM_RECORDS):
        transaction_id = f"TXN{str(i + 1).zfill(8)}"
        date = random_date(start_date, end_date)
        customer_id = random_choice(customer_ids)
        account_number = random_choice(accounts[customer_id])
        transaction_type = random_choice(TRANSACTION_TYPES)
        
        # Determine amount based on transaction type
        if transaction_type in ['deposit', 'refund', 'interest']:
            amount = round(random.random() * 2000 + 10, 2)
        elif transaction_type in ['withdrawal', 'payment', 'transfer']:
            amount = round((-random.random() * 1000 - 10), 2)
        elif transaction_type == 'fee':
            amount = round((-random.random() * 50 - 1), 2)
        else:
            amount = round(random.random() * 1000 * (1 if random.random() < 0.5 else -1), 2)
        
        currency = random_choice(CURRENCIES)
        
        # Update balance
        current_balance = get_balance(account_number)
        current_balance += amount
        account_balances[account_number] = current_balance
        
        status = random_choice(STATUSES)
        
        # Choose appropriate merchant based on transaction type
        merchant = None
        category = None
        
        if transaction_type in ['payment', 'refund']:
            merchant = random_choice(MERCHANTS)
            category = random_choice(CATEGORIES)
        elif transaction_type == 'deposit' and random.random() < 0.7:
            merchant = 'Direct Deposit - Employer'
            category = 'income'
        elif transaction_type == 'fee':
            merchant = random_choice(['Chase', 'Bank of America', 'Wells Fargo'])
            category = 'fees'
        
        location = random_choice(LOCATIONS)
        
        # Create record with potential errors
        record = {
            'transaction_id': maybe_corrupt(transaction_id, ERROR_RATE),
            'timestamp': maybe_corrupt(format_date(date), ERROR_RATE),
            'customer_id': maybe_corrupt(customer_id, ERROR_RATE),
            'account_number': maybe_corrupt(account_number, ERROR_RATE),
            'transaction_type': maybe_corrupt(transaction_type, ERROR_RATE),
            'amount': maybe_corrupt(amount, ERROR_RATE),
            'currency': maybe_corrupt(currency, ERROR_RATE),
            'balance_after': maybe_corrupt(round(current_balance, 2), ERROR_RATE),
            'status': maybe_corrupt(status, ERROR_RATE),
            'merchant': maybe_corrupt(merchant, ERROR_RATE * 1.5),  # Higher error rate for optional fields
            'category': maybe_corrupt(category, ERROR_RATE * 1.5),
            'location': maybe_corrupt(location, ERROR_RATE * 1.5)
        }
        
        transactions.append(record)
    
    return header, transactions

def main():
    header, transactions = generate_transactions()
    
    with open(OUTPUT_FILE, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        for transaction in transactions:
            writer.writerow(transaction)
    
    print(f"Generated {NUM_RECORDS} financial transactions with realistic data issues.")
    print(f"Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()