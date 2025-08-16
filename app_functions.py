import streamlit as st
import app_data
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd

# Convert 'date' to datetime for filtering

def plot_item_quantity(df, item_name, start_date, end_date):
    # Convert string dates to datetime
    df['date'] = pd.to_datetime(df['date'])
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter the dataframe
    filtered_df = df[
        (df['item_name'] == item_name) &
        (df['date'] >= start_date) &
        (df['date'] <= end_date)
    ]

    # Aggregate quantity per day
    quantity_per_day = filtered_df.groupby('date')['item_quantity'].sum().reset_index()

    # Plot using Plotly
    fig = px.bar(
        quantity_per_day,
        x='date',
        y='item_quantity',
        title=f"Daily Invoiced Quantity for '{item_name}' from {start_date.date()} to {end_date.date()}",
        labels={'item_quantity': 'Quantity', 'date': 'Date'}
    )
    fig.update_layout(xaxis_title='Date', yaxis_title='Invoiced Quantity', bargap=0.2)
    return fig


def plot_item_quantity_with_trend(df, item_name, start_date, end_date):
    df['date'] = pd.to_datetime(df['date'])
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter and group
    filtered_df = df[
        (df['item_name'] == item_name) &
        (df['date'] >= start_date) &
        (df['date'] <= end_date)
    ]
    quantity_per_day = filtered_df.groupby('date')['item_quantity'].sum().reset_index()

    # Compute rolling average (7-day window)
    quantity_per_day['rolling_avg'] = quantity_per_day['item_quantity'].rolling(window=7, min_periods=1).mean()

    # Create bar + line chart
    fig = go.Figure()

    # Bar trace
    fig.add_trace(go.Bar(
        x=quantity_per_day['date'],
        y=quantity_per_day['item_quantity'],
        name='Invoiced Quantity',
        marker_color='white',
        text=quantity_per_day['item_quantity'],
        textposition='inside',
        opacity=0.8
    ))

    # Line trace (smoothed trend)
    fig.add_trace(go.Scatter(
        x=quantity_per_day['date'],
        y=quantity_per_day['rolling_avg'],
        mode='lines',
        name='7-Day Rolling Avg',
        line=dict(color='orange', width=2)
    ))

    # Layout
    fig.update_layout(
        title=f"Daily Quantity for '{item_name}' with Trend for {start_date.date()} - {end_date.date()}",
        xaxis_title='Date',
        yaxis_title='Invoiced Quantity',
        bargap=0.2,
        template='plotly_dark'
    )

    return fig

def plot_stock_levels(df, item_name, bar_width=0.4):
    item_data = df[df['item_name'] == item_name]

    if item_data.empty:
        print("Item not found.")
        return

    stock = item_data['stock_on_hand'].values[0]
    incoming = item_data['incoming_quantity'].values[0]

    fig = go.Figure(data=[
        go.Bar(
            x=['Stock on Hand'],
            y=[stock],
            name='Stock on Hand',
            marker_color='lightblue',
            width=[bar_width],
            text=[stock],
            textposition='inside',
            opacity=.8
        ),
        go.Bar(
            x=['Incoming Quantity'],
            y=[incoming],
            name='Incoming Quantity',
            marker_color='orange',
            width=[bar_width],
            text=[incoming],
            textposition='inside',
            opacity=0.8
        )
    ])

    fig.update_layout(
        title=f"Stock Levels for '{item_name}'",
        yaxis_title='Quantity',
        xaxis_title='Stock Type',
        barmode='group',
        uniformtext_minsize=8,
        bargap=0.2,  # space between bars
        template='plotly_dark'
    )
    return fig

def show_invoiced_data(df, item_name, start_date, end_date):
    # Convert string dates to datetime
    df['date'] = pd.to_datetime(df['date'])
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter the dataframe
    filtered_df = df[
        (df['item_name'] == item_name) &
        (df['date'] >= start_date) &
        (df['date'] <= end_date)
    ]

    return filtered_df