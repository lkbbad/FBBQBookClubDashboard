import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Google Sheets setup
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Load credentials from Streamlit Secrets
try:
    credentials_dict = st.secrets["GOOGLE_SERVICE_ACCOUNT"]
    credentials = Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)
    client = gspread.authorize(credentials)
    sheet = client.open("FBBQ Onyx Storm Progress Tracker").sheet1
    st.write("Google Sheets connection successful!")
except Exception as e:
    st.error(f"Error connecting to Google Sheets: {e}")

# Helper functions for Google Sheets
def load_data():
    """Load data from the Google Sheet, or create an empty DataFrame if the sheet is blank."""
    try:
        records = sheet.get_all_records()
        if not records:  # If the sheet is empty
            return pd.DataFrame(columns=["Name", "Chapter", "Picture"])
        return pd.DataFrame(records)
    except Exception as e:
        st.error(f"Error loading data from Google Sheets: {e}")
        return pd.DataFrame(columns=["Name", "Chapter", "Picture"])

def save_data(dataframe):
    """Save data to the Google Sheet."""
    try:
        if dataframe.empty:
            sheet.clear()
            sheet.update([["Name", "Chapter", "Picture"]])  
        else:
            sheet.clear()
            sheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
    except Exception as e:
        st.error(f"Error saving data to Google Sheets: {e}")

# Load data into session state
if "progress_data" not in st.session_state:
    st.session_state.progress_data = load_data()

# List of members and their pictures
members = [
    {"Name": "Lindy", "Picture": "photos/Lindy.png"},
    {"Name": "Madison", "Picture": "photos/Madison.png"},
    {"Name": "Justine", "Picture": "photos/Justine.jpeg"},
    {"Name": "Liz", "Picture": "photos/Liz.png"},
    {"Name": "Maria", "Picture": "photos/Maria.jpeg"},
    {"Name": "Anna", "Picture": "photos/Anna.jpeg"},
    {"Name": "Kelsie", "Picture": "photos/Kelsie.png"},
    {"Name": "Caroline", "Picture": "photos/Caroline.png"},
]

# UI: Input Form
st.title("📚 FBBQ Onyx Storm Progress Tracker 🐉")

with st.form("progress_form"):
    st.subheader("Update Your Progress")
    selected_member = st.selectbox("Select Your Name", [m["Name"] for m in members])
    current_chapter = st.number_input("Current Chapter", min_value=1, step=1)
    submitted = st.form_submit_button("Update Progress")
    delete_last = st.form_submit_button("Delete Last Entry")

# Add data to the progress table
if submitted:
    member_picture = next(m["Picture"] for m in members if m["Name"] == selected_member)
    # Remove existing entry for this user
    st.session_state.progress_data = st.session_state.progress_data[
        st.session_state.progress_data["Name"] != selected_member
    ]
    # Add the new entry
    new_entry = pd.DataFrame(
        {"Name": [selected_member], "Chapter": [current_chapter], "Picture": [member_picture]}
    )
    st.session_state.progress_data = pd.concat(
        [st.session_state.progress_data, new_entry], ignore_index=True
    )
    # Save to Google Sheets
    save_data(st.session_state.progress_data)
    st.success(f"Progress updated for {selected_member}!")

# Delete the last entry
if delete_last:
    st.session_state.progress_data = st.session_state.progress_data[
        st.session_state.progress_data["Name"] != selected_member
    ]
    # Save to Google Sheets
    save_data(st.session_state.progress_data)
    st.warning(f"Last entry deleted for {selected_member}.")

# UI: Progress Dashboard
st.subheader("📊 Where the hell are we in the book? 📊")
if not st.session_state.progress_data.empty:
    sorted_data = st.session_state.progress_data.sort_values(
        "Chapter", ascending=False
    )
    for _, row in sorted_data.iterrows():
        col1, col2 = st.columns([1, 5])  # Adjust column widths as needed
        with col1:
            st.image(row["Picture"], width=80, caption=row["Name"])
        with col2:
            st.write(f"**Chapter {int(row['Chapter'])}**")
            st.progress(row["Chapter"] / 66)  # Replace 66 with the total number of chapters in your book
else:
    st.write("No progress logged yet. Use the form above to add the first entry!")

try:
    credentials_dict = st.secrets["GOOGLE_SERVICE_ACCOUNT"]
    st.write("Secrets loaded successfully!")
    credentials = Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)
    client = gspread.authorize(credentials)
    sheet = client.open("FBBQ Onyx Storm Progress Tracker").sheet1
    st.write("Google Sheets connection successful!")
except Exception as e:
    st.error(f"Error: {e}")
