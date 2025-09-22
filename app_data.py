import streamlit as st
import pandas as pd
import numpy as np
from google.cloud import storage
import os
from io import StringIO
import json

gcp_credentials = os.getenv("GCP_CREDENTIALS")
gcp_credentials = json.loads(gcp_credentials)
bucket_name = "nova-power-cloud-storage-buckett"
def get_file_gcs(bucket_name, blob_name):
    client = storage.Client.from_service_account_info(gcp_credentials)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    if blob.name.endswith('.json'):
        data = blob.download_as_text()
        return json.loads(data)
    elif blob.name.endswith('.csv'):
        data = blob.download_as_text()
        return pd.read_csv(StringIO(data))

invoices_year = get_file_gcs(bucket_name, 'invoices_year.csv')
items = get_file_gcs(bucket_name, 'items.csv')
purchases = get_file_gcs(bucket_name, 'purchases.csv')
with_incoming = get_file_gcs(bucket_name, 'with_quantity.csv')
with_incoming['item_id'] = with_incoming['item_id'].astype(str)

invoices_year['date'] = pd.to_datetime(invoices_year['date'])

def get_last_60_days(df, item_name, last_sale, last_sale_minus_60):
    df_ = df[df['item_name'] == item_name]
    return df_[(pd.to_datetime(df_['date']) <= pd.to_datetime(last_sale)) & (pd.to_datetime(df_['date']) >= pd.to_datetime(last_sale_minus_60))].groupby(['item_name', 'item_id']).agg({'item_quantity': 'sum'}).reset_index().iloc[0]['item_quantity']

last_purchase = invoices_year.groupby(['item_name', 'item_id']).agg({'date': 'max'}).reset_index().rename(columns={'date': 'last_sale'})
last_purchase = last_purchase[last_purchase['item_name'] != '']
last_purchase = last_purchase.drop(columns=['item_id'])
last_purchase['last_sale_minus_60'] = pd.to_datetime(last_purchase['last_sale']) - pd.Timedelta(days=60)
last_purchase.loc[last_purchase['last_sale_minus_60'].dt.year < 2025, 'last_sale_minus_60'] = pd.to_datetime('2025-01-01')
last_purchase['purchase_last_60'] = last_purchase.apply(lambda x: get_last_60_days(invoices_year, x['item_name'], x['last_sale'], x['last_sale_minus_60']), axis=1)

stock_tracker = last_purchase.merge(with_incoming, how='left', on=['item_name'])

stock_tracker['check_stock'] = np.where(stock_tracker['available_stock'] < stock_tracker['purchase_last_60'], True, False)
stock_tracker['check_stock_soft'] = np.where((stock_tracker['available_stock'] + stock_tracker['incoming_quantity']) < stock_tracker['purchase_last_60'], True, False)



