import streamlit as st
import pandas as pd
from packages.main import *

service_name = "dynamodb"
region = "eu-central-1"
table_name = "NeuraBubbleUID_Validator"


def main():
    st.title('NeuraBubbles Data')
    data = fetch_data()
    st.text(f"There are {len(data)} models, Visualize Raw Data?")
    status = st.button("Confirm")
    if status:
        for item in data:
            st.json(item)


@st.cache_data
def fetch_data():
    access_id, access_key = load_token()
    client = DynamoDB(access_id, access_key, service_name, region, table_name)

    # connect to DynamoDB
    client.connect()

    # get models table
    table = client.get_table()

    return table["Items"]


if __name__ == "__main__":
    main()
