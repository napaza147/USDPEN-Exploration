''' 
This program contains functions that construct several technical indicators.
'''

def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    # Calculating EMAs
    short_ema = data.ewm(span=short_window, adjust=False).mean()
    long_ema = data.ewm(span=long_window, adjust=False).mean()

    # Calculating MACD
    macd = short_ema - long_ema

    # Calculating Signal line
    macd_signal = macd.ewm(span=signal_window, adjust=False).mean()

    # Calculating Histogram
    macd_histogram = macd - macd_signal

    return macd, macd_signal, macd_histogram

def calculate_sma(data, windows):
    for window in windows:
        sma_column_name = f'SMA{window}'
        data[sma_column_name] = data['Open'].rolling(window=window).mean()

    return data


def calculate_rsi(data, windows):
    for window in windows:
        delta = data['Open'].diff(1)  # Calculate price changes
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()  # Calculate gains
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()  # Calculate losses

        rs = gain / loss  # Calculate Relative Strength (RS)
        rsi = 100 - (100 / (1 + rs))  # Calculate RSI

        # Add the RSI to the DataFrame with a column name
        data[f'RSI{window}'] = rsi

    return data


def calculate_adx(data, windows):

    # Calculate True Range (TR)
    data['High-Low'] = data['High'] - data['Low']
    data['High-PrevClose'] = abs(data['High'] - data['Close'].shift(1))
    data['Low-PrevClose'] = abs(data['Low'] - data['Close'].shift(1))

    data['TR'] = data[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)

    for window in windows:
        # Calculate the Directional Movement (DM)
        data['DM+'] = data['High'].diff()
        data['DM-'] = -data['Low'].diff()

        data['DM+'] = data['DM+'].where(data['DM+'] > data['DM-'], 0)
        data['DM-'] = data['DM-'].where(data['DM-'] > data['DM+'], 0)

        # Calculate the rolling sums
        data['TR_sum'] = data['TR'].rolling(window=window).sum()
        data['DM+_sum'] = data['DM+'].rolling(window=window).sum()
        data['DM-_sum'] = data['DM-'].rolling(window=window).sum()

        # Calculate the Directional Indicators (DI)
        data[f'DI+{window}'] = (data['DM+_sum'] / data['TR_sum']) * 100
        data[f'DI-{window}'] = (data['DM-_sum'] / data['TR_sum']) * 100

        # Calculate the ADX
        data[f'ADX{window}'] = (abs(data[f'DI+{window}'] - data[f'DI-{window}']) / (data[f'DI+{window}'] + data[f'DI-{window}'])) * 100
        data[f'ADX{window}'] = data[f'ADX{window}'].rolling(window=window).mean()  # Smooth the ADX

    # Clean up the temporary columns
    data.drop(columns=['High-Low', 'High-PrevClose', 'Low-PrevClose', 'TR', 'DM+', 'DM-', 'TR_sum', 'DM+_sum', 'DM-_sum'], inplace=True)

    return data


def calculate_wr(data, windows):

    for window in windows:
        highest_high = data['High'].rolling(window=window).max()  # Highest high over the window
        lowest_low = data['Low'].rolling(window=window).min()     # Lowest low over the window

        wr = ((highest_high - data['Close']) / (highest_high - lowest_low)) * -100  # Calculate WR

        # Add the WR to the DataFrame with a column name
        data[f'WR{window}'] = wr

    return data

def calculate_bollinger_bands(data, window, num_std_dev):

    # Calculate the Middle Band (SMA)
    data['Bollinger Middle Band'] = data['Close'].rolling(window=window).mean()

    # Calculate the standard deviation
    rolling_std = data['Close'].rolling(window=window).std()

    # Calculate Upper and Lower Bands
    data['Bollinger Upper Band'] = data['Bollinger Middle Band'] + (rolling_std * num_std_dev)
    data['Bollinger Lower Band'] = data['Bollinger Middle Band'] - (rolling_std * num_std_dev)

    return data
