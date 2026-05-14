# Description: Short example for Analyzing the 2013 Colorado Flood Using Time Series Analysis.



from data_io import read_csv
from datetime import datetime, timedelta
from matplotlib.dates import DateFormatter
from pandas.plotting import register_matplotlib_converters
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.statespace.sarimax import SARIMAX
import earthpy as et
import logging
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


# Earth Data Science Tutorial Blog
# Initial Author: Univ of Colorado Earth Lab; updated by Kyle Jones
# Last Updated: April 2024
# Description: Time Series Analysis of 2013 Colorado Flood


# Handle date time conversions
register_matplotlib_converters()

# Set plot style
sns.set(font_scale=1.5, style="whitegrid")

# Download and set up data
data = et.data.get_data('colorado-flood')
os.chdir(os.path.join(et.io.HOME, 'earth-analytics', 'data'))

# Define paths
stream_discharge_path = os.path.join("colorado-flood",
                                   "discharge",
                                   "06730200-discharge-daily-1986-2013.csv")
precip_path = os.path.join("colorado-flood",
                          "precipitation",
                          "805325-precip-daily-2003-2013.csv")

# Data processing functions
def process_discharge_data(filepath):
    """Read and process discharge data"""
    df = read_csv(filepath)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    return df

def process_precip_data(filepath):
    """Read and process precipitation data"""
    df = read_csv(filepath)
    df['DATE'] = pd.to_datetime(df['DATE'])
    df.set_index('DATE', inplace=True)
    return df

# Plotting functions
def plot_discharge(df, title="Stream Discharge Over Time"):
    """Plot discharge time series"""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df.index, df['disValue'])
    ax.set_title(title)
    ax.set_xlabel('Date')
    ax.set_ylabel('Discharge Value')
    ax.set_ylim(bottom=0)
    plt.xticks(rotation=45)
    return fig, ax

def plot_discharge_and_precip(discharge_df, precip_df, start_date, end_date):
    """Plot combined discharge and precipitation"""
    discharge_subset = subset_time_period(discharge_df, start_date, end_date)
    precip_subset = subset_time_period(precip_df, start_date, end_date)
    
    fig, ax1 = plt.subplots(figsize=(15, 7))
    
    # Discharge on primary y-axis
    color = 'tab:blue'
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Discharge Value', color=color)
    ax1.plot(discharge_subset.index, discharge_subset['disValue'], 
             color=color, label='Discharge')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_ylim(bottom=0)
    
    # Precipitation on secondary y-axis
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Precipitation (mm)', color=color)
    ax2.bar(precip_subset.index, precip_subset['HPCP'], 
            color=color, alpha=0.3, label='Precipitation')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_ylim(bottom=0)
    
    # Title and layout
    plt.title("Stream Discharge and Precipitation During 2013 Colorado Flood")
    plt.xticks(rotation=45)
    
    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    return fig, (ax1, ax2)

# Analysis functions
def subset_time_period(df, start_date, end_date):
    """Subset data for specific time period"""
    return df.loc[start_date:end_date]

def resample_weekly(df):
    """Resample data to weekly values"""
    return df.resample('W').max()


def save_plot(fig, filename, dpi=300):
    """Save plot to file"""
    if not os.path.exists('plots'):
        os.makedirs('plots')
    fig.savefig(os.path.join('plots', filename), 
                bbox_inches='tight', 
                dpi=dpi)

def analyze_flood_metrics(discharge_df, precip_df, flood_start, flood_end):
    """Calculate key flood metrics"""
    flood_discharge = subset_time_period(discharge_df, flood_start, flood_end)
    flood_precip = subset_time_period(precip_df, flood_start, flood_end)
    
    metrics = {
        'total_precip': flood_precip['HPCP'].sum(),
        'max_discharge': flood_discharge['disValue'].max(),
        'mean_discharge': flood_discharge['disValue'].mean(),
        'max_precip_day': flood_precip['HPCP'].idxmax(),
        'max_discharge_day': flood_discharge['disValue'].idxmax()
    }
    
    return metrics

def fit_sarima_model(data, train_size=0.8, 
                    order=(1,1,1), 
                    seasonal_order=(1,1,1,12)):
    """Fit SARIMA model and make predictions"""
    train_size = int(len(data) * train_size)
    train = data[:train_size]
    test = data[train_size:]
    
    model = SARIMAX(train['disValue'],
                    order=order,
                    seasonal_order=seasonal_order)
    results = model.fit()
    
    predictions = results.predict(start=len(train), 
                                end=len(train)+len(test)-1)
    
    return train, test, predictions, results

def plot_sarima_results(train, test, predictions, 
                       confidence_intervals=None,
                       title="SARIMA Forecast"):
    """Plot SARIMA results with confidence intervals"""
    fig, ax = plt.subplots(figsize=(15, 7))
    
    ax.plot(train.index, train['disValue'], 
            label='Training Data', color='blue')
    ax.plot(test.index, test['disValue'], 
            label='Actual Test Data', color='green')
    ax.plot(test.index, predictions, 
            label='SARIMA Forecast', color='red')
    
    if confidence_intervals is not None:
        lower_ci = np.maximum(confidence_intervals['lower'], 0)
        ax.fill_between(test.index,
                       lower_ci,
                       confidence_intervals['upper'],
                       color='red', alpha=0.1,
                       label='95% Confidence Interval')
    
    ax.set_title(title)
    ax.set_xlabel('Date')
    ax.set_ylabel('Discharge Value')
    ax.set_ylim(bottom=0)
    plt.xticks(rotation=45)
    plt.legend()
    
    return fig, ax

if __name__ == "__main__":
    # Load data
    logger.info("Loading and processing data...")
    discharge_df = process_discharge_data(stream_discharge_path)
    precip_df = process_precip_data(precip_path)
    
    # Analyze flood period
    flood_metrics = analyze_flood_metrics(discharge_df, precip_df,
                                        '2013-09-01', '2013-09-30')
    logger.info("\nFlood Metrics:")
    for key, value in flood_metrics.items():
        logger.info(f"{key}: {value}")
    
    # Create all plots
    logger.info("\nGenerating plots...")
    
    # Basic discharge plot
    fig1, ax1 = plot_discharge(discharge_df)
    save_plot(fig1, 'full_timeseries.png')
    
    # Flood period combined plot
    fig2, axes2 = plot_discharge_and_precip(
        discharge_df, precip_df,
        '2013-09-01', '2013-09-30'
    )
    save_plot(fig2, 'flood_period_combined.png')
    
    # SARIMA modeling
    logger.info("\nFitting SARIMA model...")
    train, test, predictions, model_results = fit_sarima_model(
        discharge_df,
        train_size=0.8,
        order=(2,1,2),
        seasonal_order=(1,1,1,12)
    )
    
    # Get forecast confidence intervals
    forecast = model_results.get_forecast(len(test))
    conf_int = forecast.conf_int()
    confidence_intervals = {
        'lower': conf_int.iloc[:, 0],
        'upper': conf_int.iloc[:, 1]
    }
    
    # Calculate and print RMSE
    rmse = np.sqrt(mean_squared_error(test['disValue'], predictions))
    logger.info(f'RMSE: {rmse:.2f}')
    
    # Plot SARIMA results
    fig3, ax3 = plot_sarima_results(
        train, test, predictions,
        confidence_intervals,
        "SARIMA Forecast vs Actual Discharge"
    )
    save_plot(fig3, 'sarima_forecast.png')
    
    plt.show()
