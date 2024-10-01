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
    months_reverse,format_sales_output,
    calculate_country_data    
)

logging.info("Loading Data from Excel file...")
df = pd.read_excel('cleaned_airhub_data.xlsx')
df['PurchaseDate'] = pd.to_datetime(df['PurchaseDate'], errors='coerce')
df['SellingPrice'] = pd.to_numeric(df['SellingPrice'], errors='coerce')

logging.info("Loaded data in dataframe...")


class ActionCountryCitySales(Action):
    def name(self) -> Text:
        return "action_country_city_sales"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            manipulated_df = df.copy()
            logging.info("Data loaded successfully...")
        except FileNotFoundError:
            dispatcher.utter_message(text="The Data file could not be found.")
            return []
        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred while loading the Data: {str(e)}")
            return []

        if manipulated_df.empty or manipulated_df['SellingPrice'].isnull().all():
            dispatcher.utter_message(text="The Data is empty or invalid.")
            return []

        user_message = tracker.latest_message.get('text')

        data = calculate_country_data(manipulated_df, user_message)
        # logging.info(data)
        # messages=format_sales_output(data)
        if data:
            dispatcher.utter_message(text=data)
        return []
class ActionGetTotalAndAverageSales(Action):

    def name(self) -> Text:
        return "action_get_total_and_average_sales"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        try:
            manipulated_df = df.copy()
            logging.info("Data loaded successfully.")
        except FileNotFoundError:
            dispatcher.utter_message(text="The Data file could not be found.")
            return []
        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred while loading the Data: {str(e)}")
            return []

        if manipulated_df.empty or manipulated_df['SellingPrice'].isnull().all():
            dispatcher.utter_message(text="The Data is empty or invalid.")
            return []

        user_message = tracker.latest_message.get('text')

        total_sales = calculate_total_and_average_sales(manipulated_df, user_message,flag=True)
        messages=format_sales_output(total_sales)
        if total_sales is not None:
            for data in messages:
                dispatcher.utter_message(text=data)

        return []



class ActionPlanSales(Action):
    def name(self) -> Text:
        return "action_plan_sales"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Implement logic for plans related queries here.
        dispatcher.utter_message(text="Processing plan related queries.")
        return []

class ActionPaymentSourceSales(Action):
    def name(self) -> Text:
        return "action_payment_source_sales"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Implement logic for payment source related queries here.
        dispatcher.utter_message(text="Processing payment source related queries.")
        return []

class ActionSourceOfSale(Action):
    def name(self) -> Text:
        return "action_source_of_sale"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Implement logic for source of sale related queries here.
        dispatcher.utter_message(text="Processing source of sale related queries.")
        return []