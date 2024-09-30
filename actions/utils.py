import re
from datetime import datetime
from datetime import datetime
import pandas as pd
import re
from dateutil.relativedelta import relativedelta
import logging
logging.basicConfig(level=logging.INFO)
from datetime import timedelta


# df = pd.read_excel('cleaned_airhub_data.xlsx')

# logging.info("loaded")
# logging.info(df.info())

months = { 'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3, 'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7, 'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'sept': 9, 'october': 10, 'oct': 10, 'november': 11, 'nov': 11, 'december': 12, 'dec': 12 }
months_reverse = {v: k for k, v in months.items()}
word_to_num = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12
}



def get_month_range_from_text(text):
    pattern = r'last\s+(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+(month|months)\s*'
    match = re.search(pattern, text, re.IGNORECASE)

    if not match:
        return 0
    month_input = match.group(1)

    if month_input.isdigit():
        months = int(month_input)
    else:
        month_mapping = {
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
            'six': 6,
            'seven': 7,
            'eight': 8,
            'nine': 9,
            'ten': 10,
            'eleven': 11,
            'twelve': 12
        }
        months = month_mapping[month_input.lower()]
    today = datetime.today()
    start_date = (today.replace(day=1) - timedelta(days=30 * months)).replace(day=1)
    end_date = today
    start_date_str = start_date.strftime("%d/%m/%Y")
    end_date_str = end_date.strftime("%d/%m/%Y")
    return [start_date_str, end_date_str],months
    

def extract_months(text):
    pattern = r'\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b'
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    month_digits = [months[match.lower()] for match in matches]
    
    return month_digits

def extract_years(text):
    # Regular expression to match years in YYYY format without capturing the century separately
    pattern = r'\b(?:19|20)\d{2}\b'
    years = re.findall(pattern, text)
    
    return [int(year) for year in years]


def extract_month_year(text):    
    pattern = r'\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s*(?:of\s*)?(\d{4})\b'
    matches = re.findall(pattern, text, re.IGNORECASE)
    month_year_pairs = [[months[month.lower()], int(year)] for month, year in matches]
    
    return month_year_pairs

def extract_and_format_dates(sentence):
    date_pattern = r'\b(?:\d{1,2}(?:th|st|nd|rd)?\s(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s\d{2,4}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b'
    
    dates = re.findall(date_pattern, sentence)
    
    formatted_dates = []
    
    for date in dates:
        try:
            if re.search(r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b', date):  # Matches dd/mm/yyyy or dd-mm-yyyy
                dt = datetime.strptime(date, '%d/%m/%Y') if '/' in date else datetime.strptime(date, '%d-%m-%Y')
            elif re.search(r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b', date):  # Matches yyyy/mm/dd or yyyy-mm-dd
                dt = datetime.strptime(date, '%Y/%m/%d') if '/' in date else datetime.strptime(date, '%Y-%m-%d')
            else:  # Matches dd Month yyyy (e.g., 12 October 2024)
                clean_date = re.sub(r'(th|st|nd|rd)', '', date).strip()
                dt = datetime.strptime(clean_date, '%d %B %Y')
            
            formatted_dates.append(dt.strftime('%d/%m/%Y'))
        except ValueError:
            continue 
    
    return formatted_dates

def calculate_total_and_average_sales(df, user_message):
    total_sales = 0
    sales_count = 0
    results = []

    # Check for sales on specific date(s) 
    dates = extract_and_format_dates(user_message)
    logging.info(dates)
    if dates:
        for date_str in dates:
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            filtered_df = df[df['PurchaseDate'].dt.date == date_obj.date()]
            total_sales += filtered_df['SellingPrice'].sum()
            logging.info(total_sales)
            sales_count += filtered_df.shape[0]
            average_sales = total_sales / sales_count if sales_count > 0 else 0
            logging.info(average_sales)
            results.append((date_str, [total_sales, average_sales]))
        return results
        
    # Check for last X months request
    total_sales = 0
    sales_count = 0
    results = []
    if "last" in user_message and ("month" in user_message or "months" in user_message):
        logging.info("Processing request for total and average sales over last months...")
        month_range, digit_in_last_month = get_month_range_from_text(user_message)
        start_date = month_range[0]
        start_date_obj = datetime.strptime(start_date, '%d/%m/%Y')
        filtered_df = df[df['PurchaseDate'].dt.date >= start_date_obj.date()]
        total_sales += filtered_df['SellingPrice'].sum()
        average_sales = total_sales / digit_in_last_month if digit_in_last_month > 0 else 0
        results.append((f"{digit_in_last_month} month", [total_sales, average_sales]))
        return results

    
    # If both months and years are mentioned
    total_sales = 0
    sales_count = 0
    results = []
    month_year_pairs = extract_month_year(user_message)
    if month_year_pairs:
        logging.info("Calculating total and average sales for specified months and years...")
        for month, year in month_year_pairs:
            filtered_sales = df[(df['PurchaseDate'].dt.month == month) & (df['PurchaseDate'].dt.year == year)]
            total_sales = filtered_sales['SellingPrice'].sum()
            days_in_month = pd.Period(year=year, month=month, freq='M').days_in_month
            average_sales = total_sales / days_in_month if days_in_month > 0 else 0
            
            logging.info([total_sales, average_sales])
            
            # Append results with formatted month-year string
            results.append((f"{month}/{year}", [total_sales, average_sales]))
        return results

            
    # Extract years and months from user input for other cases
    years = extract_years(user_message)
    months_extracted = extract_months(user_message)

    total_sales = 0.0
    num_months = 0
    
    # If only months are mentioned (without specific year)
    total_sales = 0
    sales_count = 0
    results = []
    if months_extracted:
        logging.info("Calculating total and average sales for specified months without a year...")
        current_year = pd.to_datetime('today').year  
        for month in months_extracted:
            total_sales = df[(df['PurchaseDate'].dt.month == month) & (df['PurchaseDate'].dt.year == current_year)]['SellingPrice'].sum()
            days_in_month = pd.Period(year=current_year, month=month, freq='M').days_in_month
            average_sales = total_sales / days_in_month if days_in_month > 0 else 0
            logging.info([total_sales, average_sales])
            results.append((f"{month}/{current_year}", [total_sales, average_sales]))
        return results
        
    # If only years are mentioned
    total_sales = 0
    sales_count = 0
    results = []
    if years:
        for year in years:
            filtered_sales = df[(df['PurchaseDate'].dt.year == year)]
            total_sales = filtered_sales['SellingPrice'].sum()
            average_sales = total_sales / 12
            
            logging.info([total_sales, average_sales])
            # Append results with formatted month-year string
            results.append((year, [total_sales, average_sales]))
        return results


    total_sales = df["SellingPrice"].sum()
    average_sales=0
    logging.info([total_sales, average_sales])
    results.append((f"All time", [total_sales, average_sales]))
    return results




######################################################################################################
#For countries


def extract_country(text,country_names):
    pattern = r'\b(' + '|'.join(map(re.escape, country_names)) + r')\b'
    
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(0).lower()  
    return None


def calculate_country_data(df,user_message):
    source_country = df['country_source'].dropna().unique().tolist()
    country_names = df['countryname'].dropna().unique().tolist()
    source = df['source'].dropna().unique().tolist()
    operators = df['OperatorType'].dropna().unique().tolist()
    cities = df['city'].dropna().unique().tolist()

    extracted_values = []
    for ref in df['Refsite'].dropna():
        parts = ref.split('=')
        if len(parts) > 1:
            extracted_values.append(parts[1].strip())
    value_counts = pd.Series(extracted_values).value_counts()
    refSites = value_counts.to_dict()







    
