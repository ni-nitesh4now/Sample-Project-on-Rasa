# actions.py
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from datetime import datetime

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
    
class ActionGetMonthDouble(Action):

    def name(self) -> Text:
        return "action_get_month_double"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extracting the month name from the user's message
        user_message = tracker.latest_message.get('text').strip()
        
        month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        
        if user_message in month_names:
            month_index = month_names.index(user_message) + 1  # Month number (1-12)
            result = month_index * 2  # Double of the month number
            
            dispatcher.utter_message(text=f"The double of {user_message} is {result}.")
        else:
            dispatcher.utter_message(text="I couldn't recognize that month name.")

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