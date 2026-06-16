#!/usr/bin/env python
# coding: utf-8

# In[232]:


import os

os.listdir()


# In[233]:


import os

os.listdir()


# In[234]:


import pandas as pd

df = pd.read_csv("Options_data_2023.csv")


# In[235]:


df.head()


# In[236]:


df.columns


# In[237]:


df.shape


# In[238]:


df.head(10)


# In[239]:


df['Time'].unique()[:20]


# In[240]:


df['Time'].min(), df['Time'].max()


# In[241]:


Unnamed: 0


# In[242]:


df = df.drop('Unnamed: 0', axis=1)


# In[243]:


df['Date'].nunique()


# In[244]:


df['Date'].unique()[:5]


# In[245]:


sample_day = df[df['Date'] == '2023-01-02']

sample_day.head()


# In[246]:


entry_data = sample_day[sample_day['Time'] == '09:20:59']

entry_data.head()


# In[247]:


ce_data = entry_data[entry_data['Call/Put'] == 'CE']

pe_data = entry_data[entry_data['Call/Put'] == 'PE']


# In[248]:


ce_data.head()


# In[249]:


pe_data.head()


# In[250]:


ce_data['diff'] = abs(ce_data['Close'] - 50)

ce_trade = ce_data.loc[ce_data['diff'].idxmin()]

ce_trade


# In[251]:


pe_data['diff'] = abs(pe_data['Close'] - 50)

pe_trade = pe_data.loc[pe_data['diff'].idxmin()]

pe_trade


# In[252]:


ce_entry = ce_trade['Close']
pe_entry = pe_trade['Close']

ce_sl = ce_entry * 1.5
pe_sl = pe_entry * 1.5

print("CE Entry:", ce_entry)
print("CE SL:", ce_sl)

print("PE Entry:", pe_entry)
print("PE SL:", pe_sl)


# In[253]:


ce_ticker = ce_trade['Ticker']

ce_day_data = sample_day[
    sample_day['Ticker'] == ce_ticker
]

ce_day_data.head()


# In[254]:


pe_ticker = pe_trade['Ticker']

pe_day_data = sample_day[
    sample_day['Ticker'] == pe_ticker
]

pe_day_data.head()


# In[255]:


ce_after_entry = ce_day_data[
    ce_day_data['Time'] > '09:20:59'
]

ce_after_entry.head()


# In[256]:


ce_sl_hit = ce_after_entry[
    ce_after_entry['High'] >= ce_sl
]

ce_sl_hit.head()


# In[257]:


pe_after_entry = pe_day_data[
    pe_day_data['Time'] > '09:20:59'
]

pe_sl_hit = pe_after_entry[
    pe_after_entry['High'] >= pe_sl
]

pe_sl_hit.head()


# In[258]:


pe_exit_row = pe_day_data[
    pe_day_data['Time'] == '15:20:59'
]

pe_exit_row


# In[259]:


pe_exit_price = pe_exit_row.iloc[0]['Close']

print(pe_exit_price)


# In[260]:


ce_exit_price = ce_sl


# In[261]:


ce_exit_time = ce_sl_hit.iloc[0]['Time']


# In[262]:


print(ce_exit_price)
print(ce_exit_time)


# In[263]:


ce_pnl = (ce_entry - ce_exit_price) * 15

print(ce_pnl)


# In[264]:


pe_pnl = (pe_entry - pe_exit_price) * 15

print(pe_pnl)


# In[265]:


total_pnl = ce_pnl + pe_pnl

print(total_pnl)


# In[266]:


trades = []


# In[267]:


dates = sorted(df['Date'].unique())

print("Total Days:", len(dates))


# In[268]:


df.shape


# In[269]:


df['Date'].nunique()


# In[270]:


df.memory_usage(deep=True).sum()/1024/1024


# In[271]:


df.info()


# In[272]:


df['Date'] = pd.to_datetime(df['Date'])


# In[273]:


entry_data = df[df['Time'] == '09:20:59'].copy()


# In[274]:


entry_data.shape


# In[275]:


ce_entry = entry_data[
    entry_data['Call/Put'] == 'CE'
].copy()

pe_entry = entry_data[
    entry_data['Call/Put'] == 'PE'
].copy()


# In[276]:


ce_entry['diff'] = abs(ce_entry['Close'] - 50)


# In[277]:


ce_trades = ce_entry.loc[
    ce_entry.groupby('Date')['diff'].idxmin()
]


# In[278]:


pe_entry['diff'] = abs(pe_entry['Close'] - 50)


# In[279]:


pe_trades = pe_entry.loc[
    pe_entry.groupby('Date')['diff'].idxmin()
]


# In[280]:


ce_trades.head()


# In[281]:


pe_trades.head()


# In[282]:


entry_data.shape


# In[283]:


ce_trades.shape


# In[284]:


pe_trades.shape


# In[285]:


ce_trades.head()


# In[286]:


ce_trades.to_csv("ce_trades.csv", index=False)
pe_trades.to_csv("pe_trades.csv", index=False)


# In[287]:


def calculate_trade(option_row, option_type):

    day = option_row['Date']
    ticker = option_row['Ticker']

    entry_price = option_row['Close']

    stoploss = entry_price * 1.5

    option_data = df[
        (df['Date'] == day) &
        (df['Ticker'] == ticker)
    ]

    after_entry = option_data[
        option_data['Time'] > '09:20:59'
    ]

    sl_hit = after_entry[
        after_entry['High'] >= stoploss
    ]

    if len(sl_hit) > 0:

        exit_time = sl_hit.iloc[0]['Time']
        exit_price = stoploss

    else:

        exit_row = option_data[
            option_data['Time'] == '15:20:59'
        ]

        if len(exit_row) == 0:
            return None

        exit_time = '15:20:59'
        exit_price = exit_row.iloc[0]['Close']

    pnl = (entry_price - exit_price) * 15

    return {
        'Date': day,
        'Ticker': ticker,
        'Type': option_type,
        'EntryPrice': entry_price,
        'ExitPrice': exit_price,
        'ExitTime': exit_time,
        'PnL': pnl
    }


# In[288]:


calculate_trade(
    ce_trades.iloc[0],
    'CE'
)


# In[289]:


calculate_trade(
    pe_trades.iloc[0],
    'PE'
)


# In[290]:


df = df.sort_values(['Date', 'Ticker', 'Time'])


# In[291]:


print("Sorting Done")


# In[314]:


from tqdm import tqdm

ticker_lookup = {}

for key, group in tqdm(df.groupby(['Date', 'Ticker'])):
    ticker_lookup[key] = group

print("Lookup Created")


# In[315]:


len(ticker_lookup)


# In[316]:


LOT_SIZE = 15

def process_trade(row, option_type):

    day = row['Date']
    ticker = row['Ticker']

    option_data = ticker_lookup[(day, ticker)]

    entry_price = row['Close']
    stoploss = entry_price * 1.5

    after_entry = option_data[
        option_data['Time'] > '09:20:59'
    ]

    sl_hit = after_entry[
        after_entry['High'] >= stoploss
    ]

    if len(sl_hit) > 0:

        exit_time = sl_hit.iloc[0]['Time']
        exit_price = stoploss

    else:

        exit_row = option_data[
            option_data['Time'] == '15:20:59'
        ]

        if len(exit_row) == 0:
            return None

        exit_time = '15:20:59'
        exit_price = exit_row.iloc[0]['Close']

    pnl = (entry_price - exit_price) * LOT_SIZE

    return {
        'Date': day,
        'Ticker': ticker,
        'OptionType': option_type,
        'EntryTime': '09:20:59',
        'ExitTime': exit_time,
        'EntryPrice': round(entry_price, 2),
        'ExitPrice': round(exit_price, 2),
        'PnL': round(pnl, 2)
    }


# In[317]:


process_trade(
    ce_trades.iloc[0],
    'CE'
)


# In[318]:


all_trades = []

for _, row in tqdm(
    ce_trades.iterrows(),
    total=len(ce_trades)
):
    trade = process_trade(row, 'CE')

    if trade:
        all_trades.append(trade)

for _, row in tqdm(
    pe_trades.iterrows(),
    total=len(pe_trades)
):
    trade = process_trade(row, 'PE')

    if trade:
        all_trades.append(trade)

trade_df = pd.DataFrame(all_trades)

print(trade_df.shape)


# In[297]:


trade_df.head()


# In[298]:


trade_df = trade_df.sort_values(
    ['Date', 'OptionType']
).reset_index(drop=True)

trade_df.head()


# In[299]:


trade_df['CumulativePnL'] = (
    trade_df['PnL'].cumsum()
)

trade_df.head()


# In[300]:


INITIAL_CAPITAL = 100000

trade_df['AvailableCapital'] = (
    INITIAL_CAPITAL +
    trade_df['CumulativePnL']
)

trade_df.head()


# In[301]:


LOT_SIZE = 15

trade_df['Quantity'] = LOT_SIZE

trade_df['EntryValue'] = (
    trade_df['EntryPrice']
    * LOT_SIZE
)

trade_df['ExitValue'] = (
    trade_df['ExitPrice']
    * LOT_SIZE
)


# In[302]:


trade_df['PnL_%'] = (
    trade_df['PnL']
    /
    trade_df['EntryValue']
) * 100


# In[303]:


wins = (trade_df['PnL'] > 0).sum()

losses = (trade_df['PnL'] < 0).sum()

total = len(trade_df)

win_rate = wins / total * 100

loss_rate = losses / total * 100

print("Wins :", wins)
print("Losses :", losses)
print("Win Rate :", round(win_rate,2))
print("Loss Rate :", round(loss_rate,2))


# In[304]:


trade_df['Month'] = (
    pd.to_datetime(
        trade_df['Date']
    ).dt.to_period('M')
)

monthly_pnl = (
    trade_df
    .groupby('Month')['PnL']
    .sum()
)

monthly_pnl


# In[305]:


daily_pnl = (
    trade_df
    .groupby('Date')['PnL']
    .sum()
)

nav = 100 + daily_pnl.cumsum()

nav.head()


# In[306]:


start_nav = nav.iloc[0]

end_nav = nav.iloc[-1]

years = 1

cagr = (
    ((end_nav / start_nav) ** (1/years))
    - 1
) * 100

print("CAGR:", round(cagr,2), "%")


# In[307]:


running_max = nav.cummax()

drawdown = (
    nav - running_max
) / running_max

max_drawdown = (
    drawdown.min() * 100
)

print(
    "Max Drawdown:",
    round(max_drawdown,2),
    "%"
)


# In[308]:


import matplotlib.pyplot as plt

plt.figure(figsize=(12,6))

nav.plot()

plt.title(
    "Equity Curve"
)

plt.grid(True)

plt.show()


# In[319]:


df['Ticker'].sample(20).tolist()


# In[320]:


trade_df.groupby('Date').size().value_counts()


# In[322]:


trade_df.columns.tolist()


# In[323]:


ce_wins = len(
    trade_df[
        (trade_df['OptionType'] == 'CE')
        &
        (trade_df['PnL'] > 0)
    ]
)

ce_losses = len(
    trade_df[
        (trade_df['OptionType'] == 'CE')
        &
        (trade_df['PnL'] < 0)
    ]
)

pe_wins = len(
    trade_df[
        (trade_df['OptionType'] == 'PE')
        &
        (trade_df['PnL'] > 0)
    ]
)

pe_losses = len(
    trade_df[
        (trade_df['OptionType'] == 'PE')
        &
        (trade_df['PnL'] < 0)
    ]
)

print(
    ce_wins,
    ce_losses,
    pe_wins,
    pe_losses
)


# In[325]:


summary = pd.DataFrame({

'Metric': [

'Total Trades',

'Winning Trades',
'Losing Trades',

'CE Wins',
'CE Losses',

'PE Wins',
'PE Losses',

'Win Rate %',
'Loss Rate %',

'Max Drawdown %',

'CAGR %',

'Total PnL'

],

'Value': [

len(trade_df),

wins,
losses,

ce_wins,
ce_losses,

pe_wins,
pe_losses,

round(win_rate,2),
round(loss_rate,2),

round(max_drawdown,2),

round(cagr,2),

round(
trade_df['PnL'].sum(),
2
)

]

})

summary


# In[327]:


trade_df.columns


# In[328]:


trade_df['StrikePrice'] = (
    trade_df['Ticker']
    .str.extract(r'(\d+)')
    .astype(int)
)


# In[329]:


trade_df[['Ticker','StrikePrice']].head()


# In[330]:


trade_df.rename(
    columns={'PnL':'GrossPnL'},
    inplace=True
)


# In[331]:


trade_df['CumulativePnL'] = (
    trade_df['GrossPnL'].cumsum()
)


# In[333]:


trade_df.head()


# In[334]:


trade_df.isnull().sum()


# In[336]:


trade_df.columns


# In[340]:


trade_df.columns.tolist()


# In[341]:


daily_results = (
    trade_df
    .groupby('Date', as_index=False)['GrossPnL']
    .sum()
)

daily_results.rename(
    columns={'GrossPnL': 'DailyPnL'},
    inplace=True
)

daily_results.head()


# In[342]:


daily_results['CumulativePnL'] = (
    daily_results['DailyPnL']
    .cumsum()
)

daily_results.head()


# In[343]:


INITIAL_CAPITAL = 100000

nav = (
    INITIAL_CAPITAL
    + daily_results['CumulativePnL']
)

print(nav.head())


# In[344]:


running_max = nav.cummax()

drawdown = (
    nav - running_max
) / running_max

max_drawdown = (
    drawdown.min()
) * 100

start_nav = nav.iloc[0]

end_nav = nav.iloc[-1]

cagr = (
    ((end_nav / start_nav) ** (1/1))
    - 1
) * 100

print("Max Drawdown =", round(max_drawdown,2))
print("CAGR =", round(cagr,2))


# In[345]:


summary


# In[346]:


guide = pd.DataFrame({
'Description':[
'Strategy: 09:20 AM Short Strangle',
'Entry Time: 09:20:59',
'Exit Time: Stoploss or 15:20:59',
'Strike Selection: Premium nearest Rs.50',
'Stoploss: 50% of Entry Premium',
'Lot Size: 15',
'One Lot Per Day',
'No Compounding',
'Assumption: Expiry information not present in ticker data.'
]
})


# In[348]:


with pd.ExcelWriter(
    "Qode_Backtest_Result.xlsx"
) as writer:

    guide.to_excel(
        writer,
        sheet_name='Guide',
        index=False
    )

    trade_df.to_excel(
        writer,
        sheet_name='Trades',
        index=False
    )

    summary.to_excel(
        writer,
        sheet_name='Statistics',
        index=False
    )

    monthly_pnl.to_excel(
        writer,
        sheet_name='MonthlyPnL',
        index=False
    )

print("Final Excel Ready")


# In[349]:


import matplotlib.pyplot as plt

plt.figure(figsize=(12,6))

nav.plot()

plt.title("09:20 Short Strangle Equity Curve")

plt.grid(True)

plt.savefig(
    "Equity_Curve.png",
    bbox_inches="tight"
)

plt.show()


# In[350]:


trade_df.isnull().sum()


# In[351]:


len(trade_df)


# In[352]:


import os

print(os.getcwd())


# In[353]:


import os

os.listdir()


# In[354]:


import os

print(os.path.exists("Qode_Backtest_Result.xlsx"))


# In[355]:


df['Ticker'].str.contains('BANKNIFTY').value_counts()


# In[356]:


df['Ticker'].drop_duplicates().sample(20)


# In[357]:


df[
    ~df['Ticker'].str.contains('CE|PE', regex=True)
]['Ticker'].unique()[:20]


# In[358]:


trade_df.columns.tolist()


# In[359]:


LOT_SIZE = 15

trade_df['Quantity'] = LOT_SIZE

trade_df['EntryValue'] = (
    trade_df['EntryPrice']
    * trade_df['Quantity']
)

trade_df['ExitValue'] = (
    trade_df['ExitPrice']
    * trade_df['Quantity']
)

INITIAL_CAPITAL = 100000

trade_df['AvailableCapital'] = (
    INITIAL_CAPITAL
    + trade_df['CumulativePnL']
)


# In[360]:


trade_df.columns.tolist()


# In[361]:


trade_df = trade_df[
[
'Date',
'Ticker',
'StrikePrice',
'OptionType',
'EntryTime',
'ExitTime',
'EntryPrice',
'ExitPrice',
'Quantity',
'EntryValue',
'ExitValue',
'GrossPnL',
'CumulativePnL',
'AvailableCapital'
]
]

trade_df.head()


# In[363]:


summary


# In[364]:


print("Max Drawdown =", round(max_drawdown,2))
print("CAGR =", round(cagr,2))


# In[365]:


summary = pd.DataFrame({
    'Metric': [
        'Total Trades',
        'Winning Trades',
        'Losing Trades',
        'CE Wins',
        'CE Losses',
        'PE Wins',
        'PE Losses',
        'Win Rate %',
        'Loss Rate %',
        'Max Drawdown %',
        'CAGR %',
        'Total PnL'
    ],
    'Value': [
        len(trade_df),
        wins,
        losses,
        ce_wins,
        ce_losses,
        pe_wins,
        pe_losses,
        round(win_rate,2),
        round(loss_rate,2),
        round(max_drawdown,2),
        round(cagr,2),
        round(trade_df['GrossPnL'].sum(),2)
    ]
})

summary


# In[378]:


with pd.ExcelWriter(
    "Qode_Backtest_Result.xlsx"
) as writer:

    guide.to_excel(
        writer,
        sheet_name='Guide',
        index=False
    )

    trade_df.to_excel(
        writer,
        sheet_name='Trades',
        index=False
    )

    summary.to_excel(
        writer,
        sheet_name='Statistics',
        index=False
    )

    monthly_pnl.to_excel(
        writer,
        sheet_name='MonthlyPnL',
        index=False
    )

print("Final Excel Ready")


# In[367]:


trade_df['EntryDate'] = trade_df['Date']
trade_df['ExitDate'] = trade_df['Date']


# In[368]:


trade_df = trade_df[
[
'EntryDate',
'ExitDate',
'EntryTime',
'ExitTime',
'Ticker',
'StrikePrice',
'OptionType',
'EntryPrice',
'ExitPrice',
'Quantity',
'EntryValue',
'ExitValue',
'GrossPnL',
'CumulativePnL',
'AvailableCapital'
]
]


# In[372]:


trade_df['EntryDate'] = pd.to_datetime(trade_df['EntryDate'])

trade_df['Month'] = trade_df['EntryDate'].dt.strftime('%b-%Y')


# In[373]:


monthly_pnl = (
    trade_df
    .groupby('Month', as_index=False)['GrossPnL']
    .sum()
)

monthly_pnl.columns = ['Month', 'PnL']

monthly_pnl


# In[374]:


trade_df['MonthSort'] = trade_df['EntryDate'].dt.to_period('M')

monthly_pnl = (
    trade_df
    .groupby('MonthSort', as_index=False)['GrossPnL']
    .sum()
)

monthly_pnl['Month'] = (
    monthly_pnl['MonthSort']
    .dt.strftime('%b-%Y')
)

monthly_pnl = monthly_pnl[
    ['Month', 'GrossPnL']
]

monthly_pnl.columns = ['Month', 'PnL']

monthly_pnl


# In[377]:


trade_df = trade_df.drop(
    columns=['Month', 'MonthSort']
)


# In[379]:


import matplotlib.pyplot as plt

plt.figure(figsize=(12,6))

nav.plot(linewidth=2)

plt.title(
    "09:20 AM Short Strangle Strategy - Equity Curve",
    fontsize=14
)

plt.xlabel("Trading Days")
plt.ylabel("Portfolio Value (₹)")

plt.grid(True, alpha=0.3)

plt.tight_layout()

plt.savefig(
    "Equity_Curve.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# In[ ]:





# In[ ]:




