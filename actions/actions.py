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
from .utils import (
    calculate_total_and_average_sales,
    months,
    months_reverse,    
)

logging.info("Loading sales data from Excel file...")
df = pd.read_excel('cleaned_airhub_data.xlsx')
logging.info("Loaded data in dataframe...")

def format_sales_output(results):
    message_data=[]
    for entry in results:
        period, sales_data = entry
        total_sales = sales_data[0]
        average_sales = sales_data[1]
        
        # Format the output message
        message = f"The total sales of {period} is {total_sales:.2f}.\n"
        message += f"The average sale of {period} is {average_sales:.2f}."
        message_data.append(message)

    return message_data

class ActionGetTotalAndAverageSales(Action):

    def name(self) -> Text:
        return "action_get_total_and_average_sales"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            manipulated_df = df.copy()
            logging.info("Sales data loaded successfully.")
        except FileNotFoundError:
            dispatcher.utter_message(text="The sales data file could not be found.")
            return []
        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred while loading the sales data: {str(e)}")
            return []

        manipulated_df['PurchaseDate'] = pd.to_datetime(manipulated_df['PurchaseDate'], errors='coerce')
        manipulated_df['SellingPrice'] = pd.to_numeric(manipulated_df['SellingPrice'], errors='coerce')

        if manipulated_df.empty or manipulated_df['SellingPrice'].isnull().all():
            dispatcher.utter_message(text="The sales data is empty or invalid.")
            return []

        user_message = tracker.latest_message.get('text')

        total_sales = calculate_total_and_average_sales(manipulated_df, user_message)
        messages=format_sales_output(total_sales)
        if total_sales is not None:
            for data in messages:
                dispatcher.utter_message(text=data)
            # dispatcher.utter_message(text=f"The average sales is {average_sales:.2f}.")
        # logging.info(total_sales)

        return []
    
class ActionGetCountrySales(Action):

    def name(self) -> Text:
        return "action_get_country_sales"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            manipulated_df = df.copy()
            logging.info("Sales data loaded successfully.")
        except FileNotFoundError:
            dispatcher.utter_message(text="The sales data file could not be found.")
            return []
        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred while loading the sales data: {str(e)}")
            return []

        manipulated_df['PurchaseDate'] = pd.to_datetime(manipulated_df['PurchaseDate'], errors='coerce')
        manipulated_df['SellingPrice'] = pd.to_numeric(manipulated_df['SellingPrice'], errors='coerce')

        if manipulated_df.empty or manipulated_df['SellingPrice'].isnull().all():
            dispatcher.utter_message(text="The sales data is empty or invalid.")
            return []

        user_message = tracker.latest_message.get('text')

        # Extract country from user input
        country_name = extract_country(user_message)

        if not country_name:
            dispatcher.utter_message(text="I couldn't find a valid country in your request.")
            return []

        # Check for specific queries like max or avg sales
        if "max sales" in user_message.lower():
            max_sales = manipulated_df[manipulated_df['countryname'].str.lower() == country_name]['SellingPrice'].max()
            dispatcher.utter_message(text=f"The maximum sales in {country_name.capitalize()} is {max_sales:.2f}.")
        
        elif "avg sales" in user_message.lower():
            month_year_pattern = r'\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s*(?:of\s*)?(\d{4})\b'
            match = re.search(month_year_pattern, user_message, re.IGNORECASE)
            
            if match:
                month_str = match.group(0).strip().split()[0].lower()
                year = int(match.group(1))
                month = months.get(month_str)
                
                avg_sales = manipulated_df[(manipulated_df['PurchaseDate'].dt.month == month) & 
                               (manipulated_df['PurchaseDate'].dt.year == year) & 
                               (manipulated_df['countryname'].str.lower() == country_name)]['SellingPrice'].mean()
                
                dispatcher.utter_message(text=f"The average sales in {month_str.capitalize()} {year} in {country_name.capitalize()} is {avg_sales:.2f}.")
            else:
                dispatcher.utter_message(text="Please specify a month and year for average sales.")
        
        else:
            dispatcher.utter_message(text="I couldn't understand your request regarding sales.")

        return []