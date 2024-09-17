
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SessionStarted
from rasa_sdk.executor import CollectingDispatcher
from datetime import datetime, timedelta
from actions.utils import DataManager, get_filtered_data  



#actionslist
class ActionSessionStart(Action):

    def name(self) -> Text:
        return "action_session_start"

    async def run(self, dispatcher: CollectingDispatcher, 
                  tracker: Tracker, 
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Start the session and perform any initial tasks
        events = [SessionStarted()]  # You can add other events here if needed
        
        # Example: Setting a slot with a greeting
        events.append(SlotSet("greeting", "Welcome! How can I assist you today?"))
        
        # You can also execute an action immediately after session start
        events.append(ActionExecuted("action_listen"))
        
        # Optionally, send a message at the start of the session
        dispatcher.utter_message(text="Hello! A new session has started.")
        
        return events
        
class ActionTotalSales(Action):

    def name(self) -> Text:
        return "action_total_sales"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        data_manager = DataManager()
        df = data_manager.get_data()
        # Get total sales using the function
        total_sales = df['salescount'].sum()

        # Send the result back to the user
        dispatcher.utter_message(text=f"The total sales amount is: {total_sales}")
        
        return []
class ActionTotalSalesLastMonth(Action):
    def name(self) -> Text:
        return "action_total_sales_last_month"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        today = datetime.now()
        first_day_of_current_month = today.replace(day=1)
        last_month = first_day_of_current_month - timedelta(days=1)
        first_day_of_last_month = last_month.replace(day=1)
        last_day_of_last_month = last_month
        
        data_manager = DataManager()
        df = data_manager.get_data()
        data = get_filtered_data(df, start_date=first_day_of_last_month, end_date=last_day_of_last_month)
        total_sales = data['salescount'].sum()
        
        dispatcher.utter_message(text=f"Total sales for the last month were ${total_sales:.2f}.")
        return []

class ActionSalesLastQuarter(Action):
    def name(self) -> Text:
        return "action_sales_last_quarter"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        today = datetime.now()
        current_month = today.month
        current_year = today.year
        
        if current_month in [1, 2, 3]:
            start_date = datetime(current_year - 1, 10, 1)
            end_date = datetime(current_year - 1, 12, 31)
        elif current_month in [4, 5, 6]:
            start_date = datetime(current_year, 1, 1)
            end_date = datetime(current_year, 3, 31)
        elif current_month in [7, 8, 9]:
            start_date = datetime(current_year, 4, 1)
            end_date = datetime(current_year, 6, 30)
        else:
            start_date = datetime(current_year, 7, 1)
            end_date = datetime(current_year, 9, 30)
        
        data_manager = DataManager()
        df = data_manager.get_data()
        data = get_filtered_data(df, start_date=start_date, end_date=end_date)
        total_sales = data['salescount'].sum()
        
        dispatcher.utter_message(text=f"Total sales for the last quarter were ${total_sales:.2f}.")
        return []


class ActionSalesForSpecificMonthYear(Action):
    def name(self) -> Text:
        return "action_sales_for_specific_month_year"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        month = tracker.get_slot('month')
        year = tracker.get_slot('year')
        country = tracker.get_slot('country_name')
        
        # Validate and convert month and year to integers
        try:
            month = int(month)
            year = int(year)
        except ValueError:
            dispatcher.utter_message(text="Please provide valid numerical values for month and year.")
            return []

        # Check if the month and year are valid
        if month < 1 or month > 12:
            dispatcher.utter_message(text="Please provide a valid month (1-12).")
            return []
        if year < 2000 or year > datetime.now().year:
            dispatcher.utter_message(text="Please provide a valid year.")
            return []

        start_date = datetime(year, month, 1)
        end_date = (start_date + pd.DateOffset(months=1)) - pd.DateOffset(days=1)
        
        data_manager = DataManager()
        df = data_manager.get_data()
        data = get_filtered_data(df, start_date=start_date, end_date=end_date, country=country)
        total_sales = data['salescount'].sum()
        
        dispatcher.utter_message(text=f"Total sales in {month}/{year} for {country} were ${total_sales:.2f}.")
        return []

class ActionCountryHighestSalesLastQuarter(Action):
    def name(self) -> Text:
        return "action_country_highest_sales_last_quarter"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        today = datetime.now()
        if today.month in [1, 2, 3]:
            start_date = datetime(today.year - 1, 10, 1)
        elif today.month in [4, 5, 6]:
            start_date = datetime(today.year, 1, 1)
        elif today.month in [7, 8, 9]:
            start_date = datetime(today.year, 4, 1)
        else:
            start_date = datetime(today.year, 7, 1)
        end_date = (start_date + pd.DateOffset(months=3)) - pd.DateOffset(days=1)
        
        data = get_sales_data(df, start_date, end_date)
        highest_sales_country = data.groupby('countryname')['salescount'].sum().idxmax()
        data_manager = DataManager()
        df = data_manager.get_data()
        data = get_filtered_data(df, start_date=start_date, end_date=end_date)
        dispatcher.utter_message(text=f"The country with the highest sales in the last quarter was {highest_sales_country}.")
        return []

class ActionSalesFiguresForCountryYear(Action):
    def name(self) -> Text:
        return "action_sales_figures_for_country_year"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        year = tracker.get_slot('year')
        country = tracker.get_slot('country_name')
        
        # Validate year input
        try:
            year = int(year)
        except ValueError:
            dispatcher.utter_message(text="Please provide a valid year.")
            return []

        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        
        data_manager = DataManager()
        df = data_manager.get_data()
        data = get_filtered_data(df, start_date=start_date, end_date=end_date, country=country)
        total_sales = data['salescount'].sum()
        
        dispatcher.utter_message(text=f"Total sales in {country} for the year {year} were ${total_sales:.2f}.")
        return []

class ActionSalesFiguresForCountryMonth(Action):
    def name(self) -> Text:
        return "action_sales_figures_for_country_month"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        month = tracker.get_slot('month')
        year = tracker.get_slot('year')
        country = tracker.get_slot('country_name')
        
        # Validate month and year input
        try:
            month = int(month)
            year = int(year)
            if month < 1 or month > 12:
                dispatcher.utter_message(text="Please provide a valid month (1-12).")
                return []
        except ValueError:
            dispatcher.utter_message(text="Please provide valid month and year.")
            return []

        start_date = datetime(year, month, 1)
        end_date = (start_date + pd.DateOffset(months=1)) - pd.DateOffset(days=1)
        
        data_manager = DataManager()
        df = data_manager.get_data()
        data = get_filtered_data(df, start_date=start_date, end_date=end_date, country=country)
        total_sales = data['salescount'].sum()
        
        dispatcher.utter_message(text=f"Total sales in {country} for {month}/{year} were ${total_sales:.2f}.")
        return []
class ActionSalesRankingByCountryCurrentYear(Action):
    def name(self) -> Text:
        return "action_sales_ranking_by_country_current_year"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        country = tracker.get_slot('country_name')
        year = datetime.now().year
        
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        
        data_manager = DataManager()
        df = data_manager.get_data()
        data = get_filtered_data(df, start_date=start_date, end_date=end_date, country=country)
        
        sales_ranking = data.groupby('PlanName')['salescount'].sum().sort_values(ascending=False)
        ranking_message = "\n".join([f"{plan}: ${sales:.2f}" for plan, sales in sales_ranking.items()])
        
        dispatcher.utter_message(text=f"Sales ranking for plans in {country} for the current year:\n{ranking_message}")
        return []
class ActionMostPopularPlanBySales(Action):
    def name(self) -> Text:
        return "action_most_popular_plan_by_sales"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        year = datetime.now().year
        
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        
        data_manager = DataManager()
        df = data_manager.get_data()
        data = get_filtered_data(df, start_date=start_date, end_date=end_date)
        
        most_popular_plan = data.groupby('PlanName')['salescount'].sum().idxmax()
        
        dispatcher.utter_message(text=f"The most popular plan by sales for the current year is {most_popular_plan}.")
        return []
class ActionLowestSalesPlan(Action):
    def name(self) -> Text:
        return "action_lowest_sales_plan"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        year = datetime.now().year
        
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        
        data_manager = DataManager()
        df = data_manager.get_data()
        data = get_filtered_data(df, start_date=start_date, end_date=end_date)
        
        lowest_sales_plan = data.groupby('PlanName')['salescount'].sum().idxmin()
        
        dispatcher.utter_message(text=f"The plan with the lowest sales for the current year is {lowest_sales_plan}.")
        return []
class ActionComparePlanSales(Action):
    def name(self) -> Text:
        return "action_compare_plan_sales"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        plan1 = tracker.get_slot('plan1')
        plan2 = tracker.get_slot('plan2')
        year = datetime.now().year
        
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        
        data_manager = DataManager()
        df = data_manager.get_data()
        data = get_filtered_data(df, start_date=start_date, end_date=end_date)
        
        sales_plan1 = data[data['PlanName'] == plan1]['salescount'].sum()
        sales_plan2 = data[data['PlanName'] == plan2]['salescount'].sum()
        
        if sales_plan1 > sales_plan2:
            comparison_message = f"{plan1} has higher sales than {plan2}."
        elif sales_plan1 < sales_plan2:
            comparison_message = f"{plan2} has higher sales than {plan1}."
        else:
            comparison_message = f"{plan1} and {plan2} have equal sales."
        
        dispatcher.utter_message(text=comparison_message)
        return []
class ActionTotalSalesForRegionLastYear(Action):
    def name(self) -> Text:
        return "action_total_sales_for_region_last_year"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        region = tracker.get_slot('region_name')
        last_year = datetime.now().year - 1
        
        start_date = datetime(last_year, 1, 1)
        end_date = datetime(last_year, 12, 31)
        
        data_manager = DataManager()
        df = data_manager.get_data()
        data = get_filtered_data(df, start_date=start_date, end_date=end_date, region=region)
        total_sales = data['salescount'].sum()
        
        dispatcher.utter_message(text=f"Total sales in {region} for the year {last_year} were ${total_sales:.2f}.")
        return []
class ActionSalesDataForRegionLastQuarter(Action):
    def name(self) -> Text:
        return "action_sales_data_for_region_last_quarter"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        region = tracker.get_slot('region_name')
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        
        # Determine the start and end of the last quarter
        if current_month in [1, 2, 3]:
            start_date = datetime(current_year - 1, 10, 1)
            end_date = datetime(current_year - 1, 12, 31)
        elif current_month in [4, 5, 6]:
            start_date = datetime(current_year, 1, 1)
            end_date = datetime(current_year, 3, 31)
        elif current_month in [7, 8, 9]:
            start_date = datetime(current_year, 4, 1)
            end_date = datetime(current_year, 6, 30)
        else:
            start_date = datetime(current_year, 7, 1)
            end_date = datetime(current_year, 9, 30)
        
        data_manager = DataManager()
        df = data_manager.get_data()
        data = get_filtered_data(df, start_date=start_date, end_date=end_date, region=region)
        total_sales = data['salescount'].sum()
        
        dispatcher.utter_message(text=f"Total sales in {region} for the last quarter were ${total_sales:.2f}.")
        return []

class ActionRegionWithHighestSalesIncrease(Action):
    def name(self) -> Text:
        return "action_region_with_highest_sales_increase"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        # Logic to determine region with the highest sales increase
        # Example implementation here
        # Just an example, adjust according to your actual logic
        region_sales = df.groupby('regionname')['salescount'].sum()
        region_increase = region_sales.diff().fillna(0)
        highest_increase_region = region_increase.idxmax()
        dispatcher.utter_message(text=f"The region with the highest sales increase is {highest_increase_region}.")
        return []
class ActionSalesOnSpecificDate(Action):
    def name(self) -> Text:
        return "action_sales_on_specific_date"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        specific_date = tracker.get_slot('specific_date')
        
        # Ask for input if specific_date is not provided
        if not specific_date:
            dispatcher.utter_message(text="Please provide a specific date (YYYY-MM-DD) to retrieve the sales.")
            return []

        filtered_data = get_filtered_data(df, specific_date=specific_date)
        total_sales = filtered_data['salescount'].sum()
        dispatcher.utter_message(text=f"Total sales on {specific_date} were ${total_sales:.2f}.")
        return []

class ActionSalesPerformanceForMonthYear(Action):
    def name(self) -> Text:
        return "action_sales_performance_for_month_year"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        month = tracker.get_slot('month')
        year = tracker.get_slot('year')

        # Ask for input if month or year is not provided
        if not month or not year:
            dispatcher.utter_message(text="Please provide both the month and year (e.g., MM/YYYY) for sales performance.")
            return []

        filtered_data = get_filtered_data(df, start_date=f"{year}-{month}-01", end_date=f"{year}-{month}-31")
        total_sales = filtered_data['salescount'].sum()
        dispatcher.utter_message(text=f"Sales performance for {month}/{year} shows a total of ${total_sales:.2f}.")
        return []

class ActionCompareCurrentAndLastYearSales(Action):
    def name(self) -> Text:
        return "action_compare_current_and_last_year_sales"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        current_year = tracker.get_slot('current_year')
        last_year = tracker.get_slot('last_year')

        # Ask for input if current_year or last_year is not provided
        if not current_year or not last_year:
            dispatcher.utter_message(text="Please provide both the current and last year for comparison.")
            return []

        current_year_sales = df[df['PurchaseYear'] == current_year]['salescount'].sum()
        last_year_sales = df[df['PurchaseYear'] == last_year]['salescount'].sum()
        sales_difference = current_year_sales - last_year_sales
        dispatcher.utter_message(text=f"Comparing sales between {current_year} and {last_year}, the difference is ${sales_difference:.2f}.")
        return []

class ActionMonthOverMonthComparison(Action):
    def name(self) -> Text:
        return "action_month_over_month_comparison"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        month1 = tracker.get_slot('month1')
        month2 = tracker.get_slot('month2')

        # Ask for input if month1 or month2 is not provided
        if not month1 or not month2:
            dispatcher.utter_message(text="Please provide two months (e.g., MM) for the comparison.")
            return []

        year = datetime.datetime.now().year  # Assuming current year for comparison
        sales_month1 = df[(df['PurchaseMonth'] == month1) & (df['PurchaseYear'] == year)]['salescount'].sum()
        sales_month2 = df[(df['PurchaseMonth'] == month2) & (df['PurchaseYear'] == year)]['salescount'].sum()
        comparison_result = "higher" if sales_month1 > sales_month2 else "lower"
        dispatcher.utter_message(text=f"Month-over-month comparison shows that {month1} had {comparison_result} sales compared to {month2}.")
        return []
class ActionTrendOfSales(Action):
    def name(self) -> Text:
        return "action_trend_of_sales"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        # Example logic for trend analysis
        # You can replace this with actual trend analysis
        sales_trend = df.groupby('PurchaseDate')['salescount'].sum().pct_change().mean()
        trend_result = "positive" if sales_trend > 0 else "negative"
        dispatcher.utter_message(text=f"The sales trend shows {trend_result}.")
        return []

class ActionSalesDataForFirstQuarter(Action):
    def name(self) -> Text:
        return "action_sales_data_for_first_quarter"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        year = tracker.get_slot('year')

        # Validate year input
        try:
            year = int(year)
        except ValueError:
            dispatcher.utter_message(text="Please provide a valid year.")
            return []

        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 3, 31)

        data = get_filtered_data(df, start_date, end_date)
        total_sales = data['salescount'].sum()

        dispatcher.utter_message(text=f"Total sales for the first quarter of {year} were ${total_sales:.2f}.")
        return []

class ActionTop5CountriesBySales(Action):
    def name(self) -> Text:
        return "action_top_5_countries_by_sales"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        top_countries = df.groupby('countryname')['salescount'].sum().nlargest(5)
        
        message = "Top 5 countries by sales:\n"
        for country, sales in top_countries.items():
            message += f"{country}: ${sales:.2f}\n"

        dispatcher.utter_message(text=message)
        return []

class ActionSalesDifferenceBetweenCountries(Action):
    def name(self) -> Text:
        return "action_sales_difference_between_countries"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        country1 = tracker.get_slot('country1')
        country2 = tracker.get_slot('country2')

        df = DataManager().get_data()
        sales_country1 = df[df['countryname'] == country1]['salescount'].sum()
        sales_country2 = df[df['countryname'] == country2]['salescount'].sum()

        difference = sales_country1 - sales_country2

        dispatcher.utter_message(text=f"The sales difference between {country1} and {country2} is ${difference:.2f}.")
        return []

class ActionWeeklySalesInMonthYear(Action):
    def name(self) -> Text:
        return "action_weekly_sales_in_month_year"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        month = tracker.get_slot('month')
        year = tracker.get_slot('year')

        # Validate month and year input
        try:
            month = int(month)
            year = int(year)
            if month < 1 or month > 12:
                dispatcher.utter_message(text="Please provide a valid month (1-12).")
                return []
        except ValueError:
            dispatcher.utter_message(text="Please provide valid month and year.")
            return []

        start_date = datetime(year, month, 1)
        end_date = (start_date + pd.DateOffset(months=1)) - pd.DateOffset(days=1)

        data = get_filtered_data(df, start_date, end_date)
        weekly_sales = data.groupby(data['PurchaseDate'].dt.isocalendar().week)['salescount'].sum()

        message = f"Weekly sales for {month}/{year}:\n"
        for week, sales in weekly_sales.items():
            message += f"Week {week}: ${sales:.2f}\n"

        dispatcher.utter_message(text=message)
        return []

class ActionSalesDataLast6Months(Action):
    def name(self) -> Text:
        return "action_sales_data_last_6_months"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.DateOffset(months=6)

        data = get_filtered_data(df, start_date, end_date)
        total_sales = data['salescount'].sum()

        dispatcher.utter_message(text=f"Total sales for the last 6 months were ${total_sales:.2f}.")
        return []

class ActionTotalSalesLast12Months(Action):
    def name(self) -> Text:
        return "action_total_sales_last_12_months"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.DateOffset(months=12)

        data = get_filtered_data(df, start_date, end_date)
        total_sales = data['salescount'].sum()

        dispatcher.utter_message(text=f"Total sales for the last 12 months were ${total_sales:.2f}.")
        return []
from typing import Text, Any, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from datetime import datetime

class ActionHighestSingleSaleLastYear(Action):
    def name(self) -> Text:
        return "action_highest_single_sale_last_year"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        year = datetime.now().year - 1
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)

        data = get_filtered_data(df, start_date, end_date)
        highest_sale = data['salescount'].max()

        dispatcher.utter_message(text=f"The highest single sale in {year} was ${highest_sale:.2f}.")
        return []

class ActionLowestPerformingPlanLastQuarter(Action):
    def name(self) -> Text:
        return "action_lowest_performing_plan_last_quarter"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        end_date = datetime.now()
        start_date = end_date - pd.DateOffset(weeks=13)

        data = get_filtered_data(df, start_date, end_date)
        lowest_performing_plan = data.groupby('PlanName')['salescount'].sum().idxmin()

        dispatcher.utter_message(text=f"The lowest performing plan in the last quarter was {lowest_performing_plan}.")
        return []

class ActionLowestSalesRegionThisYear(Action):
    def name(self) -> Text:
        return "action_lowest_sales_region_this_year"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        year = datetime.now().year
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)

        data = get_filtered_data(df, start_date, end_date)
        lowest_sales_region = data.groupby('regionname')['salescount'].sum().idxmin()

        dispatcher.utter_message(text=f"The region with the lowest sales this year is {lowest_sales_region}.")
        return []

class ActionSalesDuringHolidaySeason(Action):
    def name(self) -> Text:
        return "action_sales_during_holiday_season"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        year = datetime.now().year
        start_date = datetime(year, 12, 1)
        end_date = datetime(year, 12, 31)

        data = get_filtered_data(df, start_date, end_date)
        total_sales = data['salescount'].sum()

        dispatcher.utter_message(text=f"Total sales during the holiday season (December) this year were ${total_sales:.2f}.")
        return []

class ActionSalesComparisonSummerWinter(Action):
    def name(self) -> Text:
        return "action_sales_comparison_summer_winter"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        year = datetime.now().year
        
        summer_start = datetime(year, 6, 1)
        summer_end = datetime(year, 8, 31)
        winter_start = datetime(year, 12, 1)
        winter_end = datetime(year, 2, 28) if (datetime(year, 2, 28).month == 2) else datetime(year, 2, 29)

        summer_sales = get_filtered_data(df, summer_start, summer_end)['salescount'].sum()
        winter_sales = get_filtered_data(df, winter_start, winter_end)['salescount'].sum()

        dispatcher.utter_message(text=f"Sales comparison: Summer (June-August) vs. Winter (December-February).\nSummer sales: ${summer_sales:.2f}\nWinter sales: ${winter_sales:.2f}")
        return []

class ActionSalesTrendForSeason(Action):
    def name(self) -> Text:
        return "action_sales_trend_for_season"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        season = tracker.get_slot('season')
        year = datetime.now().year

        if season == 'summer':
            start_date = datetime(year, 6, 1)
            end_date = datetime(year, 8, 31)
        elif season == 'winter':
            start_date = datetime(year, 12, 1)
            end_date = datetime(year, 2, 28) if (datetime(year, 2, 28).month == 2) else datetime(year, 2, 29)
        elif season == 'spring':
            start_date = datetime(year, 3, 1)
            end_date = datetime(year, 5, 31)
        elif season == 'autumn':
            start_date = datetime(year, 9, 1)
            end_date = datetime(year, 11, 30)
        else:
            dispatcher.utter_message(text="Please specify a valid season (summer, winter, spring, autumn).")
            return []
        data_manager = DataManager()
        df = data_manager.get_data()
        data = get_filtered_data(df, start_date, end_date)
        total_sales = data['salescount'].sum()

        dispatcher.utter_message(text=f"Total sales for {season.capitalize()} {year} were ${total_sales:.2f}.")
        return []

class ActionAverageSalesPerTransaction(Action):
    def name(self) -> Text:
        return "action_average_sales_per_transaction"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        average_sales = df['salescount'].mean()
        dispatcher.utter_message(text=f"The average sales per transaction is ${average_sales:.2f}.")
        return []
class ActionSalesGrowthPercentage(Action):
    def name(self) -> Text:
        return "action_sales_growth_percentage"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        # Example logic for growth calculation
        current_year = pd.Timestamp.now().year
        last_year = current_year - 1
        current_sales = df[df['PurchaseYear'] == current_year]['salescount'].sum()
        last_year_sales = df[df['PurchaseYear'] == last_year]['salescount'].sum()
        growth_percentage = ((current_sales - last_year_sales) / last_year_sales) * 100 if last_year_sales > 0 else 0
        dispatcher.utter_message(text=f"The sales growth percentage from last year to this year is {growth_percentage:.2f}%.")
        return []
class ActionAverageSalesPerPlan(Action):
    def name(self) -> Text:
        return "action_average_sales_per_plan"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        average_sales_per_plan = df.groupby('PlanName')['salescount'].mean()
        dispatcher.utter_message(text=f"The average sales per plan are as follows:\n{average_sales_per_plan.to_string()}.")
        return []
class ActionLongTermSalesTrends(Action):
    def name(self) -> Text:
        return "action_long_term_sales_trends"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        trend_data = df.groupby('PurchaseYear')['salescount'].sum()
        dispatcher.utter_message(text=f"Long-term sales trends are as follows:\n{trend_data.to_string()}.")
        return []
class ActionSalesTrendChange(Action):
    def name(self) -> Text:
        return "action_sales_trend_change"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        trend_change = df.groupby('PurchaseYear')['salescount'].sum().pct_change().mean()
        trend_result = "increased" if trend_change > 0 else "decreased"
        dispatcher.utter_message(text=f"The average sales trend has {trend_result} over the years.")
        return []
class ActionSeasonalSalesTrend(Action):
    def name(self) -> Text:
        return "action_seasonal_sales_trend"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        season = tracker.get_slot('season')
        df = DataManager().get_data()
        if season:
            season_months = {
                'spring': [3, 4, 5],
                'summer': [6, 7, 8],
                'autumn': [9, 10, 11],
                'winter': [12, 1, 2]
            }
            if season in season_months:
                months = season_months[season]
                seasonal_sales = df[df['PurchaseMonth'].isin(months)]['salescount'].sum()
                dispatcher.utter_message(text=f"Total sales during {season} are ${seasonal_sales:.2f}.")
            else:
                dispatcher.utter_message(text="Please specify a valid season (spring, summer, autumn, winter).")
        else:
            dispatcher.utter_message(text="Please specify the season for the sales trend analysis.")
        return []
class ActionSalesForProductMonthYear(Action):
    def name(self) -> Text:
        return "action_sales_for_product_month_year"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        month = tracker.get_slot('month')
        year = tracker.get_slot('year')
        product = tracker.get_slot('plan')
        
        if not month or not year or not product:
            dispatcher.utter_message(text="Please provide the product, month, and year for the sales data.")
            return []

        try:
            month = int(month)
            year = int(year)
            if month < 1 or month > 12:
                dispatcher.utter_message(text="Please provide a valid month (1-12).")
                return []
        except ValueError:
            dispatcher.utter_message(text="Please provide valid month and year.")
            return []
        
        start_date = datetime(year, month, 1)
        end_date = (start_date + pd.DateOffset(months=1)) - pd.DateOffset(days=1)
        
        df = DataManager().get_data()
        data = get_filtered_data(df, start_date, end_date, plan=product)
        total_sales = data['salescount'].sum()
        
        dispatcher.utter_message(text=f"Total sales for the product '{product}' in {month}/{year} were ${total_sales:.2f}.")
        return []
class ActionSalesSummaryForPlanLast6Months(Action):
    def name(self) -> Text:
        return "action_sales_summary_for_plan_last_6_months"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        plan = tracker.get_slot('plan')
        df = DataManager().get_data()
        end_date = pd.Timestamp.now().date()
        start_date = end_date - pd.DateOffset(months=6)
        
        if plan:
            data = get_filtered_data(df, start_date, end_date, plan=plan)
            total_sales = data['salescount'].sum()
            dispatcher.utter_message(text=f"Total sales for the plan '{plan}' in the last 6 months were ${total_sales:.2f}.")
        else:
            dispatcher.utter_message(text="Please specify the plan for the sales summary.")
        return []
class ActionMonthlySalesVariationLastYear(Action):
    def name(self) -> Text:
        return "action_monthly_sales_variation_last_year"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        year = tracker.get_slot('year')
        
        try:
            year = int(year)
        except ValueError:
            dispatcher.utter_message(text="Please provide a valid year.")
            return []
        
        df = DataManager().get_data()
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        data = get_filtered_data(df, start_date, end_date)
        
        monthly_sales = data.groupby(data['PurchaseDate'].dt.month)['salescount'].sum()
        sales_variation = monthly_sales.pct_change().mean()
        variation_result = "increased" if sales_variation > 0 else "decreased"
        
        dispatcher.utter_message(text=f"Sales variation for each month in {year} has {variation_result}.")
        return []
class ActionCorrelationWithMarketingSpend(Action):
    def name(self) -> Text:
        return "action_correlation_with_marketing_spend"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        # Assuming there is a column 'MarketingSpend' in your dataframe
        correlation = df[['salescount', 'MarketingSpend']].corr().iloc[0, 1]
        dispatcher.utter_message(text=f"The correlation between sales and marketing spend is {correlation:.2f}.")
        return []
class ActionKeyDriversOfSales(Action):
    def name(self) -> Text:
        return "action_key_drivers_of_sales"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        # Assuming there are key features like 'MarketingSpend', 'Region', 'PlanName'
        key_drivers = df[['salescount', 'MarketingSpend', 'Region', 'PlanName']].mean()
        dispatcher.utter_message(text=f"Key drivers of sales include average Marketing Spend: ${key_drivers['MarketingSpend']:.2f}, Region: {key_drivers['Region']}, and Plan Name: {key_drivers['PlanName']}.")
        return []
class ActionSalesPercentageIncreaseByMonth(Action):
    def name(self) -> Text:
        return "action_sales_percentage_increase_by_month"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        year = tracker.get_slot('year')
        
        try:
            year = int(year)
        except ValueError:
            dispatcher.utter_message(text="Please provide a valid year.")
            return []
        
        df = DataManager().get_data()
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        data = get_filtered_data(df, start_date, end_date)
        
        monthly_sales = data.groupby(data['PurchaseDate'].dt.month)['salescount'].sum()
        sales_percentage_increase = monthly_sales.pct_change() * 100
        dispatcher.utter_message(text=f"Sales percentage increase by month in {year}: {sales_percentage_increase.to_dict()}.")
        return []
class ActionSalesPercentageIncreaseByYear(Action):
    def name(self) -> Text:
        return "action_sales_percentage_increase_by_year"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_year = tracker.get_slot('year')
        
        try:
            current_year = int(current_year)
        except ValueError:
            dispatcher.utter_message(text="Please provide a valid year.")
            return []
        
        df = DataManager().get_data()
        previous_year = current_year - 1
        
        start_date_current = datetime(current_year, 1, 1)
        end_date_current = datetime(current_year, 12, 31)
        start_date_previous = datetime(previous_year, 1, 1)
        end_date_previous = datetime(previous_year, 12, 31)
        
        current_year_sales = get_filtered_data(df, start_date_current, end_date_current)['salescount'].sum()
        previous_year_sales = get_filtered_data(df, start_date_previous, end_date_previous)['salescount'].sum()
        
        percentage_increase = ((current_year_sales - previous_year_sales) / previous_year_sales) * 100
        dispatcher.utter_message(text=f"The sales percentage increase from {previous_year} to {current_year} is {percentage_increase:.2f}%.")
        return []
class ActionTotalNumberOfPlans(Action):
    def name(self) -> Text:
        return "action_total_number_of_plans"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        total_plans = df['PlanName'].nunique()
        dispatcher.utter_message(text=f"The total number of unique plans is {total_plans}.")
        return []
class ActionNamesOfAllPlans(Action):
    def name(self) -> Text:
        return "action_names_of_all_plans"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        plans = df['PlanName'].unique()
        plans_list = ', '.join(plans)
        dispatcher.utter_message(text=f"The names of all available plans are: {plans_list}.")
        return []
class ActionNamesOfAllCountries(Action):
    def name(self) -> Text:
        return "action_names_of_all_countries"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        countries = df['countryname'].unique()
        countries_list = ', '.join(countries)
        dispatcher.utter_message(text=f"The names of all available countries are: {countries_list}.")
        return []
class ActionTotalSalesByCity(Action):
    def name(self) -> Text:
        return "action_total_sales_by_city"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        city = tracker.get_slot('city')
        
        if not city:
            dispatcher.utter_message(text="Please provide the name of the city.")
            return []
        
        df = DataManager().get_data()
        city_sales = df[df['city'] == city]['salescount'].sum()
        dispatcher.utter_message(text=f"Total sales in {city} are ${city_sales:.2f}.")
        return []
class ActionCurrentMonthSalesVsPreviousMonth(Action):
    def name(self) -> Text:
        return "action_current_month_sales_vs_previous_month"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        year = tracker.get_slot('year')
        month = tracker.get_slot('month')
        
        try:
            year = int(year)
            month = int(month)
            if month < 1 or month > 12:
                dispatcher.utter_message(text="Please provide a valid month (1-12).")
                return []
        except ValueError:
            dispatcher.utter_message(text="Please provide valid year and month.")
            return []
        
        df = DataManager().get_data()
        current_month_start = datetime(year, month, 1)
        current_month_end = (current_month_start + pd.DateOffset(months=1)) - pd.DateOffset(days=1)
        
        previous_month_start = (current_month_start - pd.DateOffset(months=1)).replace(day=1)
        previous_month_end = (previous_month_start + pd.DateOffset(months=1)) - pd.DateOffset(days=1)
        
        current_month_sales = get_filtered_data(df, current_month_start, current_month_end)['salescount'].sum()
        previous_month_sales = get_filtered_data(df, previous_month_start, previous_month_end)['salescount'].sum()
        
        sales_comparison = current_month_sales - previous_month_sales
        dispatcher.utter_message(text=f"Sales in {month}/{year} compared to the previous month is ${sales_comparison:.2f}.")
        return []
class ActionMostCommonSource(Action):
    def name(self) -> Text:
        return "action_most_common_source"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        most_common_source = df['source'].mode()[0]
        dispatcher.utter_message(text=f"The most common source of sales is {most_common_source}.")
        return []

class ActionSalesStatisticsBySource(Action):
    def name(self) -> Text:
        return "action_sales_statistics_by_source"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        sales_stats = df.groupby('source')['salescount'].agg(['sum', 'mean', 'count'])
        sales_stats_message = sales_stats.to_string()
        dispatcher.utter_message(text=f"Sales statistics by source:\n{sales_stats_message}")
        return []

class ActionHighestRevenueSource(Action):
    def name(self) -> Text:
        return "action_highest_revenue_source"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        highest_revenue_source = df.groupby('source')['salescount'].sum().idxmax()
        dispatcher.utter_message(text=f"The source that has generated the highest revenue is {highest_revenue_source}.")
        return []

class ActionSalesTrendBySource(Action):
    def name(self) -> Text:
        return "action_sales_trend_by_source"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        trend = df.groupby(['PurchaseDate', 'source'])['salescount'].sum().unstack().pct_change().mean()
        trend_message = trend.to_string()
        dispatcher.utter_message(text=f"Trend of sales by source over the past year:\n{trend_message}")
        return []


class ActionLowestSalesFiguresSource(Action):
    def name(self) -> Text:
        return "action_lowest_sales_figures_source"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        lowest_sales_source = df.groupby('source')['salescount'].sum().idxmin()
        dispatcher.utter_message(text=f"The source with the lowest sales figures is {lowest_sales_source}.")
        return []

class ActionCustomerAcquisitionBySource(Action):
    def name(self) -> Text:
        return "action_customer_acquisition_by_source"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        acquisition = df.groupby('source')['CustomerID'].nunique()
        acquisition_message = acquisition.to_string()
        dispatcher.utter_message(text=f"Customer acquisition by source:\n{acquisition_message}")
        return []

class ActionPercentageOfTotalSalesBySource(Action):
    def name(self) -> Text:
        return "action_percentage_of_total_sales_by_source"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        total_sales = df['salescount'].sum()
        sales_percentage = df.groupby('source')['salescount'].sum() / total_sales * 100
        percentage_message = sales_percentage.to_string()
        dispatcher.utter_message(text=f"Percentage of total sales by source:\n{percentage_message}")
        return []

class ActionMostFrequentPaymentGateway(Action):
    def name(self) -> Text:
        return "action_most_frequent_payment_gateway"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        most_frequent_gateway = df['payment_gateway'].mode()[0]
        dispatcher.utter_message(text=f"The payment gateway used most frequently is {most_frequent_gateway}.")
        return []

class ActionSalesBreakdownByPaymentGateway(Action):
    def name(self) -> Text:
        return "action_sales_breakdown_by_payment_gateway"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        sales_breakdown = df.groupby('payment_gateway')['salescount'].agg(['sum', 'mean', 'count'])
        breakdown_message = sales_breakdown.to_string()
        dispatcher.utter_message(text=f"Breakdown of sales by payment gateway:\n{breakdown_message}")
        return []

class ActionHighestTransactionVolumeGateway(Action):
    def name(self) -> Text:
        return "action_highest_transaction_volume_gateway"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        highest_volume_gateway = df.groupby('payment_gateway')['salescount'].count().idxmax()
        dispatcher.utter_message(text=f"The payment gateway with the highest transaction volume is {highest_volume_gateway}.")
        return []

class ActionSalesTrendByPaymentGateway(Action):
    def name(self) -> Text:
        return "action_sales_trend_by_payment_gateway"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        trend = df.groupby(['PurchaseDate', 'payment_gateway'])['salescount'].sum().unstack().pct_change().mean()
        trend_message = trend.to_string()
        dispatcher.utter_message(text=f"Trend of sales through different payment gateways:\n{trend_message}")
        return []

class ActionSuccessRateComparisonBetweenGateways(Action):
    def name(self) -> Text:
        return "action_success_rate_comparison_between_gateways"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        # Assuming 'status' column indicates transaction success
        success_rate = df[df['status'] == 'successful'].groupby('payment_gateway').size() / df.groupby('payment_gateway').size()
        success_rate_message = success_rate.to_string()
        dispatcher.utter_message(text=f"Success rate of transactions by payment gateway:\n{success_rate_message}")
        return []

class ActionLowestTransactionFeesGateway(Action):
    def name(self) -> Text:
        return "action_lowest_transaction_fees_gateway"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        # Placeholder logic - update if you have transaction fees data
        # Assuming you have 'transaction_fees' column in your data
        lowest_fees_gateway = df.groupby('payment_gateway')['transaction_fees'].mean().idxmin()
        dispatcher.utter_message(text=f"The payment gateway with the lowest transaction fees is {lowest_fees_gateway}.")
        return []

class ActionAverageTransactionAmountByGateway(Action):
    def name(self) -> Text:
        return "action_average_transaction_amount_by_gateway"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        average_amount = df.groupby('payment_gateway')['salescount'].mean()
        average_amount_message = average_amount.to_string()
        dispatcher.utter_message(text=f"Average transaction amount for each payment gateway:\n{average_amount_message}")
        return []

class ActionPercentageOfTotalSalesByGateway(Action):
    def name(self) -> Text:
        return "action_percentage_of_total_sales_by_gateway"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        total_sales = df['salescount'].sum()
        sales_percentage = df.groupby('payment_gateway')['salescount'].sum() / total_sales * 100
        percentage_message = sales_percentage.to_string()
        dispatcher.utter_message(text=f"Percentage of total sales processed through each payment gateway:\n{percentage_message}")
        return []

class ActionTop10PercentSalesGateways(Action):
    def name(self) -> Text:
        return "action_top_10_percent_sales_gateways"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        top_10_percent_value = df['salescount'].quantile(0.9)
        top_gateways = df[df['salescount'] >= top_10_percent_value]['payment_gateway'].unique()
        top_gateways_message = ', '.join(top_gateways)
        dispatcher.utter_message(text=f"The payment gateways that contributed to the top 10% of sales are: {top_gateways_message}.")
        return []


class ActionTotalSalesRevenueThisYear(Action):
    def name(self) -> Text:
        return "action_total_sales_revenue_this_year"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        df['revenue'] = df['sellingprice'] * df['salescount']
        total_revenue = df[df['year'] == current_year]['revenue'].sum()
        dispatcher.utter_message(text=f"The total sales revenue for this year is ${total_revenue:.2f}.")
        return []

class ActionMonthlySalesRevenueThisYear(Action):
    def name(self) -> Text:
        return "action_monthly_sales_revenue_this_year"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        df['revenue'] = df['sellingprice'] * df['salescount']
        monthly_revenue = df[df['year'] == current_year].groupby('month')['revenue'].sum()
        result = ', '.join([f'{month}: ${revenue:.2f}' for month, revenue in monthly_revenue.items()])
        dispatcher.utter_message(text=f"The sales revenue for each month of this year is as follows: {result}.")
        return []

class ActionHighestSalesRevenueProduct(Action):
    def name(self) -> Text:
        return "action_highest_sales_revenue_product"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        df['revenue'] = df['sellingprice'] * df['salescount']
        highest_revenue_product = df.groupby('product')['revenue'].sum().idxmax()
        dispatcher.utter_message(text=f"The product or service with the highest sales revenue is {highest_revenue_product}.")
        return []

class ActionQuarterlyRevenueComparison(Action):
    def name(self) -> Text:
        return "action_quarterly_revenue_comparison"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        df['revenue'] = df['sellingprice'] * df['salescount']
        quarterly_revenue = df.groupby(['year', 'quarter'])['revenue'].sum().unstack()
        comparison = quarterly_revenue.diff(axis=1).iloc[:, -1].mean()
        dispatcher.utter_message(text=f"The sales revenue for this quarter {'increased' if comparison > 0 else 'decreased'} by ${abs(comparison):.2f} compared to the last quarter.")
        return []

class ActionTotalSalesRevenueByRegion(Action):
    def name(self) -> Text:
        return "action_total_sales_revenue_by_region"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        df['revenue'] = df['sellingprice'] * df['salescount']
        revenue_by_region = df.groupby('region')['revenue'].sum()
        result = ', '.join([f'{region}: ${revenue:.2f}' for region, revenue in revenue_by_region.items()])
        dispatcher.utter_message(text=f"The total sales revenue for each region or country is as follows: {result}.")
        return []

class ActionHolidaySeasonRevenue(Action):
    def name(self) -> Text:
        return "action_holiday_season_revenue"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        df['revenue'] = df['sellingprice'] * df['salescount']
        holiday_revenue = df[df['season'] == 'holiday']['revenue'].sum()
        dispatcher.utter_message(text=f"The revenue generated from sales during the holiday season is ${holiday_revenue:.2f}.")
        return []

class ActionSalesRevenuePercentageIncrease(Action):
    def name(self) -> Text:
        return "action_sales_revenue_percentage_increase"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        df['revenue'] = df['sellingprice'] * df['salescount']
        revenue_last_year = df[df['year'] == (current_year - 1)]['revenue'].sum()
        revenue_this_year = df[df['year'] == current_year]['revenue'].sum()
        percentage_increase = ((revenue_this_year - revenue_last_year) / revenue_last_year) * 100
        dispatcher.utter_message(text=f"The percentage increase in sales revenue compared to the previous year is {percentage_increase:.2f}%.")
        return []

class ActionTotalProfit(Action):
    def name(self) -> Text:
        return "action_total_profit"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        total_profit = (df['SellingPrice'] - df['CompanyBuyingPrice']).sum()
        dispatcher.utter_message(text=f"The total profit made from sales is {total_profit}.")
        return []

class ActionProfitMarginPerProduct(Action):
    def name(self) -> Text:
        return "action_profit_margin_per_product"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        df['profit_margin'] = (df['SellingPrice'] - df['CompanyBuyingPrice']) / df['SellingPrice']
        margins = df.groupby('PlanName')['profit_margin'].mean().reset_index()
        margins_list = margins.to_dict(orient='records')
        response = "\n".join([f"{row['PlanName']}: {row['profit_margin']:.2%}" for row in margins_list])
        dispatcher.utter_message(text=f"Profit margin for each product or service:\n{response}")
        return []

class ActionHighestProfitMargin(Action):
    def name(self) -> Text:
        return "action_highest_profit_margin"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        df['profit_margin'] = (df['SellingPrice'] - df['CompanyBuyingPrice']) / df['SellingPrice']
        highest_margin_product = df.groupby('PlanName')['profit_margin'].mean().idxmax()
        highest_margin_value = df.groupby('PlanName')['profit_margin'].mean().max()
        dispatcher.utter_message(text=f"The product or service with the highest profit margin is {highest_margin_product} with a margin of {highest_margin_value:.2%}.")
        return []

class ActionProfitChangeLastYear(Action):
    def name(self) -> Text:
        return "action_profit_change_last_year"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        df['profit'] = df['SellingPrice'] - df['CompanyBuyingPrice']
        df['PurchaseDate'] = pd.to_datetime(df['PurchaseDate'])
        df.set_index('PurchaseDate', inplace=True)
        yearly_profit = df['profit'].resample('Y').sum()
        profit_change = yearly_profit.pct_change().iloc[-1]
        dispatcher.utter_message(text=f"The profit has {'increased' if profit_change > 0 else 'decreased'} over the past year by {abs(profit_change):.2%}.")
        return []

class ActionAverageProfitPerTransaction(Action):
    def name(self) -> Text:
        return "action_average_profit_per_transaction"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        df['profit'] = df['SellingPrice'] - df['CompanyBuyingPrice']
        average_profit = df['profit'].mean()
        dispatcher.utter_message(text=f"The average profit per transaction is {average_profit:.2f}.")
        return []

class ActionProfitByRegion(Action):
    def name(self) -> Text:
        return "action_profit_by_region"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        df['profit'] = df['SellingPrice'] - df['CompanyBuyingPrice']
        region_profit = df.groupby('regionname')['profit'].sum().reset_index()
        region_profit_list = region_profit.to_dict(orient='records')
        response = "\n".join([f"{row['regionname']}: {row['profit']:.2f}" for row in region_profit_list])
        dispatcher.utter_message(text=f"Profit by region or country:\n{response}")
        return []

class ActionQuarterlyProfitComparison(Action):
    def name(self) -> Text:
        return "action_quarterly_profit_comparison"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        df['profit'] = df['SellingPrice'] - df['CompanyBuyingPrice']
        df['PurchaseDate'] = pd.to_datetime(df['PurchaseDate'])
        df.set_index('PurchaseDate', inplace=True)
        quarterly_profit = df['profit'].resample('Q').sum()
        current_quarter = quarterly_profit.index[-1]
        previous_quarter = quarterly_profit.index[-2]
        comparison = quarterly_profit.loc[current_quarter] - quarterly_profit.loc[previous_quarter]
        dispatcher.utter_message(text=f"The profit for the current quarter is {'higher' if comparison > 0 else 'lower'} compared to the previous quarter by {abs(comparison):.2f}.")
        return []

class ActionTopProductsByProfit(Action):
    def name(self) -> Text:
        return "action_top_products_by_profit"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        df['profit'] = df['SellingPrice'] - df['CompanyBuyingPrice']
        top_products = df.groupby('PlanName')['profit'].sum().nlargest(5).reset_index()
        top_products_list = top_products.to_dict(orient='records')
        response = "\n".join([f"{row['PlanName']}: {row['profit']:.2f}" for row in top_products_list])
        dispatcher.utter_message(text=f"Top five products or services by profit:\n{response}")
        return []

class ActionProfitPercentageOfRevenue(Action):
    def name(self) -> Text:
        return "action_profit_percentage_of_revenue"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        df['profit'] = df['SellingPrice'] - df['CompanyBuyingPrice']
        total_revenue = df['SellingPrice'].sum()
        total_profit = df['profit'].sum()
        profit_percentage = (total_profit / total_revenue) * 100
        dispatcher.utter_message(text=f"The percentage of total revenue that is profit is {profit_percentage:.2f}%.")
        return []

class ActionProfitBySource(Action):
    def name(self) -> Text:
        return "action_profit_by_source"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df = DataManager().get_data()
        df['profit'] = df['SellingPrice'] - df['CompanyBuyingPrice']
        source_profit = df.groupby('source')['profit'].sum().reset_index()
        source_profit_list = source_profit.to_dict(orient='records')
        response = "\n".join([f"{row['source']}: {row['profit']:.2f}" for row in source_profit_list])
        dispatcher.utter_message(text=f"Profit breakdown by source:\n{response}")
        return []
