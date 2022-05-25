# Imports
from statistics import quantiles
import pandas as pd
import datetime as dt
import warnings
warnings.filterwarnings('ignore')

# Data
df = pd.read_excel('C:\\Users\\DayanaCavalcante\\Documents\\Estudo\\Projects_Notes\\CustomerSegmentation\\OnlineRetail.xlsx')

# Data Exploration
data = df 
print(data.Country.nunique())
data.Country.unique()
customer_group = data[['Country', 'CustomerID']].drop_duplicates()
customer_group.groupby(['Country']).agg({'CustomerID':'count'}).reset_index().sort_values('CustomerID', ascending=False)

# More than 90% of the data is from UK. In this case I restricted the data to the UK only
data = data.loc[data['Country']=='United Kingdom']

# Check missing values
data.isnull().sum()

# Delete CustomerID null data
data = data[pd.notnull(data['CustomerID'])]

# Check negative quantity values
data.Quantity.min()

# Remove negative values
data = data[data['Quantity']>0]
print(data.shape)

# Info
print(data.info())

# Check unique value for each column
def unique_counts(data):
    for i in data.columns:
        count=data[i].nunique()
        print(i, ": ", count)
print(unique_counts(data))

# Add Total Price column
data['TotalPrice'] = data['Quantity']*data['UnitPrice']

# Check the first and last dates
data['InvoiceDate'].min()
data['InvoiceDate'].max()

now = dt.datetime(2011,12,10)
data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'])

#RFM
rfm = data.groupby('CustomerID').agg({'InvoiceDate': lambda x: (now - x.max()).days,
                                    'InvoiceNo': lambda x: len(x),
                                    'TotalPrice': lambda x: x.sum()})

rfm['InvoiceDate'] = rfm['InvoiceDate'].astype(int)
rfm.rename(columns={'InvoiceDate':'recency',
                    'InvoiceNo':'frequency',
                    'TotalPrice':'monetary_value'}, inplace=True)
print(rfm.head())

# This customer bought only once but in large quantity and the price of the product was very low
first_customer = data[data['CustomerID']== 12346.0]
print(first_customer)

# Dividing the metrics using quartiles
quantiles = rfm.quantile(q=[0.25,0.5,0.75])
quantiles = quantiles.to_dict()

# Create a segmented RFM
# The best customers are the ones with the lowest recency, the highest frequencies and monetary values
segmented_rfm = rfm

def RScore(x,p,d):
    if x <= d[p][0.25]:
        return 1
    elif x <= d[p][0.50]:
        return 2
    elif x <= d[p][0.75]:
        return 3
    else:
        return 4

def FMScore(x,p,d):
    if x <=d[p][0.25]:
        return 4
    elif x<=d[p][0.50]:
        return 3
    elif x <= d[p][0.75]:
        return 2
    else:
        return 1

segmented_rfm['r_quartile'] = segmented_rfm['recency'].apply(RScore, args=('recency', quantiles))
segmented_rfm['f_quartile'] = segmented_rfm['frequency'].apply(FMScore, args=('frequency',quantiles))
segmented_rfm['m_quartile'] = segmented_rfm['monetary_value'].apply(FMScore, args=('monetary_value',quantiles))
print(segmented_rfm.head())

segmented_rfm['RFMScore'] = segmented_rfm.r_quartile.map(str) + segmented_rfm.f_quartile.map(str) + segmented_rfm.m_quartile.map(str) 
print(segmented_rfm.head())

# 20 best customers
print(segmented_rfm[segmented_rfm['RFMScore']== '111'].sort_values('monetary_value', ascending=False).head(20))