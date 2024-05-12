# pip install streamlit fbprophet yfinance plotly
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import pandas as pd
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
import pygwalker as pyg
import requests
from pygwalker.api.streamlit import StreamlitRenderer
import time


import base64
def download_link(object_to_download, download_filename, download_link_text):
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    b64 = base64.b64encode(object_to_download.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'




START = "2015-01-01"
TODAY = datetime.today().strftime('%Y-%m-%d')


# Main page layout adjustments
st.set_page_config(page_title='Cryptocurrencies Price Predictor', layout='wide')
st.title('Cryptocurrencies Price Predictor')

#Navigation bar Defination
def navigation_bar():
    st.markdown("""
    <style>
    .nav-container {
        background-color: #f1f3f6;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        text-align: center;
        margin-bottom: 20px;
    }
    .nav-link {
        color: black;
        text-decoration: none;
        padding: 10px 20px;
        display: inline-block;
        border-radius: 5px;
        transition: background-color 0.3s, box-shadow 0.3s;
    }
    .nav-link:hover {
        background-color: #e8e8e8;
        box-shadow: 0 2px 4px 0 rgba(0,0,0,0.2);
    }
    </style>
    <div class="nav-container">
        <a href="#FORECASTING" class="nav-link">FORECASTING</a>
        <a href="#USER DATA VISUALIZATION" class="nav-link">USER DATA VISUALIZATION</a>
        
    </div>
    """, unsafe_allow_html=True)

# Call the function to display the navigation bar
navigation_bar()



st.markdown("""
Our innovative prediction tool empowers users to chart the potential trajectory of top cryptocurrencies, providing granular insights on a daily, weekly, monthly, and yearly basis, extending up to a visionary 10-year outlook
""")
st.markdown("""Select a cryptocurrency and the frequency of prediction from the dropdown menus below.""")

# List of cryptocurrencies
Currency = ('BTC-USD', 'ETH-USD', 'USDT-USD', 'BNB-USD','SOL-USD','USDC-USD','XRP-USD','ADA-USD','AVAX-USD','BCH-USD')


# Create a container with the custom scrollbar
with st.container():
    st.markdown('<div class="container-to-scroll">', unsafe_allow_html=True)
    
    # ... [content that may overflow and require scrolling] ...
    
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar for parameter selection
with st.sidebar:

    selected_currency = st.selectbox('Select dataset for prediction', Currency)
    # Add a selectbox for the frequency of prediction
    frequency = st.selectbox('Select frequency for prediction', ('Daily', 'Weekly', 'Monthly', 'Yearly'))

    #Map frequency to appropriate Prophet frequency format and slider range
    freq_map = {'Daily': ('D', 3650), 'Weekly': ('W', 520), 'Monthly': ('M', 120), 'Yearly': ('Y', 10)}
    freq, max_periods = freq_map[frequency]

    # Real-time Data Updates
    if st.button('Refresh Data', key='refresh_data_sidebar'):
        # Initialize progress bar
        progress_bar = st.progress(0)
        for i in range(100):
            # Simulate a long process
            time.sleep(0.1)
            # Update progress bar
            progress_bar.progress(i + 1)
        st.experimental_rerun()


# Adjust the slider for the number of periods to forecast based on the selected frequency
st.header('Select Parameters')
period = st.slider('Number of periods for prediction:', 1, max_periods)
    

@st.cache_data
def load_data(ticker):
    data = yf.download(ticker, START, TODAY)
    data.reset_index(inplace=True)
    return data

	
data_load_state = st.text('Loading data...')
data = load_data(selected_currency)
data_load_state.text('Loading data... done!')

st.markdown("---")
st.subheader('Raw data')
st.write(data.tail())
st.markdown("---")


# Plot raw data
def plot_raw_data():
    fig = go.Figure(data=[go.Candlestick(x=data['Date'],
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'])])
    fig.update_layout( autosize=True, height=500,width=1350, margin=dict(l=20, r=20, t=20, b=20),  # Adjust as needed
                       title='Raw Data Candlestick Chart', xaxis_rangeslider_visible=True)
    st.plotly_chart(fig,use_container_width=True)
plot_raw_data()



# Predict forecast with Prophet.
df_train = data[['Date','Close']]
df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

m = Prophet()
m.fit(df_train)
future = m.make_future_dataframe(periods=period , freq=freq)
forecast = m.predict(future)

st.divider()

# Use markdown to create an anchor in your app for the FORECASTING  section
st.markdown('<div id="FORECASTING"></div>', unsafe_allow_html=True)



# Add content for the FORECSTING section
st.header('FORECASTING')
st.markdown(" The Forecasting section of the application leverages to predict future cryptocurrency prices based on historical data. Users can select from a range of cryptocurrencies and set the prediction frequency to daily, weekly, monthly, or yearly. The forecast includes a plot of predicted values along with upper and lower limits, providing a visual representation of the expected price range.")
     


## forecasting
# Show and plot forecast
st.markdown("---")
st.subheader('Forecasted Data')
st.write(forecast.tail())


st.markdown("---")
st.subheader(f'Forecasted plot for {period} {freq}')
fig1 = plot_plotly(m, forecast)
st.plotly_chart(fig1)


# Create a line chart for forecasted yhat, yhat_lower, yhat_upper, ds, yhat
st.markdown("---")
st.subheader(f'Forecasted plot for {period} {freq} from Today')
fig2= go.Figure()

#Filter the forecast
if period == 1 and freq in ['D','W','M','Y']:
    forecast_filt = forecast.tail(2)
else :
    forecast_filt = forecast[forecast['ds'] >= pd.Timestamp(TODAY)]


# Add traces
fig2.add_trace(go.Scatter(x=forecast_filt['ds'], y=forecast_filt['yhat'], mode='lines', name='PREDICTED',
                         hovertemplate = 'Date: %{x}<br>Predicted: %{y}'))
fig2.add_trace(go.Scatter(x=forecast_filt['ds'], y=forecast_filt['yhat_upper'], mode='lines', name='UPPER_LIMIT',
                         hovertemplate = 'Date: %{x}<br>Upper Limit: %{y}', line=dict(width=2)))
fig2.add_trace(go.Scatter(x=forecast_filt['ds'], y=forecast_filt['yhat_lower'], mode='lines', name='LOWER_LIMIT',
                         hovertemplate = 'Date: %{x}<br>Lower Limit: %{y}', line=dict(width=2)))

# Add shaded region for uncertainty
fig2.add_trace(go.Scatter(
    x=forecast_filt['ds'].tolist() + forecast_filt['ds'].tolist()[::-1],  # x, then x reversed
    y=forecast_filt['yhat_upper'].tolist() + forecast_filt['yhat_lower'].tolist()[::-1],  # upper, then lower reversed
    fill='toself',
    fillcolor='rgba(0,176,246,0.2)',
    line=dict(color='rgba(255,255,255,0)'),
    hoverinfo="skip",
    showlegend=False))

# Layout
fig2.update_layout( autosize=True,
                     width=1350, margin=dict(l=20, r=20, t=20, b=20),  # Adjust as needed
                   title='Forecasted line chart',
                   xaxis_title='Date',
                   yaxis_title='Value')

st.plotly_chart(fig2,use_container_width=True)


#Dipslay forecast components
st.markdown("---")
st.subheader("FORECASTED COMPONENTS")
fig3 = m.plot_components(forecast)
st.write(fig3)



# Optimize the forecast dataframe by selecting only necessary columns
Optimized_Forecast = forecast_filt[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
Optimized_Forecast = Optimized_Forecast.rename(columns={"yhat": "predicted","yhat_upper":"Upper","yhat_lower":"Lower"})



# Sidebar for download links
with st.sidebar:
    st.markdown("""
    ## Download Section 

    Click on the link below to download the data.
    """)
    
    # Create a radio button to select the file to download
    download_choice = st.radio('Choose a file to download:', ('Complete Forecast Data', 'Future Forecast Data','Optimized Forecast Data'))
    
    # Generate the appropriate download link based on the user's choice
    if download_choice == 'Complete Forecast Data':
        tmp_download_link = download_link(forecast.to_csv(), 'forecast.csv', 'Download Complete Forecast Data')
    elif download_choice=='Future Forecast Data' :
        tmp_download_link = download_link(forecast_filt.to_csv(), 'future_forecast.csv', 'Download Future Forecast Data')
    else :
        tmp_download_link = download_link(Optimized_Forecast.to_csv(),'Optimized_Forecast.csv','Optimized_Forecast')
   
    # Display the download link
    st.markdown(tmp_download_link, unsafe_allow_html=True)


# Use markdown to create an anchor in your app for the USER DATA VISUALIZATION section
st.markdown('<div id="USER DATA VISUALIZATION"></div>', unsafe_allow_html=True)


# PyGWalker Section
st.divider()
st.header("USER DATA VISUALIZATION")
st.markdown("---")
st.markdown("This section offers users the ability to upload their own datasets in CSV or Excel format. Once uploaded, it will be allowing users to delve into their data. This feature is particularly useful for users who wish to analyze their personal or business-related data within the same application.")


# File uploader allows user to add their own dataset
uploaded_file = st.file_uploader("Upload your CSV or Excel file. (200MB max)", type=["csv", "xlsx"])

# If a file is uploaded, read it into a dataframe and display the PyGWalker explorer
if uploaded_file is not None:
    # Read the uploaded file into a dataframe
    if uploaded_file.name.endswith('.csv'):
        df_uploaded = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df_uploaded = pd.read_excel(uploaded_file)

    # Display the PyGWalker explorer
    st.subheader("Explore your dataset")
    pyg_app = StreamlitRenderer(df_uploaded)
    pyg_app.explorer()  




