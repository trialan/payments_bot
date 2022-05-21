import pandas as pd
import pymongo

def get_collection():
    client = pymongo.MongoClient()
    db = client["database"]
    col = db["transactions"]
    return col


def print_col(col):
    df = pd.DataFrame(col.find())
    print(df)
