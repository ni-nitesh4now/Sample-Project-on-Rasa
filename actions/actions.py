
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


# Global variable for storing dataset
LOADED_DATASET = None

def load_sales_data(file_path='cleaned_airhub_data.xlsx'):
    global LOADED_DATASET
    if LOADED_DATASET is None:
        try:
            logging.info("Loading sales data from Excel file globally...")
            LOADED_DATASET = pd.read_excel(file_path)
            LOADED_DATASET['PurchaseDate'] = pd.to_datetime(LOADED_DATASET['PurchaseDate'], errors='coerce')
            LOADED_DATASET['salescount'] = pd.to_numeric(LOADED_DATASET['salescount'], errors='coerce')
            LOADED_DATASET['SellingPrice'] = pd.to_numeric(LOADED_DATASET['SellingPrice'], errors='coerce')
            logging.info("Sales data loaded successfully.")
        except FileNotFoundError:
            logging.error("The sales data file could not be found.")
        except Exception as e:
            logging.error(f"An error occurred while loading the sales data: {str(e)}")

#logging.info(f"Loaded columns: {LOADED_DATASET.columns.tolist()}")

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
    

# def calculate_sales_for_month_year_pairs(self, month_year_pairs: List[tuple[int, int]], 
#                                             dispatcher: CollectingDispatcher) -> float:
        
#         total_sales = 0.0
#         logging.info("Calculating total sales for specified months and years...")
       
#         for month, year in month_year_pairs:
#             monthly_sales = LOADED_DATASET[
#                 (LOADED_DATASET['PurchaseDate'].dt.month == month) & 
#                 (LOADED_DATASET['PurchaseDate'].dt.year == year)
#             ]['salescount'].sum()
#             # Handle potential NaN values
#             monthly_sales = monthly_sales if not pd.isna(monthly_sales) else 0.0

            
#             total_sales += monthly_sales
#             dispatcher.utter_message(text=f"The total sales for {months_reverse[month]} {year} is {monthly_sales:.2f}.")
        
#         return total_sales
# def calculate_sales_for_months(self, months_extracted: List[int], 
#                                     dispatcher: CollectingDispatcher) -> float:
        
        # logging.info("Calculating total sales for specified months without a year...")
#         current_year = pd.to_datetime('today').year  
#         total_sales = 0.0
        
#         for month in months_extracted:
#             monthly_sales = LOADED_DATASET[
#                 (LOADED_DATASET['PurchaseDate'].dt.month == month) & 
#                 (LOADED_DATASET['PurchaseDate'].dt.year == current_year)
#             ]['salescount'].sum()
#             # Handle potential NaN values
#             monthly_sales = monthly_sales if not pd.isna(monthly_sales) else 0.0
#             total_sales += monthly_sales
#             dispatcher.utter_message(text=f"The total sales for {months_reverse[month]} {current_year} is {monthly_sales:.2f}.")
        
#         return total_sales

# def handle_last_months_request(self, user_message: str, dispatcher: CollectingDispatcher) -> List[Dict[Text, Any]]:
#         logging.info("Processing request for total sales over last months...")
#         month_range_info = get_month_range_from_text(user_message)
#         month_range, num_months = month_range_info

#         if num_months:
#             start_month, start_year = month_range[0]
#             end_month, end_year = month_range[1]
#             logging.info("Calculating total sales for the last %d months...", num_months)
            
#             total_sales = self.calculate_total_sales_in_date_range(start_month, start_year, end_month, end_year)

#             dispatcher.utter_message(text=f"The total sales for the last {num_months} months is {total_sales:.2f}.")

 
# def calculate_total_sales_in_date_range(self, start_month: int, start_year: int, end_month: int, end_year: int) -> float:
#     return LOADED_DATASET[
#             ((LOADED_DATASET['PurchaseDate'].dt.year == start_year) & 
#              (LOADED_DATASET['PurchaseDate'].dt.month >= start_month)) |
#             ((LOADED_DATASET['PurchaseDate'].dt.year == end_year) & 
#              (LOADED_DATASET['PurchaseDate'].dt.month <= end_month)) |
#             ((LOADED_DATASET['PurchaseDate'].dt.year > start_year) & 
#              (LOADED_DATASET['PurchaseDate'].dt.year < end_year))
#         ]['salescount'].sum()
    
        
     
        
# class ActionGetTotalSales(Action):

#     def name(self) -> Text:
#         return "action_get_total_sales"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         
#         if LOADED_DATASET is None:
#             dispatcher.utter_message(text="Sorry, I couldn't load the sales data.")
#             return []

#         user_message = tracker.latest_message.get('text')
        
#         # Check for last X months request
#         if "last" in user_message and "month" in user_message:
#             return self.handle_last_months_request(user_message, dispatcher)
           
            
            

#         # Extract years and months from user input for other cases
#         years = extract_years(user_message)
#         months_extracted = extract_months(user_message)
#         month_year_pairs = extract_month_year(user_message)

#         total_sales = 0.0
#         if month_year_pairs:
#             total_sales = self.calculate_sales_for_month_year_pairs(month_year_pairs, dispatcher)
        
#         # If only years are mentioned
#         elif years:
#             total_sales = self.calculate_sales_for_years(years, dispatcher)

#         # If only months are mentioned (without specific year)
#         elif months_extracted:
#             total_sales = self.calculate_sales_for_months(months_extracted, dispatcher)

#         else:
#             dispatcher.utter_message(text="I couldn't find any valid year or month in your request.")
#             return []

#        return []

        



def extract_country(user_message):
    global LOADED_DATASET
    
    if LOADED_DATASET is not None:
        if 'countryname' in LOADED_DATASET.columns:
            logging.info("extracting country")
            valid_countries = LOADED_DATASET['countryname'].dropna().unique()
            # Create a regex pattern to match the country from the user message
            pattern = r'\b(' + '|'.join(map(re.escape, valid_countries)) + r')\b'

            match = re.search(pattern, user_message, re.IGNORECASE)
            if match:
                return match.group(0).lower()
            else:
                return None
        else:
            print("The dataset does not contain a 'countryname' column.")
            return None
    else:
        print("The dataset is not loaded.")
        return None


class ActionGetCountrySales(Action):

    def name(self) -> Text:
        return "action_get_country_sales"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
    

        user_message = tracker.latest_message.get('text')

        # Extract country from user input
        country_name = extract_country(user_message)

        if not country_name:
            dispatcher.utter_message(text="I couldn't find a valid country in your request.")
            return []

        # Check for specific queries like max or avg sales
        if "max sales" in user_message.lower():
            max_sales = df[df['countryname'].str.lower() == country_name]['salecount'].max()
            dispatcher.utter_message(text=f"The maximum sales in {country_name.capitalize()} is {max_sales:.2f}.")
        
        elif "avg sales" in user_message.lower():
            month_year_pattern = r'\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s*(?:of\s*)?(\d{4})\b'
            match = re.search(month_year_pattern, user_message, re.IGNORECASE)
            
            if match:
                month_str = match.group(0).strip().split()[0].lower()
                year = int(match.group(1))
                month = months.get(month_str)
                
                avg_sales = df[(df['PurchaseDate'].dt.month == month) & 
                               (df['PurchaseDate'].dt.year == year) & 
                               (df['countryname'].str.lower() == country_name)]['salescount'].mean()
                
                dispatcher.utter_message(text=f"The average sales in {month_str.capitalize()} {year} in {country_name.capitalize()} is {avg_sales:.2f}.")
            else:
                dispatcher.utter_message(text="Please specify a month and year for average sales.")
        
        else:
            dispatcher.utter_message(text="I couldn't understand your request regarding sales.")

        return []

 
def extract_total_revenue(country_name: str) -> float:
    global LOADED_DATASET

    # Check if the dataset is loaded
    if LOADED_DATASET is not None:
        logging.info("Calculating total revenue")
        # Filter the dataset by country name
        filtered_data = LOADED_DATASET[LOADED_DATASET['countryname'].str.lower() == country_name.lower()]

        # Calculate the total sales revenue for the specified country
        total_revenue = filtered_data['SellingPrice'].sum()

        return total_revenue

    return None


class ActionGetTotalRevenue(Action):

    def name(self) -> Text:
        return "action_get_total_revenue"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

          # Load the dataset globally at the start of the action server
        
        user_message = tracker.latest_message.get('text')

        # Extract country from user input
        country_name = extract_country(user_message)
        if not country_name:
            dispatcher.utter_message(text="I couldn't find a valid country in your request.")
            return []
       
        # Extract total revenue from user input
        total_revenue = extract_total_revenue(user_message)

        if total_revenue is not None:
            # # Calculate total sales exceeding the specified revenue in the given country
            # exceeding_sales = LOADED_DATASET[
            #     (LOADED_DATASET['countryname'].str.lower() == country_name) & 
            #     (LOADED_DATASET['SellingPrice'] > total_revenue)
            # ]['SellingPrice'].sum()
            dispatcher.utter_message(text=f"The total sales in {country_name.capitalize()} exceeding ${total_revenue:.2f} is ${exceeding_sales:.2f}.")
        
        else:
            dispatcher.utter_message(text="Please specify a valid country name.")

        return []



def extract_countries_from_data():
    global LOADED_DATASET 
    try:
        if LOADED_DATASET is not None:
            logging.info("Extractig countries from data")
            # Assuming 'countryname' is the column that contains country names
            unique_countries = LOADED_DATASET['countryname'].unique()
            return unique_countries.tolist()
    except Exception as e:
        logging.error(f"An error occurred while extracting countries: {str(e)}")
    return []


class ActionGetCountryNames(Action):

    def name(self) -> Text:
        return "action_get_country_names"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

         
        
        # Extract country names using the helper function
        unique_countries = extract_countries_from_data()
        
        if unique_countries:
            total_countries = len(unique_countries)
            countries_list = ', '.join(unique_countries)
            dispatcher.utter_message(text=f"There are a total of {total_countries} countries: {countries_list}.")
        else:
            dispatcher.utter_message(text="No countries found in the sales data.")

        return []

def extract_plan_names():
    global LOADED_DATASET
    try:
        if LOADED_DATASET is not None:
            logging.info("Extracting Plan names")
            unique_plans = LOADED_DATASET['PlanName'].unique()
            return unique_plans.tolist()
    except Exception as e:
        logging.error(f"An error occurred while extracting plan names: {str(e)}")
    return []



class ActionGetPlanNames(Action):

    def name(self) -> Text:
        return "action_get_plan_names"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

         
        # Extract plan names
        plan_names = extract_plan_names()
       
        if plan_names:
            total_plans = len(plan_names)
            plans_list = ', '.join(plan_names)
            dispatcher.utter_message(text=f"There are a total of {total_plans} plans: {plans_list}.")
        else:
            dispatcher.utter_message(text="No plans found in the sales data.")

        return []




def extract_top_countries():
    global LOADED_DATASET
    if LOADED_DATASET is not None:
        logging.info("Calculating top countries")
        country_sales = LOADED_DATASET.groupby('countryname').agg(
            sales_count=('SellingPrice', 'count'),
            total_sales=('SellingPrice', 'sum')
        ).reset_index()

        # Sort by sales_count and total_sales
        top_countries = country_sales.sort_values(by=['sales_count', 'total_sales'], ascending=False).head(10)
        return top_countries
    return None

def extract_top_plans():
    global LOADED_DATASET
    if LOADED_DATASET is not None:
        logging.info("Calculating top plans")
        plan_sales = LOADED_DATASET.groupby('PlanName').agg(
            sales_count=('SellingPrice', 'count'),
            total_sales=('SellingPrice', 'sum')
        ).reset_index()

        # Sort by sales_count
        top_plans = plan_sales.sort_values(by='sales_count', ascending=False).head(5)
        return top_plans
    return None



class ActionGetTopCountriesAndPlans(Action):

    def name(self) -> Text:
        return "action_get_top_countries_and_plans"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

         
        
        # Extract top countries
        top_countries = extract_top_countries()
        
        if top_countries is not None:
            country_info = "\n".join([f"{row['countryname']}: {row['sales_count']} sales, ${row['total_sales']:.2f}" for index, row in top_countries.iterrows()])
            dispatcher.utter_message(text=f"Top 10 countries by sales count:\n{country_info}")
        
        # Extract top plans
        top_plans = extract_top_plans()
        
        if top_plans is not None:
            plan_info = "\n".join([f"{row['PlanName']}: {row['sales_count']} sales, ${row['total_sales']:.2f}" for index, row in top_plans.iterrows()])
            dispatcher.utter_message(text=f"\nTop 5 plans by sales:\n{plan_info}")

        return []





def calculate_sales_growth(period='month'):
    global LOADED_DATASET
    if LOADED_DATASET is not None:
        try:
            if period == 'month':
                logging.info("Sales growth by month")
                LOADED_DATASET['YearMonth'] = LOADED_DATASET['PurchaseDate'].dt.to_period('M')
                sales_growth = LOADED_DATASET.groupby('YearMonth')['salescount'].sum().pct_change() * 100
                return sales_growth.dropna().reset_index(name='SalesGrowthPercentage')

            elif period == 'year':
                logging.info("growth by year")
                LOADED_DATASET['Year'] = LOADED_DATASET['PurchaseDate'].dt.year
                sales_growth = LOADED_DATASET.groupby('Year')['salescount'].sum().pct_change() * 100
                return sales_growth.dropna().reset_index(name='SalesGrowthPercentage')

        except Exception as e:
            logging.error(f"An error occurred while calculating sales growth: {str(e)}")
    return None

class ActionGetSalesGrowth(Action):

    def name(self) -> Text:
        return "action_get_sales_growth"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get('text')
        
        
        # Determine if the query is for monthly or yearly growth
        if "month" in user_message.lower():
            sales_growth_data = calculate_sales_growth( period='month')
            if sales_growth_data is not None:
                growth_info = "\n".join([f"{row['YearMonth']}: {row['SalesGrowthPercentage']:.2f}%" for index, row in sales_growth_data.iterrows()])
                dispatcher.utter_message(text=f"Sales growth percentage by month:\n{growth_info}")
        
        elif "year" in user_message.lower():
            sales_growth_data = calculate_sales_growth( period='year')
            if sales_growth_data is not None:
                growth_info = "\n".join([f"{row['Year']}: {row['SalesGrowthPercentage']:.2f}%" for index, row in sales_growth_data.iterrows()])
                dispatcher.utter_message(text=f"Sales growth percentage by year:\n{growth_info}")
        
        else:
            dispatcher.utter_message(text="Please specify whether you want to see the sales growth by month or by year.")

        return []


def extract_lowest_countries():
    global LOADED_DATASET
    if LOADED_DATASET is not None:
        logging.info("Calculating lowest country")
        country_sales = LOADED_DATASET.groupby('countryname').agg(
            sales_count=('SellingPrice', 'count'),
            total_sales=('SellingPrice', 'sum')
        ).reset_index()

        # Sort by sales_count and total_sales in ascending order
        lowest_countries = country_sales.sort_values(by=['sales_count', 'total_sales']).head(10)
        return lowest_countries
    return None




class ActionGetLowestCountries(Action):

    def name(self) -> Text:
        return "action_get_lowest_countries"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

          # Load the dataset globally at the start of the action server
        
        # Extract lowest countries
        lowest_countries = extract_lowest_countries()
        
        if lowest_countries is not None:
            country_info = "\n".join([f"{row['countryname']}: {row['sales_count']} sales, ${row['total_sales']:.2f}" for index, row in lowest_countries.iterrows()])
            dispatcher.utter_message(text=f"Lowest 10 countries by sales count:\n{country_info}")
        
        return []

def extract_lowest_plans():
    global LOADED_DATASET
    if LOADED_DATASET is not None:
        logging.info("Lowest plans")
        plan_sales = LOADED_DATASET.groupby('PlanName').agg(
            sales_count=('SellingPrice', 'count'),
            total_sales=('SellingPrice', 'sum')
        ).reset_index()

        # Sort by sales_count in ascending order
        lowest_plans = plan_sales.sort_values(by='sales_count').head(5)
        return lowest_plans
    return None
    
class ActionGetLowestPlans(Action):

    def name(self) -> Text:
        return "action_get_lowest_plans"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

          # Load the dataset globally at the start of the action server
        
        # Extract lowest plans
        lowest_plans = extract_lowest_plans()
        
        if lowest_plans is not None:
            plan_info = "\n".join([f"{row['PlanName']}: {row['sales_count']} sales, ${row['total_sales']:.2f}" for index, row in lowest_plans.iterrows()])
            dispatcher.utter_message(text=f"Lowest 5 plans by sales count:\n{plan_info}")

        return []

def extract_top_regions():
    global LOADED_DATASET
    if LOADED_DATASET is not None:
        logging.info("Calculating top regions")
        region_sales = LOADED_DATASET.groupby('regionname').agg(
            sales_count=('SellingPrice', 'count'),
            total_sales=('SellingPrice', 'sum')
        ).reset_index()

        # Sort by sales_count and total_sales in descending order
        top_regions = region_sales.sort_values(by=['sales_count', 'total_sales'], ascending=False).head(10)
        return top_regions
    return None
class ActionGetTopRegions(Action):

    def name(self) -> Text:
        return "action_get_top_regions"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

          # Load the dataset globally at the start of the action server
        
        # Extract top regions
        top_regions = extract_top_regions()
        
        if top_regions is not None:
            region_info = "\n".join([f"{row['regionname']}: {row['sales_count']} sales, ${row['total_sales']:.2f}" for index, row in top_regions.iterrows()])
            dispatcher.utter_message(text=f"Top 10 regions by sales count:\n{region_info}")

        return []

def extract_regions():
    global LOADED_DATASET
    if LOADED_DATASET is not None:
        logging.info("Extracting regions")
        # Assuming 'Region' is the column that contains region names
        unique_regions = LOADED_DATASET['regionname'].unique()
        return unique_regions.tolist()
    return []

class ActionGetRegions(Action):

    def name(self) -> Text:
        return "action_get_regions"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

          # Load the dataset globally at the start of the action server
        
        # Extract regions using the helper function
        regions = extract_regions()
        if regions:
            total_regions = len(regions)
            regions_list = ', '.join(regions)
            dispatcher.utter_message(text=f"There are a total of {total_regions} regions: {regions_list}.")
        else:
            dispatcher.utter_message(text="No regions found in the sales data.")

        return []

def extract_sales_by_source():
    global LOADED_DATASET
    if LOADED_DATASET is not None:
        # Group by 'Source' and aggregate total sales and count of 'SellingPrice'
        logging.info("Calculating sales by source")
        aggregated_data = LOADED_DATASET.groupby(LOADED_DATASET['Source'].str.lower()).agg(
            total_sales=('SellingPrice', 'sum'),
            sales_count=('SellingPrice', 'count')
        ).reset_index()

        return aggregated_data
    return None
    
class ActionGetSalesBySource(Action):

    def name(self) -> Text:
        return "action_get_sales_by_source"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

          # Load the dataset globally at the start of the action server
        
        # Extract aggregate plans by source using the helper function
        aggregated_sales = extract_sales_by_source()
        
        if aggregated_sales is not None and not aggregated_sales.empty:
            source_info = "\n".join([f"{row['Source']}: Total Sales = ${row['total_sales']:.2f}, Sales Count = {row['sales_count']}" for index, row in aggregated_sales.iterrows()])
            dispatcher.utter_message(text=f" sources by total sales:\n{source_info}")
        else:
            dispatcher.utter_message(text="No sources found in the sales data.")

        return []

def extract_plan_names_by_country(country_name):
    global LOADED_DATASET
    if LOADED_DATASET is not None:
        # Filter the dataset by the specified country
        logging.info("Calculating plan names by country")

        country_data = LOADED_DATASET[LOADED_DATASET['countryname'].str.lower() == country_name.lower()]
        
        # Extract unique plan names from the filtered dataset
        plan_names = country_data['PlanName'].unique().tolist()
        
        return plan_names
    return []

class ActionGetPlanNamesByCountry(Action):

    def name(self) -> Text:
        return "action_get_plan_names_by_country"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

          # Load the dataset globally at the start of the action server
        load_sales_data()

        user_message = tracker.latest_message.get('text')
        
        # Extract country from user input
        country_name = extract_country(user_message)
        if not country_name:
            dispatcher.utter_message(text="I couldn't find a valid country in your request.")
            return []
        
        # Extract plan names for the specified country
        plan_names = extract_plan_names_by_country(country_name)
        
        if plan_names:
            total_plans = len(plan_names)
            plans_list = ', '.join(plan_names)
            dispatcher.utter_message(text=f"The available plans in {country_name.capitalize()} are: {plans_list}.")
        else:
            dispatcher.utter_message(text=f"No plans found for {country_name.capitalize()}.")

        return []


def extract_sales_by_payment_gateway():
    global LOADED_DATASET
    if LOADED_DATASET is not None:
        if 'PaymentGateway' in LOADED_DATASET.columns:
            logging.info("Calculating sales by payment gateway")

            # Group by 'PaymentGateway' and aggregate total sales count and sum of 'SellingPrice'
            aggregated_data = LOADED_DATASET.groupby('PaymentGateway').agg(
                total_sales_count=('SellingPrice', 'count'),
                total_sales_value=('SellingPrice', 'sum')
            ).reset_index()

            return aggregated_data
        else:
            logging.error("The 'PaymentGateway' column is missing from the dataset.")
    return None
        

class ActionGetSalesByPaymentGateway(Action):

    def name(self) -> Text:
        return "action_get_sales_by_payment_gateway"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

          # Load the dataset globally at the start of the action server
        
        # Extract sales data grouped by payment gateway using the helper function
        sales_by_gateway = extract_sales_by_payment_gateway()
        
        if sales_by_gateway is not None and not sales_by_gateway.empty:
            gateway_info = "\n".join([f"{row['PaymentGateway']}: Total Sales = ${row['total_sales']:.2f}, Sales Count = {row['sales_count']}" for index, row in sales_by_gateway.iterrows()])
            dispatcher.utter_message(text=f"Sales grouped by payment gateway:\n{gateway_info}")
        else:
            dispatcher.utter_message(text="No sales data found.")

        return []


def extract_sales_by_country_and_plan():
    global LOADED_DATASET
    if LOADED_DATASET is not None:
        # Group by 'countryname' and 'PlanName' and aggregate total sales count and sum of 'SellingPrice'
        # Ensure the required columns exist
        required_columns = ['countryname', 'PlanName', 'SellingPrice']
        if all(col in LOADED_DATASET.columns for col in required_columns):
            # Group by 'countryname' and 'PlanName' and aggregate total sales count and sum of 'SellingPrice'
            aggregated_data = LOADED_DATASET.groupby(['countryname', 'PlanName']).agg(
                total_sales_count=('SellingPrice', 'count'),
                total_sales_value=('SellingPrice', 'sum')
            ).reset_index()

            return aggregated_data
        else:
            logging.error("Required columns are missing from the dataset.")
    return None
        

class ActionGetSalesByCountryAndPlan(Action):

    def name(self) -> Text:
        return "action_get_sales_by_country_and_plan"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

          # Load the dataset globally at the start of the action server
        
        # Extract sales data grouped by country and plan using the helper function
        sales_data = extract_sales_by_country_and_plan()
        
        if sales_data is not None and not sales_data.empty:
            sales_info = "\n".join([f"{row['countryname']} - {row['PlanName']}: Count = {row['total_sales_count']}, Total Sales = ${row['total_sales_value']:.2f}" for index, row in sales_data.iterrows()])
            dispatcher.utter_message(text=f"Sales grouped by country and plan:\n{sales_info}")
        else:
            dispatcher.utter_message(text="No sales data found.")

        return []