import sys
from pathlib import Path
import pandas as pd

ROOT = Path.cwd()
if ROOT.name == "notebooks":
    ROOT = ROOT.parent
RAW, CLEAN = ROOT / "data" / "raw", ROOT / "data" / "cleaned"
sys.path.append(str(ROOT / "streamlit"))

FILES = {  # edit here if your filenames differ
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "product_category_translation": "product_category_name_translation.csv",
}
# Zip prefixes MUST be read as text, or leading zeros are lost (01310 -> 1310)
ZIP_COLS = {
    "customers": "customer_zip_code_prefix",
    "sellers": "seller_zip_code_prefix",
    "geolocation": "geolocation_zip_code_prefix",
}


def load_raw() -> dict[str, pd.DataFrame]:
    dfs = {}
    for name, fname in FILES.items():
        dtype = {ZIP_COLS[name]: str} if name in ZIP_COLS else None
        dfs[name] = pd.read_csv(RAW / fname, dtype=dtype)
    return dfs