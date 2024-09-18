# actions.py
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from datetime import datetime
import pandas as pd
import re
from dateutil.relativedelta import relativedelta
import logging
logging.basicConfig(level=logging.INFO)


months = { 'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3, 'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7, 'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'sept': 9, 'october': 10, 'oct': 10, 'november': 11, 'nov': 11, 'december': 12, 'dec': 12 }
months_reverse = {v: k for k, v in months.items()}
word_to_num = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12
}

def extract_months_from_text(text):
    # Regular expression to match numbers or words like '5', 'five', etc.
    pattern = r'\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+months?\b'
    
    # Search for the number of months in the text
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        # Extract the matched part
        month_str = match.group(1).lower()
        
        # Convert word-based numbers to digits, or just use the digit if it's already a number
        if month_str.isdigit():
            return int(month_str)
        else:
            return word_to_num.get(month_str, 0)  # Convert word to number, default to 0 if not found
    return 0

def get_month_range_from_text(text):
    # Extract the number of months
    num_months = extract_months_from_text(text)
    
    if num_months > 0:
        # Get the current date
        current_date = datetime.now()
        
        # Calculate the date X months ago
        past_date = current_date - relativedelta(months=num_months)
        
        # Return the range of months (past month/year to current month/year)
        month_range = [[past_date.month, past_date.year], [current_date.month, current_date.year]]
        return month_range, num_months
    else:
        return None
    

def extract_months(text):
    # Regular expression to find month names or abbreviations (case-insensitive)
    pattern = r'\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b'
    
    # Find all matches of month names (case-insensitive)
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    # Convert matched month names to corresponding digits
    month_digits = [months[match.lower()] for match in matches]
    
    return month_digits

def extract_years(text):
    # Regular expression to match years in YYYY format without capturing the century separately
    pattern = r'\b(?:19|20)\d{2}\b'
    
    # Find all matches of the pattern
    years = re.findall(pattern, text)
    
    return [int(year) for year in years]


def extract_month_year(text):    
    pattern = r'\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s*(?:of\s*)?(\d{4})\b'
    
    # Find all matches of the pattern (month and year)
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    # Convert matched month names to corresponding digits and pair them with the year as arrays
    month_year_pairs = [[months[month.lower()], int(year)] for month, year in matches]
    
    return month_year_pairs


class ActionMultiplyNumbers(Action):

    def name(self) -> Text:
        return "action_multiply_numbers"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extracting the numbers from the user's message
        user_message = tracker.latest_message.get('text')
        
        # Assuming the format is always "Add these numbers X and Y"
        numbers = [int(num) for num in user_message.split() if num.isdigit()]

        if len(numbers) == 2:
            result = numbers[0] * numbers[1]
            dispatcher.utter_message(text=f"The result of multiplying {numbers[0]} and {numbers[1]} is {result}.")
        else:
            dispatcher.utter_message(text="I couldn't find two numbers to multiply.")

        return []


class ActionGetCurrentTimeDate(Action):

    def name(self) -> Text:
        return "action_get_current_time_date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get current date and time
        now = datetime.now()

        # Format day, month, year, and time
        day = now.day
        month = now.strftime("%B")  # Full month name
        year = now.year
        time = now.strftime("%H:%M")  # Format HH:MM

        # Create a formatted response
        dispatcher.utter_message(text=f"Today is {day}th {month} {year}, time is {time}.")

        return []

class ActionGetTotalSales(Action):

    def name(self) -> Text:
        return "action_get_total_sales"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            logging.info("Loading sales data from Excel file...")
            df = pd.read_excel('airhub_data.xlsx')
            logging.info("Sales data loaded successfully.")
        except FileNotFoundError:
            dispatcher.utter_message(text="The sales data file could not be found.")
            return []
        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred while loading the sales data: {str(e)}")
            return []

        df['PurchaseDate'] = pd.to_datetime(df['PurchaseDate'], errors='coerce')
        df['SellingPrice'] = pd.to_numeric(df['SellingPrice'], errors='coerce')

        if df.empty or df['SellingPrice'].isnull().all():
            dispatcher.utter_message(text="The sales data is empty or invalid.")
            return []

        user_message = tracker.latest_message.get('text')
        
        # Check for last X months request
        if "last" in user_message and "month" in user_message:
            logging.info("Processing request for total sales over last months...")
            month_range_info = get_month_range_from_text(user_message)
            month_range, num_months = month_range_info

            if num_months:
                start_month, start_year = month_range[0]
                end_month, end_year = month_range[1]
                logging.info("Executing...",num_months)
                total_sales = df[((df['PurchaseDate'].dt.year == start_year) & (df['PurchaseDate'].dt.month >= start_month)) | ((df['PurchaseDate'].dt.year == end_year) & (df['PurchaseDate'].dt.month <= end_month)) |      # Sales in end year before end month
                ((df['PurchaseDate'].dt.year > start_year) & (df['PurchaseDate'].dt.year < end_year))]['SellingPrice'].sum()
                dispatcher.utter_message(text=f"The total sales for the last {num_months} months is {total_sales:.2f}.")
                return []

        # Extract years and months from user input for other cases
        years = extract_years(user_message)
        months_extracted = extract_months(user_message)
        month_year_pairs = extract_month_year(user_message)

        total_sales = 0.0

        # If both months and years are mentioned
        if month_year_pairs:
            logging.info("Calculating total sales for specified months and years...")
            for month, year in month_year_pairs:
                monthly_sales = df[(df['PurchaseDate'].dt.month == month) & (df['PurchaseDate'].dt.year == year)]['SellingPrice'].sum()
                total_sales += monthly_sales
                dispatcher.utter_message(text=f"The total sales for {months_reverse[month]} {year} is {monthly_sales:.2f}.")
        
        # If only years are mentioned
        elif years:
            logging.info("Calculating total sales for specified years...")
            total_sales = df[df['PurchaseDate'].dt.year.isin(years)]['SellingPrice'].sum()
            if len(years) == 1:
                year = years[0]
                dispatcher.utter_message(text=f"The total sales for {year} is {total_sales:.2f}.")
            else:
                years_str = ', '.join(map(str, years))
                dispatcher.utter_message(text=f"Overall sales for {years_str} is {total_sales:.2f}.")

        # If only months are mentioned (without specific year)
        elif months_extracted:
            logging.info("Calculating total sales for specified months without a year...")
            current_year = pd.to_datetime('today').year  
            for month in months_extracted:
                monthly_sales = df[(df['PurchaseDate'].dt.month == month) & (df['PurchaseDate'].dt.year == current_year)]['SellingPrice'].sum()
                total_sales += monthly_sales
                dispatcher.utter_message(text=f"The total sales for {months_reverse[month]} {current_year} is {monthly_sales:.2f}.")
        
        else:
            dispatcher.utter_message(text="I couldn't find any valid year or month in your request.")
            return []

        return []