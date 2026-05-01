import base64
import xmlrpc.client
import pandas as pd
from datetime import datetime, date
import os
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv("credentials.env")

url = os.getenv("url")
password = os.getenv("password_api")
username = os.getenv("username")
db = os.getenv("db")


common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")


ids = models.execute_kw(
    db, uid, password,
    'product.template', 'search',
    [[]],  # Empty domain - matches all records
    {'limit': 2000}  # Keyword arguments
)


records = models.execute_kw(
    db, uid, password,
    'product.template', 'read',
    [ids],
    {'fields': ['name']}
)

products = []
for record in records:
    product = {}
    product['name'] = record['name']
    products.append(product)

df = pd.DataFrame(products)
df.to_csv('data/products.csv', index=False)
