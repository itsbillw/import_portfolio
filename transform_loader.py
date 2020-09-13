import pandas as pd

from sqlalchemy import create_engine

engine = create_engine('sqlite:///data/saved_loader_files.sqlite3', echo=False)

required_columns = ["ISIN","VALUE","CURRENCY"]
supported_currencies = ["AUD","CAD","CHF","EUR","GBP","NOK","SEK","USD"]

def loader_prep(df):
    if set(required_columns).issubset(df.columns):
        df = df[required_columns]
        if set(df["CURRENCY"].unique().tolist()).issubset(supported_currencies):
            if pd.to_numeric(df["VALUE"], errors='coerce').notnull().all() == True:
                df = df.groupby(["ISIN","CURRENCY"]).sum().reset_index()
    return df


def combine_loaders(dataframes):
    result = pd.DataFrame()
    for dataframe in dataframes:
        result = result.append(pd.read_sql("select * from '{}'".format(dataframe), con=engine))
    result = result.groupby(["ISIN","CURRENCY"]).sum().reset_index()
    return result
