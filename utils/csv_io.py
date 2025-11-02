import pandas as pd
import requests
from io import StringIO

def export_csv(df: pd.DataFrame) -> bytes:
    """
    DataFrameをCSV文字列に変換して返す
    """
    csv_data = df.to_csv(index=False)
    return csv_data.encode("utf-8")


def import_csv(file_obj, api_url: str) -> int:
    """
    アップロードされたCSVファイルを読み込み、
    FastAPI にデータをPOSTしてDBに登録する。
    成功した件数を返す。
    """
    df_new = pd.read_csv(file_obj)
    success_count = 0
    for _, row in df_new.iterrows():
        payload = {
            "date": str(row["date"]),
            "systolic": int(row["systolic"]),
            "diastolic": int(row["diastolic"]),
            "pulse": int(row["pulse"]) if not pd.isna(row["pulse"]) else None,
            "note": str(row["note"]) if not pd.isna(row["note"]) else "",
        }
        res = requests.post(f"{api_url}/bp", json=payload)
        if res.status_code == 200:
            success_count += 1
    return success_count
