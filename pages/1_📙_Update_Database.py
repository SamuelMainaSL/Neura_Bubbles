import streamlit as st
import pandas as pd
from packages.main import *

service_name = "dynamodb"
region = "eu-central-1"
table_name = "NeuraBubbleUID_Validator"
client = None


def main():
    """

    :return:
    """
    uid = st.text_input("Enter NeuraBubble UID", value="")
    if validate_uid(uid):
        if not check_uid(uid):
            add_status = st.radio(f'Do you want to Update NeuraBubble `{uid}` details?', ["Yes", 'No'], index=1)
            if add_status == "Yes":
                st.subheader("NeuraBubble Details")

                data_form(uid)

            if add_status == "Yes":
                pass

    # data = fetch_data()
    # for item in data:
    #   st.json(item)


@st.cache_data
def fetch_data():
    """

    :return: table items as a list
    """
    global client
    access_id, access_key = load_token()
    client = DynamoDB(access_id, access_key, service_name, region, table_name)

    # connect to DynamoDB
    client.connect()

    # get models table
    table = client.get_table()

    return table["Items"]


def check_uid(uid):
    df = pd.DataFrame(fetch_data(), index=None)

    if uid in list(df.UID):
        st.success("NeuraBubble UID is Already in the Database")
        uid_df = df[df.UID == uid]
        uid_df.drop("usages", axis=1, inplace=True)
        st.table(uid_df.T)

        return True
    else:
        st.warning("NeuraBubble UID Does Not Exist in the Database!")
        return False


@st.cache_data
def validate_uid(uid):
    try:
        assert len(uid) == 6
        return True

    except AssertionError:
        if len(uid) == 0:
            st.warning("Enter UID!")
        else:
            st.warning("UID Should Contain 6 Characters!")


def add_details(uid, nb_id, raptured, shipped, destination, usage_count, usages):
    details_dict = {'UID': uid,
                    'destinationShipped': destination,
                    'ID': nb_id,
                    'raptured': raptured,
                    'shippedStatus': shipped,
                    'usageCount': usage_count,
                    'usages': usages
                    }
    # TODO: add code to upload to DB

    return details_dict


def data_form(uid):
    nb_form = st.form("nb_id", clear_on_submit=True)
    aneurysm_type = nb_form.selectbox("Type of Aneurysm", ["MCA", "ICA", "PCOM", "ACOM", "BA"])
    aneurysm_side = nb_form.selectbox("Aneurysm Side", ["R", "L"])
    anonymized_id = nb_form.text_input("Anonymized ID", value="T04", help="(T04, T13, T23)")
    nb_number = nb_form.text_input("NeuraBubble Number", value="001", help="(001, 010)")
    raptured = nb_form.radio("Is the NeuraBubble Raptured?", ["Yes", "No"], index=1)
    shipped = nb_form.radio("Is the NeuraBubble Shipped?", ["Yes", "No"], index=1)

    usage_count = nb_form.number_input("Enter the NeuraBubble Usage Count", value=0, min_value=0,
                                       max_value=5)

    shipping_address = nb_form.text_input("Enter Shipping Destination")
    nb_id = f"{aneurysm_type} {aneurysm_side} {anonymized_id} {nb_number}"
    usages = {
        'timestamps': [],
        'systemIDs': [],
        'userEmailIDs': [],
        'locations': []}
    nb_form.warning("Confirm the Accuracy of the Details before Clicking Submit!")
    nb_id_status = nb_form.form_submit_button("Submit")

    json_data = add_details(uid, nb_id, raptured, shipped, shipping_address, usage_count, usages)

    if nb_id_status:
        st.success("Details Saved!")
        details, usages = get_tables(json_data)
        st.table(pd.DataFrame(details, index=["Details"]))
        if details["usageCount"] != 0:
            st.table(pd.DataFrame(usages))


def get_tables(json_data):
    json_data_copy = json_data.copy()
    usages = json_data_copy.pop("usages")

    return json_data_copy, usages


if __name__ == "__main__":
    main()
