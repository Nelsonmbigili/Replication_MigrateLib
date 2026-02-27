import pandas as pd


def gsheet_csv_url(file_id: str, sheet_id: str):
    return f"https://docs.google.com/spreadsheets/d/{file_id}/export?gid={sheet_id}&format=csv"


def read_gsheet(file_id: str, sheet_id: str, index_col: str = None):
    gsheet_url = gsheet_csv_url(file_id, sheet_id)
    return pd.read_csv(gsheet_url, index_col=index_col, keep_default_na=False, na_values=["@{}]#"]).to_dict(
        orient='records')
