import streamlit as st
from app_data import invoices_year, with_incoming, stock_tracker
import datetime
from app_functions import plot_item_quantity, plot_item_quantity_with_trend, plot_stock_levels, show_invoiced_data

st.set_page_config(layout="wide", page_title='Nova Power Dashboard')

invoice_data = invoices_year.copy(deep=True)
item_data = with_incoming.copy(deep=True)

item_list = list(invoice_data['item_name'].unique())
item_list = [str(item) for item in item_list]
item_list = sorted(item_list)

st.header('Invoice Data for Selected Item and Stock Information')

main_col1, main_col2 = st.columns(2, gap='medium')

with main_col1:
    col1, col2, col3 = st.columns(3, gap='small')

    with col1:
        st.selectbox(label='Select Item: ', index=0, options=item_list, key='selection_item')
    with col2:
        st.date_input(label='Invoice Date Range: ', value=(datetime.date(2025, 1, 1), 'today'), min_value=datetime.date(2025, 1, 1), max_value='today', key='selection_date_range')

with main_col2:
    kpi1, kpi2 = st.columns(2, gap='small')

    with kpi1:
        metric_data = invoice_data[(invoice_data['item_name'] == st.session_state['selection_item']) & (invoice_data['date'] >= st.session_state['selection_date_range'][0]) & (invoice_data['date'] <= st.session_state['selection_date_range'][1])]
        mean_quant = round(metric_data['item_quantity'].mean(), 2)
        st.metric('Mean Invoiced Quantity for Selected Period', mean_quant, border=True)
    with kpi2:
        median_quant = round(metric_data['item_quantity'].median(), 2)
        st.metric('Median Invoiced Quantity for Selected Period', median_quant, border=True)


plot_col_1, plot_col_2 = st.columns(2, gap='medium')

with plot_col_1:
    plotly_fig = plot_item_quantity(df=invoice_data, item_name=st.session_state['selection_item'], start_date=st.session_state['selection_date_range'][0], end_date=st.session_state['selection_date_range'][1])
    plotly_fig_trend = plot_item_quantity_with_trend(df=invoice_data, item_name=st.session_state['selection_item'], start_date=st.session_state['selection_date_range'][0], end_date=st.session_state['selection_date_range'][1])
    st.plotly_chart(plotly_fig_trend)

with plot_col_2:
    plotly_stock = plot_stock_levels(df=item_data, item_name=st.session_state['selection_item'])
    st.plotly_chart(plotly_stock)

st.subheader('Invoice Data') 
st.dataframe(show_invoiced_data(df=invoice_data, item_name=st.session_state['selection_item'], start_date=st.session_state['selection_date_range'][0], end_date=st.session_state['selection_date_range'][1]), column_config={'id': None, 'item_id': None, 'date': st.column_config.DateColumn(format='MM-DD-YYYY'), 'total_amount': None}, hide_index=True)
st.divider()
st.header('Stock Tracker')
st.dataframe(stock_tracker[['item_name', 'last_sale', 'purchase_last_60', 'stock_on_hand', 'incoming_quantity', 'check_stock', 'check_stock_soft']].sort_values(by=['check_stock', 'incoming_quantity'], ascending=[False, False]), hide_index=True)
# st.dataframe(with_incoming)