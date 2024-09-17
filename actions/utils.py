import pandas as pd
import numpy as np
from datetime import datetime

class DataManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance.load_data()
        return cls._instance

    def load_data(self):
        # Load your data here
        self.df = pd.read_excel('airhub_data.xlsx')
        self.df = self.df.assign(
            country_source=self.df['country_source'].fillna('Unknown'),
            countryname=self.df['countryname'].fillna('Unknown'),
            regionname=self.df['regionname'].fillna('Unknown'),
            SellingPrice=self.df['SellingPrice'].fillna(0)
        )
        self.df['PurchaseDate'] = pd.to_datetime(self.df['PurchaseDate'], errors='coerce').dt.date
        self.df['TravelDate'] = pd.to_datetime(self.df['TravelDate'], errors='coerce')
        self.df['SellingPrice'] = pd.to_numeric(self.df['SellingPrice'], errors='coerce')
        self.df['CompanyBuyingPrice'] = pd.to_numeric(self.df['CompanyBuyingPrice'], errors='coerce')
        self.df = self.df.drop_duplicates().replace({'\\N': np.nan, 'undefined': np.nan, 'null': np.nan})
        self.df['salescount'] = self.df['SellingPrice'].apply(lambda x: 1 if pd.notnull(x) and x > 0 else 0).astype(int)
        self.df['vaildity'] = pd.to_numeric(self.df['vaildity'], errors='coerce')
        self.df['CompanyBuyingPrice'] = pd.to_numeric(self.df['CompanyBuyingPrice'], errors='coerce')
        self.df.dropna(subset=['SellingPrice', 'CompanyBuyingPrice'], inplace=True)
        self.df['PurchaseDate'] = pd.to_datetime(self.df['PurchaseDate'], errors='coerce')
        self.df['PurchaseYear'] = self.df['PurchaseDate'].dt.year
        self.df['PurchaseMonth'] = self.df['PurchaseDate'].dt.month
        self.df['day_of_week'] = self.df['PurchaseDate'].dt.weekday
        self.df['TravelYear'] = self.df['TravelDate'].dt.year
        self.df['TravelMonth'] = self.df['TravelDate'].dt.month
        self.df['SellingPrice'] = self.df['SellingPrice'].astype(float)

    def get_data(self):
        return self.df

def get_filtered_data(df, start_date=None, end_date=None, country=None, region=None, plan=None, specific_date=None,source=None, payment_gateway=None):
    mask = pd.Series([True] * len(df))
    
    if start_date and end_date:
        mask &= (df['PurchaseDate'] >= start_date) & (df['PurchaseDate'] <= end_date)
    if country:
        mask &= (df['countryname'] == country)
    if region:
        mask &= (df['regionname'] == region)
    if plan:
        mask &= (df['PlanName'] == plan)
    if specific_date:
        mask &= (df['PurchaseDate'] == specific_date)
    if source:
        mask &= (df['source'] == source)
    if payment_gateway:
        mask &= (df['payment_gateway'] == payment_gateway)

    filtered_data = df[mask]
    return filtered_data
