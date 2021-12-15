import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
    backoff_factor=1
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)


def json_to_dataframe(json, single_entry: bool = False):
    if not single_entry:
        df = pd.DataFrame.from_records(json)
    else:
        df = pd.DataFrame.from_dict(json, orient='index').T
    try:
        df.createdAt = pd.to_datetime(df.createdAt).apply(lambda x: str(x).split(".")[0])
    except Exception:
        pass
    try:
        df.finishedAt = pd.to_datetime(df.finishedAt).apply(lambda x: str(x).split(".")[0])
    except Exception:
        pass
    return df
