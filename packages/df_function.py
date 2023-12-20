import pandas as pd
import numpy as np

from hidrokit.contrib.taruma import hk98
from hidrokit.prep import read
from hidrokit.prep import timeseries
from hidrokit.viz import table
from hidrokit.viz import graph
from hidrokit.contrib.taruma import anfrek
import plotly.express as px

def annual_daily_max(df):
    # df annual daily max
    dfY = df.copy()
    dfY.reset_index(inplace=True)
    name_col = dfY.columns[0]
    dfY = dfY.rename(columns={name_col:'Date'})
    # Creation colonne year pour groupby
    dfY['Year'] = dfY['Date'].dt.year

    # Max journalier annuel
    dfY = dfY.groupby(['Year']).max()
    # Suppression colonne DATE
    dfY = dfY.drop(columns=['Date'])
    # Year en index
    dfY.reset_index(inplace=True)
    dfY.set_index('Year', inplace=True)
    return dfY

def date_annual_daily_max(df):
    dfY_date = df.copy()

    dfY_date['Year'] = dfY_date.index.year
    dfY_date['month'] = dfY_date.index.month

    # dfY_date = dfY_date.groupby('Year').idxmax() # Deprecated
    dfY_date = dfY_date.groupby('Year').apply(lambda x: x.idxmax(skipna=True))
    dfY_date = dfY_date.drop(columns='month')

    # dfY_plt = dfY.copy()
    # dfY_plt['Year'] = dfY_plt.index
    return dfY_date

def max_mensuel(df):
    list_month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    dfM = df.resample('M').max()
    dfM['Month'] = dfM.index.month
    dfM = dfM.groupby('Month').max()
    dfM['Months'] = list_month
    dfM.set_index('Months',inplace=True)
    return dfM

def nb_rainday_month(df):
    dfM_nbP = df.copy()
    list_month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    # On masque les 0 et les nan avec valeur none
    # dfM_nbP = dfM_nbP.applymap(lambda x: x if x != 0 and not np.isnan(x) else None) # applymap deprecated
    dfM_nbP = dfM_nbP.map(lambda x: x if x != 0 and not np.isnan(x) else None)
    dfM_nbP = dfM_nbP.resample('M').apply(lambda x: np.nan if x.isnull().all() else x.count()) # car si juste .count resultat 0 quand pour annee avec None
    dfM_nbP = dfM_nbP.copy()
    dfM_nbP['Month'] = dfM_nbP.index.month
    dfM_nbP = dfM_nbP.groupby('Month').mean()
    dfM_nbP['Months'] = list_month
    dfM_nbP.set_index('Months',inplace=True)
    return dfM_nbP

def month_cumul_mean(dfCM):
    dfMM = dfCM.copy()
    list_month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    dfMM['Month'] = dfMM.index.month

    dfMM = dfMM.groupby('Month').mean(numeric_only=True)
    # dfMM = dfMM.groupby('Month').sum(numeric_only=True)
    dfMM['Months'] = list_month
    dfMM.set_index('Months',inplace=True)
    return dfMM


def generate_summary_single(dataframe, n_days="1MS"):
    def days(vector):
        return len(vector)

    def sum(vector):
        return vector.sum().round(3)

    def n_rain(vector):
        return (vector > 0).sum()

    def n_dry(vector):
        return np.logical_or(vector.isna(), vector == 0).sum()

    def max_date(vector):
        if vector.any():
            return vector.idxmax().date()
        else:
            return pd.NaT

    def max(vector):
        return vector.max()

    ufunc = [days, max, sum, n_rain, n_dry, max_date]
    ufunc_col = ["days", "max", "sum", "n_rain", "n_dry", "max_date"]

    summary = hk98.summary_all(
        dataframe, ufunc=ufunc, ufunc_col=ufunc_col, n_days=n_days
    )

    return summary.infer_objects()


def var_hk98(df_source,var):
    df = df_source.copy()
    # df = df.reset_index(inplace=True)
    df.columns = [' '.join(col).strip() for col in df.columns.values]
    df.rename(columns={'a Unnamed: 0_level_1': 'a', 'b Unnamed: 1_level_1': 'b'}, inplace=True)

    df.reset_index(inplace=True)
    df = df.melt(id_vars=['Date',], var_name='station_variable', value_name='value')
    df['Station'] = df['station_variable'].str.extract('(\w+)', expand=False)
    df['func'] = df['station_variable'].str.extract('(\S+)$', expand=False)
    df.drop(columns='station_variable', inplace=True)

    df_var = df[df['func'] == var].copy().dropna()
    df_var = df_var.replace(0, pd.NA).dropna()
    df_var['Date'] = pd.to_datetime(df_var['Date'])
    df_var['value'] = pd.to_numeric(df_var['value'], errors='coerce')

    return df_var

def plot_hk98(df_var,var,trend_or_not):
    if trend_or_not:
        fig = px.scatter(df_var, x="Date", y="value", size="value",color="Station", trendline="ols")
    else :
        fig = px.scatter(df_var, x="Date", y="value", size="value",color="Station")

    fig.update_layout(xaxis_title='Date', yaxis_title=var)

    # Loop sur chaque station 
    for i, station in enumerate(df_var['Station'].unique()):
        df_station = df_var[df_var['Station'] == station].copy()
        station_name = df_station['Station'].iat[0]

        desired_trace = None
        for trace in fig.data:
            if trace.name == station_name:
                desired_trace = trace
                break
        color = desired_trace['marker']['color'] 

        # Ajoute une trace de ligne avec la même couleur
        if len(df_var['Station'].unique()) < 4:
            fig.add_trace(px.line(df_station, x="Date", y="value").update_traces(line=dict(dash="dot", color=color)).data[0])
        
        df_station['value'] = pd.to_numeric(df_station['value'], errors='coerce')

        # Regression lineaire
        days_since_reference = (df_station['Date'] - df_station['Date'].min()).dt.days
        df_station['Days since ref'] = days_since_reference
        coefficients = np.polyfit(days_since_reference, df_station['value'], 1)

        # Calcul du coefficient
        residuals = df_station['value'] - (coefficients[0] * days_since_reference + coefficients[1])
        r_squared = 1 - (np.sum(residuals**2) / np.sum((df_station['value'] - np.mean(df_station['value']))**2))

        equation = f"{station_name}<br>y = {coefficients[0]:.2f}x + {coefficients[1]:.2f}, R² = {r_squared:.2f}"
        x_position = df_station['Date'].iloc[-1]  # Position sur l'axe x
        y_position = df_station['value'].iloc[-1]  # Position sur l'axe y
        # fig.add_annotation(
        #     x=x_position,
        #     y=y_position+y_position/10,
        #     text=equation,
        #     showarrow=False,
        #     font=dict(size=10, color="black"),
        #     bgcolor="white",
        #     opacity=0.8,
        #     xref='x',
        #     yref='y',
        #     xshift=10,
        #     yshift=10
        # )

    return fig
