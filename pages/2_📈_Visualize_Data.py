import streamlit as st
import pandas as pd
from packages.main import *
import plotly.express as px
import plotly.graph_objects as go

service_name = "dynamodb"
region = "eu-central-1"
table_name = "NeuraBubbleUID_Validator"


def main():
    st.title('NeuraBubbles Data')
    side_bar()


@st.cache_data
def fetch_data():
    access_id, access_key = load_token()
    client = DynamoDB(access_id, access_key, service_name, region, table_name)

    # connect to DynamoDB
    client.connect()

    # get models table
    table = client.get_table()
    return table["Items"]


def side_bar():
    data = fetch_data()

    clean_df, usages_df = pre_process_data(data)

    st.sidebar.header("Filters")
    anon_id = st.sidebar.button("Anonymized ID")
    side = st.sidebar.button("Aneurysm Side")
    aneurysm_type = st.sidebar.button("Types of Aneurysm")
    raptured = st.sidebar.button("Raptured")
    shipped = st.sidebar.button("Shipped Status")
    shipped_location = st.sidebar.button("Shipped Location")
    usage_count = st.sidebar.button("Usage Count")

    st.sidebar.button("No Filters")

    if raptured:
        st.subheader("Raptured NeuraBubbles")
        st.bar_chart(clean_df["raptured"].value_counts())
    elif shipped:
        st.subheader("NeuraBubbles Shipping Status")
        st.bar_chart(clean_df["shippedStatus"].value_counts())
    elif usage_count:
        st.subheader("NeuraBubbles Usage Count")
        st.bar_chart(clean_df["usageCount"].value_counts())
    elif aneurysm_type:
        st.subheader("NeuraBubbles Aneurysm Type")
        st.bar_chart(clean_df["Aneurysm_Type"].value_counts())
    elif side:
        st.subheader("Aneurysm Side of the Head")
        fig = go.Figure(data=[go.Pie(labels=clean_df["Aneurysm_Side"].unique(), values=clean_df["Aneurysm_Side"].value_counts())])
        st.plotly_chart(fig)
    elif anon_id:
        st.subheader("Patient Anonymized ID")
        st.bar_chart(clean_df["Anonymized_ID"].value_counts())
    elif shipped_location:
        st.subheader("Shipping Destination")
        shipped_df = clean_df["destinationShipped"].value_counts()
        fig = go.Figure(
            data=[go.Pie(values=shipped_df.values, labels=list(shipped_df.index))])
        st.plotly_chart(fig)
        st.bar_chart(clean_df["destinationShipped"].value_counts())

    else:
        st.dataframe(clean_df)


@st.cache_data
def pre_process_data(json_data):
    df = pd.DataFrame(json_data)

    df[["Aneurysm_Type", "Aneurysm_Side", "Anonymized_ID", "NeuraBubble_ID"]] = df["ID"].str.split(" ", expand=True)

    usages_df = df[["usages", "UID"]]

    df.drop(["ID", "usages"], inplace=True, axis=1)

    return df, usages_df


# TODO: Complete plot function
def plot(df, group_by):
    features = df.columns.pop()

    st.bar_chart(df.groupby(group_by)["Anonymized_ID"])


if __name__ == "__main__":
    main()
