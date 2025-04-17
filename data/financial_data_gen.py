#!/usr/bin/env python3
# Financial Transaction Dataset Generator with 4 CSV files

import csv
import random
import datetime
import string
import os
from typing import List, Dict, Any, Optional, Union

# Configuration
BASE_NUM_RECORDS = 1000  # Base number of records for first file
ADDITIONAL_RECORDS_PER_FILE = 250  # New records per additional file
UPDATE_PERCENTAGE = 30  # Percentage of records to update in subsequent files
ERROR_RATE = 0.05  # 5% of records will have some issue

# Output files with timestamps
current_time = datetime.datetime.now()
file_1a_time = current_time - datetime.timedelta(days=8)
file_1b_time = current_time - datetime.timedelta(days=7)
file_2_time = current_time - datetime.timedelta(days=3)
file_3_time = current_time

OUTPUT_FILES = [
    f'financial_transactions_{file_1a_time.strftime("%Y%m%d_%H%M%S")}.csv',
    f'financial_transactions_{file_1b_time.strftime("%Y%m%d_%H%M%S")}.csv',
    f'financial_transactions_{file_2_time.strftime("%Y%m%d_%H%M%S")}.csv',
    f'financial_transactions_{file_3_time.strftime("%Y%m%d_%H%M%S")}.csv'
]

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

def generate_initial_data():
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
    
    # Generate the base set of transactions
    transactions = []
    all_transaction_ids = []
    
    # Generate records for first file
    for i in range(BASE_NUM_RECORDS):
        transaction_id = f"TXN{str(i + 1).zfill(8)}"
        all_transaction_ids.append(transaction_id)
        
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
    
    return header, transactions, all_transaction_ids, account_balances, accounts, customer_ids

def generate_subsequent_files(header, initial_transactions, all_transaction_ids, account_balances, accounts, customer_ids, file_index):
    """Generate data for subsequent files with updates and new records"""
    
    # Make a deep copy of initial transactions
    transactions = [record.copy() for record in initial_transactions]
    
    # Determine how many records to update
    num_updates = int(len(transactions) * (UPDATE_PERCENTAGE / 100))
    
    # Update existing transactions
    update_indices = random.sample(range(len(transactions)), num_updates)
    
    # Date range for new transactions - extend beyond the original date range for newer files
    end_date_offset = file_index * 15  # Each file extends the date range by 15 days
    start_date = datetime.datetime(2023, 12, 31) + datetime.timedelta(days=1)
    end_date = datetime.datetime(2024, 1, 15) + datetime.timedelta(days=end_date_offset)
    
    # Update selected transactions
    for idx in update_indices:
        # Determine what to update
        update_type = random.random()
        
        # Get the transaction
        transaction = transactions[idx]
        transaction_id = transaction['transaction_id']
        
        # Handle corrupted transaction IDs and skip if we can't identify it
        if transaction_id is None or transaction_id == "":
            continue
            
        # Clean transaction ID if it was corrupted
        if transaction_id not in all_transaction_ids:
            # Try to clean it up
            for tid in all_transaction_ids:
                if tid in str(transaction_id):
                    transaction_id = tid
                    break
            if transaction_id not in all_transaction_ids:
                continue
        
        if update_type < 0.4:
            # Update status
            new_status = random_choice(STATUSES)
            while new_status == transaction['status']:
                new_status = random_choice(STATUSES)
            transaction['status'] = maybe_corrupt(new_status, ERROR_RATE)
            
        elif update_type < 0.8:
            # Update amount and recalculate balance
            account_number = transaction['account_number']
            
            # Handle corrupted account numbers
            if account_number is None or account_number == "":
                continue
                
            original_amount = transaction['amount']
            if isinstance(original_amount, str) and not original_amount.replace('-', '').replace('.', '').isdigit():
                continue  # Skip if amount is corrupted and not convertible
                
            try:
                # Try to convert back to float
                if isinstance(original_amount, str):
                    original_amount = float(original_amount.replace('x', ''))
                
                # Get the current balance
                if account_number in account_balances:
                    # Adjust the balance by removing the old amount
                    account_balances[account_number] -= original_amount
                    
                    # Calculate new amount with a slight change
                    new_amount = original_amount * (0.8 + random.random() * 0.4)  # 80-120% of original
                    transaction['amount'] = maybe_corrupt(round(new_amount, 2), ERROR_RATE)
                    
                    # Update the balance
                    try:
                        current_amount = transaction['amount']
                        if isinstance(current_amount, str):
                            current_amount = float(current_amount.replace('x', ''))
                        account_balances[account_number] += current_amount
                        transaction['balance_after'] = maybe_corrupt(round(account_balances[account_number], 2), ERROR_RATE)
                    except:
                        # If conversion fails, just leave it
                        pass
            except:
                # If something goes wrong, just leave it
                pass
                
        else:
            # Update timestamp to be more recent
            new_date = random_date(start_date, end_date)
            transaction['timestamp'] = maybe_corrupt(format_date(new_date), ERROR_RATE)
    
    # Add new transactions
    next_id_num = len(all_transaction_ids) + 1
    
    for i in range(ADDITIONAL_RECORDS_PER_FILE):
        transaction_id = f"TXN{str(next_id_num + i).zfill(8)}"
        all_transaction_ids.append(transaction_id)
        
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
        current_balance = account_balances.get(account_number, 1000 + random.random() * 9000)
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
            'merchant': maybe_corrupt(merchant, ERROR_RATE * 1.5),
            'category': maybe_corrupt(category, ERROR_RATE * 1.5),
            'location': maybe_corrupt(location, ERROR_RATE * 1.5)
        }
        
        transactions.append(record)
    
    return header, transactions, all_transaction_ids, account_balances

def main():
    # Set random seed for reproducibility
    random.seed(42)
    
    # Generate initial data
    header, initial_transactions, all_transaction_ids, account_balances, accounts, customer_ids = generate_initial_data()
    
    # Create directory for output files if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILES[0]) if os.path.dirname(OUTPUT_FILES[0]) else '.', exist_ok=True)
    
    # Split the first file's data into two parts
    split_point = len(initial_transactions) // 2
    first_half = initial_transactions[:split_point]
    second_half = initial_transactions[split_point:]
    
    # Write first part
    with open(OUTPUT_FILES[0], 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        for transaction in first_half:
            writer.writerow(transaction)
            
    # Write second part
    with open(OUTPUT_FILES[1], 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        for transaction in second_half:
            writer.writerow(transaction)
    
    # For each subsequent file
    current_transactions = initial_transactions
    
    for i in range(2, len(OUTPUT_FILES)):
        # Generate updated data
        header, current_transactions, all_transaction_ids, account_balances = generate_subsequent_files(
            header, current_transactions, all_transaction_ids, account_balances, accounts, customer_ids, i-1
        )
        
        # Write to file
        with open(OUTPUT_FILES[i], 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            for transaction in current_transactions:
                writer.writerow(transaction)
    
    print(f"Generated {len(initial_transactions)} initial financial transactions split across two files.")
    print(f"Added approximately {ADDITIONAL_RECORDS_PER_FILE} new transactions in each subsequent file.")
    print(f"Updated approximately {UPDATE_PERCENTAGE}% of records in each subsequent file.")
    print("Files generated:")
    for file in OUTPUT_FILES:
        print(f"- {file}")

if __name__ == "__main__":
    main()