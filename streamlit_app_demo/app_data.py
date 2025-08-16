import streamlit as st
import pandas as pd
import numpy as np

invoices_year = pd.read_csv('../sample_files/invoices_year.csv')
items = pd.read_csv('../sample_files/items.csv')
purchases = pd.read_csv('../sample_files/purchases.csv')
with_incoming = pd.read_csv('../sample_files/with_quantity.csv')
with_incoming['item_id'] = with_incoming['item_id'].astype(str)

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
