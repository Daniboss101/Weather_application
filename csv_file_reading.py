from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
from dateutil.relativedelta import relativedelta
import os
import numpy as np
from pmdarima import auto_arima
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.holtwinters import ExponentialSmoothing


def process_temp(row):
    if pd.isnull(row['TMAX']) or pd.isnull(row['TMIN']):
        return pd.NA
    elif pd.isnull(row['TAVG']) or row['TAVG'] == 0:
        return (row['TMAX'] + row['TMIN']) / 2
    else:
        return row['TAVG']


def create_trendline(ax, x, y):
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    ax.plot(x, p(x), "r--", label="Trendline")


def import_year_file(csv_path):
    print("Import year file")
    columns_to_read = ['DATE', 'TAVG', 'TMAX', 'TMIN', 'PRCP']
    df = pd.read_csv(csv_path, usecols=columns_to_read)

    df['DATE'] = pd.to_datetime(df['DATE'], format='%Y')

    statistical_modeling_forecast(df[['DATE', 'TAVG']], 'year')

    end_date = datetime.now().year
    start_date = end_date - 10
    df_filtered = df[df['DATE'].dt.year >= start_date].copy()

    df_filtered['TAVG'] = df_filtered.apply(process_temp, axis=1)
    df_filtered = df_filtered.dropna(subset=['TAVG', 'PRCP'])
    file_name = 'AverageTemp_year'
    save_plot(df_filtered[['DATE', 'TAVG', 'PRCP']], file_name)
    return 'AverageTemp_year'


def import_month_file(csv_path):
    print("Import month file")
    columns_to_read = ['DATE', 'TAVG', 'TMAX', 'TMIN', 'PRCP']
    df = pd.read_csv(csv_path, usecols=columns_to_read)

    df['DATE'] = pd.to_datetime(df['DATE'], format='%Y-%m')

    end_date = datetime.now()
    start_date = end_date - relativedelta(years=10)
    df_statistically_filtered = df[(df['DATE'].dt.month == end_date.month)]
    statistical_modeling_forecast(df_statistically_filtered, 'month')

    df_filtered = df[(df['DATE'] >= start_date) & (df['DATE'].dt.month == end_date.month)]

    df_filtered['TAVG'] = df_filtered.apply(process_temp, axis=1)

    df_filtered = df_filtered.dropna(subset=['TAVG', 'PRCP'])

    df_filtered['DATE'] = df_filtered['DATE'].dt.strftime('%Y-%m')
    file_name = 'AverageTemp_month'
    save_plot(df_filtered[['DATE', 'TAVG', 'PRCP']], file_name)
    return 'AverageTemp_month'


def import_daily_file(csv_path, output_path='data_daily_filtered.csv'):
    columns_to_read = ['DATE', 'TAVG', 'TMAX', 'TMIN', 'PRCP']
    df = pd.read_csv(csv_path, usecols=columns_to_read)
    df['DATE'] = pd.to_datetime(df['DATE'], format='%Y-%m-%d')
    filename = 'AverageTemp_daily'

    end_date = datetime.now()
    start_date = end_date - relativedelta(years=30)
    save_plot_start = end_date - relativedelta(years=10)

    df_filtered = df[df['DATE'] >= start_date]

    df_statistically_filtered = df[(df['DATE'].dt.month == end_date.month) & (df['DATE'].dt.day == end_date.day)]

    df_save_plot = df[
        (df['DATE'] >= save_plot_start) & (df['DATE'].dt.month == end_date.month) & (df['DATE'].dt.day == end_date.day)]

    save_plot(df_save_plot[['DATE', 'TAVG', 'PRCP']], filename)

    df_statistically_filtered['TAVG'] = df_statistically_filtered.apply(process_temp, axis=1)
    df_statistically_filtered.dropna(subset=['TAVG'])
    df_statistically_filtered['TAVG'] = df_statistically_filtered['TAVG'] / 10
    print(df_statistically_filtered)

    statistical_modeling_forecast(df_statistically_filtered[['DATE', 'TAVG']], 'daily')

    df_filtered['TAVG'] = df_filtered.apply(process_temp, axis=1)

    df_filtered = df_filtered.dropna(subset=['TAVG'])

    df_filtered[['DATE', 'TAVG']].to_csv(output_path, index=False)

    return filename



def save_plot(df, file_name):
    from app import app

    if not file_name:
        raise ValueError("Filename is not defined")

    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax1.plot(df['DATE'], df['TAVG'], marker='o', label='Average Temp', color='tab:blue')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Average Temp (°C)', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    window_size = 3
    df.loc[:, 'TAVG_MA'] = df['TAVG'].rolling(window=window_size).mean()
    ax1.plot(df['DATE'], df['TAVG_MA'], marker='x', linestyle='--', label='Temp Moving Average', color='tab:cyan')

    ax2 = ax1.twinx()
    ax2.plot(df['DATE'], df['PRCP'], marker='o', label='Precipitation', color='tab:red')
    ax2.set_ylabel('Precipitation (mm)', color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    df.loc[:, 'PRCP_MA'] = df['PRCP'].rolling(window=window_size).mean()
    ax2.plot(df['DATE'], df['PRCP_MA'], marker='x', linestyle='--', label='Prec Moving Average', color='tab:green')

    plt.title("Precipitation and Avg Temp with moving averages")
    fig.tight_layout()
    plt.grid(True)
    plt.xticks(rotation=45)

    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    plot_path = os.path.join(app.root_path, 'static/plots/' + f'{file_name}.png')
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    plt.savefig(plot_path)
    plt.close()


def statistical_modeling_forecast(df, date_type):
    from app import app

    dif_date = 30
    end_date = datetime.now().year
    start_date = end_date - dif_date

    while dif_date > 0:
        df_filtered = df[df['DATE'].dt.year >= start_date]

        if (df_filtered['TAVG'] != 0).sum() > 10:
            break

        dif_date -= 1
        start_date = end_date - dif_date

    df_filtered['TAVG'] = df_filtered['TAVG'].ffill()
    df_filtered = df_filtered.dropna(subset=['TAVG'])

    if date_type == 'year':
        filename = 'year_forecast_chart'
    elif date_type == 'month':
        statistical_modeling_forecast_ets(df_filtered, 'month')
        return
    elif date_type == 'daily':
        statistical_modeling_forecast_ets(df_filtered, 'daily')
        return
    else:
        print("No forecast chart identifier")
        return None

    model = auto_arima(df_filtered['TAVG'], seasonal=True, stepwise=True, trace=True)

    n_periods = 5
    forecast, conf_int = model.predict(n_periods=n_periods, return_conf_int=True)

    future_dates = pd.date_range(start=df_filtered['DATE'].max() + pd.DateOffset(1), periods=n_periods, freq='YS')

    plt.figure(figsize=(10, 6))
    plt.plot(df_filtered['DATE'], df_filtered['TAVG'], label='Historical Data', color='tab:blue')
    plt.plot(future_dates, forecast, label='Forecast', color='tab:green')

    plt.fill_between(future_dates, conf_int[:, 0], conf_int[:, 1], alpha=0.2, color='tab:red')

    plt.xlabel('Date')
    plt.ylabel('Average Temp')
    plt.legend(loc='upper left')
    plt.title("Temperature Forecast")


    forecast_next_year = forecast.iloc[0]

    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plot_path = os.path.join(app.root_path, 'static/plots/' + f'{filename}.png')
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    plt.savefig(plot_path)
    plt.close()


def statistical_modeling_forecast_ets(df, date_type):
    from app import app
    dif_date = 30
    end_date = datetime.now().year
    start_date = end_date - dif_date

    while dif_date > 0:
        df_filtered = df[df['DATE'].dt.year >= start_date]

        if (df_filtered['TAVG'] != 0).sum() > 10:
            break

        dif_date -= 1
        start_date = end_date - dif_date

    df_filtered['TAVG'] = df_filtered['TAVG'].ffill()

    # Fit the ETS model
    model = ExponentialSmoothing(
        df_filtered['TAVG'],
        trend="add",
        seasonal=None,
        seasonal_periods=12
    ).fit()

    # Forecast the next 5 periods (years in this case)
    n_periods = 5
    forecast = model.forecast(n_periods)

    # Define future dates for plotting
    future_dates = pd.date_range(start=df_filtered['DATE'].max() + pd.DateOffset(1), periods=n_periods, freq='YS')

    # Plotting the results
    plt.figure(figsize=(10, 6))
    plt.plot(df_filtered['DATE'], df_filtered['TAVG'], label='Historical Data', color='tab:blue')
    plt.plot(future_dates, forecast, label='Forecast', color='tab:green')

    plt.xlabel('Date')
    plt.ylabel('Average Temp')
    plt.legend(loc='upper left')
    plt.title("Temperature Forecast with ETS")

    filename = ''

    if date_type == 'month':
        filename = 'month_forecast_chart'
    elif date_type == 'daily':
        filename = 'daily_forecast_chart'
    else:
        print("No forecast chart identifier")
        return None

    print("the file name is: ", filename)

    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plot_path = os.path.join(app.root_path, 'static/plots/' + f'{filename}.png')
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    plt.savefig(plot_path)
    plt.close()


def linear_model(df):
    x = df[['DATE']]
    y = df[['TAVG']]

    x['Year'] = x['DATE'].dt.year
    x['Month'] = x['DATE'].dt.month
    x['Day'] = x['DATE'].dt.day

    x = x[['Year', 'Month', 'Day']]

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(x_train, y_train)
    print("Model function called")
    return model


def predict_temp(df, predict_date):
    model = linear_model(df)
    # Extract year, month, and day from predict_date
    predict_date = pd.to_datetime(predict_date)
    predict_features = [[predict_date.year, predict_date.month, predict_date.day]]
    forecasted_temp = model.predict(predict_features)
    print("PREDICT TEMP CALLED")
    return forecasted_temp


def prediction_data(forecast_date, csv_path='data_daily_filtered.csv'):
    columns_to_read = ['DATE', 'TAVG']
    print("Forecast Date: ", forecast_date)

    try:
        target_month = forecast_date.month
        target_day = forecast_date.day

        # Read the CSV file
        df = pd.read_csv(csv_path, usecols=columns_to_read)
        df['DATE'] = pd.to_datetime(df['DATE'], format='%Y-%m-%d')

        # Filter the DataFrame
        df_filtered = df[(df['DATE'].dt.month == target_month) & (df['DATE'].dt.day == target_day)]
        print(df_filtered)

        if df_filtered.empty:
            print("Historical data for predicting weather is empty")
            return None

        # Predict temperature
        predicted_temp = predict_temp(df_filtered, forecast_date)
        print("THE PREDICTED VALUE:", predicted_temp / 10)

        return predicted_temp / 10

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
