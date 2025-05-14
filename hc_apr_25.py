# =================================== IMPORTS ================================= #

import pandas as pd 
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import dash
from dash import dcc, html
from collections import Counter

# Google Web Credentials
import json
import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 'data/~$bmhc_data_2024_cleaned.xlsx'
# print('System Version:', sys.version)

# ------ Pandas Display Options ------ #
pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns (if needed)
pd.set_option('display.width', 1000)  # Adjust the width to prevent line wrapping
pd.reset_option('display.max_columns')
# -------------------------------------- DATA ------------------------------------------- #

current_dir = os.getcwd()
current_file = os.path.basename(__file__)
script_dir = os.path.dirname(os.path.abspath(__file__))
# data_path = 'data/Submit_Review_Responses.xlsx'
# file_path = os.path.join(script_dir, data_path)
# data = pd.read_excel(file_path)
# df = data.copy()

# Define the Google Sheets URL
sheet_url = "https://docs.google.com/spreadsheets/d/1EXmlLJ2epGxnFcreWFp4p4ShHFyWcuUfEtC3SIjwkKA/edit?resourcekey=&gid=1922572542#gid=1922572542"

# Define the scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials
encoded_key = os.getenv("GOOGLE_CREDENTIALS")

if encoded_key:
    json_key = json.loads(base64.b64decode(encoded_key).decode("utf-8"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json_key, scope)
else:
    creds_path = r"C:\Users\CxLos\OneDrive\Documents\BMHC\Data\bmhc-timesheet-4808d1347240.json"
    if os.path.exists(creds_path):
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    else:
        raise FileNotFoundError("Service account JSON file not found and GOOGLE_CREDENTIALS is not set.")
    
expected_headers = [

]

# Authorize and load the sheet
client = gspread.authorize(creds)
sheet = client.open_by_url(sheet_url)
# worksheet = sheet.get_worksheet(0)  
# values = worksheet.get_all_values()
# headers = values[0] 
# rows = values[1:] # Remaining rows as data

# data = pd.DataFrame(rows, columns=headers)
# data = pd.DataFrame(worksheet.get_all_records())
# data = pd.DataFrame(client.open_by_url(sheet_url).get_all_records())
data = pd.DataFrame(client.open_by_url(sheet_url).sheet1.get_all_records())
df = data.copy()

# Get the reporting month:
current_month = datetime(2025, 4, 1).strftime("%B")
report_year = datetime(2025, 4, 1).strftime("%Y")

# Trim leading and trailing whitespaces from column names
df.columns = df.columns.str.strip()

# Filtered df where 'Date of Activity:' is between Ocotber to December:
df['Date of Event'] = pd.to_datetime(df['Date of Event'], errors='coerce')
df = df[df['Date of Event'].dt.month == 4]
df['Month'] = df['Date of Event'].dt.month_name()

# print(df.head(10))
# print('Total Marketing Events: ', len(df))
# print('Column Names: \n', df.columns)
# print('DF Shape:', df.shape)
# print('Dtypes: \n', df.dtypes)
# print('Info:', df.info())
# print("Amount of duplicate rows:", df.duplicated().sum())

# print('Current Directory:', current_dir)
# print('Script Directory:', script_dir)
# print('Path to data:',file_path)

# ================================= Columns ================================= #

columns =[
'Timestamp', 
'Date of Event', 
'First Name', 
'Last Name',
'Email',
'Phone Number', 
'Month'
'Column 19', 

# Visuals
'Zip Code', 
'Age', 
'Weight Lbs. (numbers only)',
'Systolic Blood Pressure',
'Diastolic Blood Pressure', 
'Heart Rate (numbers only)', 
'Was the information/ activity provided useful?', 
'Preferred Method of Contact',
'Which topics are you interested in?', 
'Are you interested in creating a Healthy Cuts account?',
'Would you like to enroll as a BMHC client/ get scheduled for an appointment?', 
'Are you interested in participating in our Movement is Medicine exercise classes?', 
'Did you have any vitals checked today?', 
'Would you like information on our partnered clinical trials, their benefits to you, and compensation amount?', 

# Table
'Do you have any feedback about this engagement?', 
]

# =============================== Missing Values ============================ #

# missing = df.isnull().sum()
# print('Columns with missing values before fillna: \n', missing[missing > 0])

# ============================== Data Preprocessing ========================== #

# Check for duplicate columns
# duplicate_columns = df.columns[df.columns.duplicated()].tolist()
# print(f"Duplicate columns found: {duplicate_columns}")
# if duplicate_columns:
#     print(f"Duplicate columns found: {duplicate_columns}")

df.rename(
    columns={
        # Numeric
        'Zip Code': 'ZIP',
        'Age': 'Age',
        'Weight Lbs. (numbers only)': 'Weight',
        'Systolic Blood Pressure': 'Systolic',
        'Diastolic Blood Pressure': 'Diastolic',
        'Heart Rate (numbers only)': 'Heart Rate',
        
        # Yes/ No
        'Was the information/ activity provided useful?': 'Info Useful',
        'Are you interested in creating a Healthy Cuts account?': 'Healthy Cuts',
        'Would you like to enroll as a BMHC client/ get scheduled for an appointment?': 'Enroll',
        'Are you interested in participating in our Movement is Medicine exercise classes?': 'MIM',
        'Did you have any vitals checked today?': 'Vitals',
        'Would you like information on our partnered clinical trials, their benefits to you, and compensation amount?': 'Clinical Trials',
        
        # Other
        'Preferred Method of Contact': 'Contact Method',
        'Which topics are you interested in?': 'Topics',
        'Do you have any feedback about this engagement?': 'Feedback',
    },
    inplace=True
)

# ------------------------ Total Reviews ---------------------------- #

hc_interactions = len(df)
# print('Total Reviews:', total_engagements)

# ------------------------------- Age Distribution ---------------------------- #

# print("Age Unique Before: \n", df['Age'].unique().tolist())
# print("Age Value Counts Before: \n", df['Age'].value_counts())

df['Age'].replace("", pd.NA, inplace=True)
age_mode = df['Age'].mode()[0]
# print("Age Mode: ", age_mode)

df['Age'] = (
    df['Age']
        .astype(str)
        .str.strip()
        .replace({
            pd.NA: age_mode,
        })
)

# convert to numeric, forcing errors to NaN
df['Age'] = pd.to_numeric(df['Age'], errors='coerce')

# print("Age Unique After: \n", df['Age'].unique().tolist())
# print("Age Value Counts After: \n", df['Age'].value_counts())

# Function to categorize ages into age groups
def categorize_age(age):
    if age == "":
        return age_mode
    elif 10 <= age <= 19:
        return '10-19'
    elif 20 <= age <= 29:
        return '20-29'
    elif 30 <= age <= 39:
        return '30-39'
    elif 40 <= age <= 49:
        return '40-49'
    elif 50 <= age <= 59:
        return '50-59'
    elif 60 <= age <= 69:
        return '60-69'
    elif 70 <= age <= 79:
        return '70-79'
    else:
        return '80+'

 # Apply the function to create the 'Age_Group' column
df['Age_Group'] = df['Age'].apply(categorize_age)
df_decades = df.groupby('Age_Group',  observed=True).size().reset_index(name='Count')

# print("Age Group Unique After: \n", df['Age_Group'].unique().tolist())
print("Age Group Value Counts After: \n", df['Age_Group'].value_counts())

# Sort the result by the minimum age in each group
age_order = [
            '10-19',
            '20-29', 
            '30-39', 
            '40-49', 
            '50-59', 
            '60-69', 
            '70-79',
            '80+'
             ]

df_decades['Age_Group'] = pd.Categorical(df_decades['Age_Group'], categories=age_order, ordered=True)
df_decades = df_decades.sort_values('Age_Group')
# print(df_decades.value_counts())

# Age Bar Chart
age_fig=px.bar(
    df_decades,
    x='Age_Group',
    y='Count',
    color='Age_Group',
    text='Count',
).update_layout(
    height=700, 
    width=1000,
    title=dict(
        text=f'{current_month} Client Age Distribution',
        x=0.5, 
        font=dict(
            size=25,
            family='Calibri',
            color='black',
            )
    ),
    font=dict(
        family='Calibri',
        size=18,
        color='black'
    ),
    xaxis=dict(
        tickangle=0,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            # text=None,
            text="Age Group",
            font=dict(size=20),  # Font size for the title
        ),
    ),
    yaxis=dict(
        title=dict(
            text='Number of Visits',
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        title_text='',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        visible=False
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='auto',
    hovertemplate='<b>Age:</b>: %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Pie chart showing values and percentages:

# # Age Pie Chart
age_pie = px.pie(
    df_decades,
    names='Age_Group',
    values='Count',
).update_layout(
    height=700, 
    title=f'{current_month} Client Age Distribution',
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    # textinfo='value+percent',
    texttemplate='%{value} (%{percent:.2%})',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# ---------------------- Zip 2 --------------------- #

# print('ZIP Unique Before: \n', df['ZIP'].unique().tolist())

zip_unique =[

]
        
zip_mode = df['ZIP'].mode()[0]

df['ZIP'] = (
    df['ZIP']
    .astype(str)
    .str.strip()
    .replace({
        "": zip_mode,
    })
)

df['ZIP'] = df['ZIP'].fillna(zip_mode)
df['ZIP'] = df['ZIP'].astype(str)

df_z = df['ZIP'].value_counts().reset_index(name='Count')

# print('ZIP Unique After: \n', df_z['ZIP'].unique().tolist())

zip_fig =px.bar(
    df_z,
    x='Count',
    y='ZIP',
    color='ZIP',
    text='Count',
    orientation='h'  # Horizontal bar chart
).update_layout(
    title='Number of Clients by Zip Code',
    xaxis_title='Residents',
    yaxis_title='Zip Code',
    title_x=0.5,
    height=950,
    width=1500,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    ),
        yaxis=dict(
        tickangle=0  # Keep y-axis labels horizontal for readability
    ),
        legend=dict(
        title='ZIP Code',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        xanchor="left",  # Anchor legend to the left
        y=1,  # Position legend at the top
        yanchor="top"  # Anchor legend at the top
    ),
).update_traces(
    textposition='auto',  # Place text labels inside the bars
    textfont=dict(size=30),  # Increase text size in each bar
    # insidetextanchor='middle',  # Center text within the bars
    textangle=0,            # Ensure text labels are horizontal
    hovertemplate='<b>ZIP Code</b>: %{y}<br><b>Count</b>: %{x}<extra></extra>'
)

# =============================== Was the information useful? ============================ #

# print("Info Useful Unique Before: \n", df['Info Useful'].unique().tolist())
# print("Info Useful Value Counts: \n", df['Info Useful'].value_counts())

df['Info Useful'] = (df['Info Useful']
    .astype(str)
    .str.strip()
    .replace({
        "" : "N/A"
    })          
)

# print("Info Useful Unique After: \n", df['Info Useful'].unique().tolist())

df_useful = df['Info Useful'].value_counts().reset_index(name='Count')

useful_fig = px.bar(
    df_useful, 
    x='Info Useful', 
    y='Count',
    color='Info Useful', 
    text='Count',  
).update_layout(
    height=600, 
    width=1050,
    title=dict(
        text=f'{current_month} Was the information useful?',
        x=0.5, 
        font=dict(
            size=22,
            family='Calibri',
            color='black',
        )
    ),
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    ),
    xaxis=dict(
        title=dict(
            # text=None,
            text="Response",
            font=dict(size=20), 
        ),
        tickmode='array',
        tickangle=0,
        # showticklabels=True,
        showticklabels=False,
    ),
    yaxis=dict(
        title=dict(
            # text=None,
            text="Count",
            font=dict(size=20), 
        ),
    ),
    legend=dict(
        title='',
        orientation="v",
        x=1.05,
        xanchor="left",
        y=1,
        yanchor="top"
    ),
    # margin=dict(t=60, r=0, b=70, l=0),
).update_traces(
    texttemplate='%{text}',
    textfont=dict(size=20),  
    textposition='auto', 
    textangle=0, 
    hovertemplate='<b>Response</b>: %{x}<br><b>Count</b>: %{y}<extra></extra>'
)

useful_pie = px.pie(
    df_useful,
    names='Info Useful',
    values='Count',
    color='Info Useful',
).update_layout(
    height=600,
    title=dict(
        x=0.5,
        text=f'{current_month} Ratio of Was the information useful?', 
        font=dict(
            size=22,  
            family='Calibri',  
            color='black'  
        ),
    ),  
    legend=dict(
        # title='Rating',
        title=None,
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        xanchor="left",  # Anchor legend to the left
        y=1,  # Position legend at the top
        yanchor="top" 
    ),
    margin=dict(t=60, r=0, b=60, l=0)  
).update_traces(
    rotation=-40,  #
    textfont=dict(size=19),  
    texttemplate='%{value} (%{percent:.2%})',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# =============================== Interested in Healthy Cuts ? ============================ #

# print("Healthy Cuts Unique Before: \n", df['Healthy Cuts'].unique().tolist())
# print("Healthy Cuts Value Counts: \n", df['Healthy Cuts'].value_counts())

df['Healthy Cuts'] = (df['Healthy Cuts']
    .astype(str)
    .str.strip()
    .replace({
        "" : "N/A"
    })          
)

# print("Healthy Cuts Unique After: \n", df['Healthy Cuts'].unique().tolist())

df_hc = df['Healthy Cuts'].value_counts().reset_index(name='Count')

hc_fig = px.bar(
    df_hc, 
    x='Healthy Cuts', 
    y='Count',
    color='Healthy Cuts', 
    text='Count',  
).update_layout(
    height=600, 
    width=1050,
    title=dict(
        text=f'{current_month} Interested in Becoming a Healthy Cuts Member?',
        x=0.5, 
        font=dict(
            size=22,
            family='Calibri',
            color='black',
        )
    ),
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    ),
    xaxis=dict(
        title=dict(
            text="Response",
            font=dict(size=20), 
        ),
        tickmode='array',
        tickangle=0,
        # showticklabels=True,
        showticklabels=False,
    ),
    yaxis=dict(
        title=dict(
            text="Count",
            font=dict(size=20), 
        ),
    ),
    legend=dict(
        title='',
        orientation="v",
        x=1.05,
        xanchor="left",
        y=1,
        yanchor="top"
    ),
).update_traces(
    texttemplate='%{text}',
    textfont=dict(size=20),  
    textposition='auto', 
    textangle=0, 
    hovertemplate='<b>Response</b>: %{x}<br><b>Count</b>: %{y}<extra></extra>'
)

hc_pie = px.pie(
    df_hc,
    names='Healthy Cuts',
    values='Count',
    color='Healthy Cuts',
).update_layout(
    height=600,
    title=dict(
        x=0.5,
        text=f'{current_month} Interested in Becoming a Healthy Cuts Member?', 
        font=dict(
            size=22,  
            family='Calibri',  
            color='black'  
        ),
    ),  
    legend=dict(
        title=None,
        orientation="v",
        x=1.05,
        xanchor="left",
        y=1,
        yanchor="top" 
    ),
    margin=dict(t=60, r=0, b=60, l=0)  
).update_traces(
    rotation=-40,
    textfont=dict(size=19),  
    texttemplate='%{value}<br>(%{percent:.2%})',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# =============================== Enroll as BMHC client? ============================ #

# print("Enroll Unique Before: \n", df['Enroll'].unique().tolist())
# print("Enroll Value Counts: \n", df['Enroll'].value_counts())

df['Enroll'] = (df['Enroll']
    .astype(str)
    .str.strip()
    .replace({
        "" : "N/A"
    })          
)

# print("Enroll Unique After: \n", df['Enroll'].unique().tolist())

df_enroll = df['Enroll'].value_counts().reset_index(name='Count')

enroll_fig = px.bar(
    df_enroll, 
    x='Enroll', 
    y='Count',
    color='Enroll', 
    text='Count',  
).update_layout(
    height=600, 
    width=1050,
    title=dict(
        text=f'{current_month} Interested in Enrolling as a BMHC Client?', 
        x=0.5, 
        font=dict(
            size=22,
            family='Calibri',
            color='black',
        )
    ),
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    ),
    xaxis=dict(
        title=dict(
            text="Response",
            font=dict(size=20), 
        ),
        tickmode='array',
        tickangle=0,
        # showticklabels=True,
        showticklabels=False,
    ),
    yaxis=dict(
        title=dict(
            text="Count",
            font=dict(size=20), 
        ),
    ),
    legend=dict(
        title='',
        orientation="v",
        x=1.05,
        xanchor="left",
        y=1,
        yanchor="top"
    ),
).update_traces(
    texttemplate='%{text}',
    textfont=dict(size=20),  
    textposition='auto', 
    textangle=0, 
    hovertemplate='<b>Response</b>: %{x}<br><b>Count</b>: %{y}<extra></extra>'
)

enroll_pie = px.pie(
    df_enroll,
    names='Enroll',
    values='Count',
    color='Enroll',
).update_layout(
    height=600,
    title=dict(
        x=0.5,
        text=f'{current_month} Ratio of Interested in Enrolling as a BMHC Client?', 
        font=dict(
            size=22,  
            family='Calibri',  
            color='black'  
        ),
    ),  
    legend=dict(
        title=None,
        orientation="v",
        x=1.05,
        xanchor="left",
        y=1,
        yanchor="top" 
    ),
    margin=dict(t=60, r=0, b=60, l=0)  
).update_traces(
    rotation=-40,
    textfont=dict(size=19),  
    texttemplate='%{value}<br>(%{percent:.2%})',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)


# ============= Interested in participating in Movement is Medicine? ================= #

# print("MIM Unique Before: \n", df['MIM'].unique().tolist())
# print("MIM Value Counts: \n", df['MIM'].value_counts())

df['MIM'] = (df['MIM']
    .astype(str)
    .str.strip()
    .replace({
        "" : "N/A"
    })          
)

# print("MIM Unique After: \n", df['MIM'].unique().tolist())

df_mim = df['MIM'].value_counts().reset_index(name='Count')

mim_fig = px.bar(
    df_mim, 
    x='MIM', 
    y='Count',
    color='MIM', 
    text='Count',  
).update_layout(
    height=600, 
    width=1050,
    title=dict(
        text=f'{current_month} Interested in Movement is Medicine Exercise Classes?',
        x=0.5, 
        font=dict(
            size=22,
            family='Calibri',
            color='black',
        )
    ),
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    ),
    xaxis=dict(
        title=dict(
            text="Response",
            font=dict(size=20), 
        ),
        tickmode='array',
        tickangle=0,
        # showticklabels=True,
        showticklabels=False,
    ),
    yaxis=dict(
        title=dict(
            text="Count",
            font=dict(size=20), 
        ),
    ),
    legend=dict(
        title='',
        orientation="v",
        x=1.05,
        xanchor="left",
        y=1,
        yanchor="top"
    ),
).update_traces(
    texttemplate='%{text}',
    textfont=dict(size=20),  
    textposition='auto', 
    textangle=0, 
    hovertemplate='<b>Response</b>: %{x}<br><b>Count</b>: %{y}<extra></extra>'
)

mim_pie = px.pie(
    df_mim,
    names='MIM',
    values='Count',
    color='MIM',
).update_layout(
    height=600,
    title=dict(
        x=0.5,
        text=f'{current_month} Interested in Movement is Medicine Exercise Classes?', 
        font=dict(
            size=22,  
            family='Calibri',  
            color='black'  
        ),
    ),  
    legend=dict(
        title=None,
        orientation="v",
        x=1.05,
        xanchor="left",
        y=1,
        yanchor="top" 
    ),
    margin=dict(t=60, r=0, b=60, l=0)  
).update_traces(
    rotation=-40,
    textfont=dict(size=19),  
    texttemplate='%{value}<br>(%{percent:.2%})',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# =============================== Did you have vitals checked today? ============================ #

# print("Vitals Unique Before: \n", df['Vitals'].unique().tolist())
# print("Vitals Value Counts: \n", df['Vitals'].value_counts())

df['Vitals'] = (df['Vitals']
    .astype(str)
    .str.strip()
    .replace({
        "" : "N/A"
    })          
)

# print("Vitals Unique After: \n", df['Vitals'].unique().tolist())

df_vitals = df['Vitals'].value_counts().reset_index(name='Count')

vitals_fig = px.bar(
    df_vitals, 
    x='Vitals', 
    y='Count',
    color='Vitals', 
    text='Count',  
).update_layout(
    height=600, 
    width=1050,
    title=dict(
        text=f'{current_month} Did You Have Any Vitals Checked Today?',
        x=0.5, 
        font=dict(
            size=22,
            family='Calibri',
            color='black',
        )
    ),
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    ),
    xaxis=dict(
        title=dict(
            text="Response",
            font=dict(size=20), 
        ),
        tickmode='array',
        tickangle=0,
        # showticklabels=True,
        showticklabels=False,
    ),
    yaxis=dict(
        title=dict(
            text="Count",
            font=dict(size=20), 
        ),
    ),
    legend=dict(
        title='',
        orientation="v",
        x=1.05,
        xanchor="left",
        y=1,
        yanchor="top"
    ),
).update_traces(
    texttemplate='%{text}',
    textfont=dict(size=20),  
    textposition='auto', 
    textangle=0, 
    hovertemplate='<b>Response</b>: %{x}<br><b>Count</b>: %{y}<extra></extra>'
)

vitals_pie = px.pie(
    df_vitals,
    names='Vitals',
    values='Count',
    color='Vitals',
).update_layout(
    height=600,
    title=dict(
        x=0.5,
        text=f'{current_month} Did You Have Any Vitals Checked Today?', 
        font=dict(
            size=22,  
            family='Calibri',  
            color='black'  
        ),
    ),  
    legend=dict(
        title=None,
        orientation="v",
        x=1.05,
        xanchor="left",
        y=1,
        yanchor="top" 
    ),
    margin=dict(t=60, r=0, b=60, l=0)  
).update_traces(
    rotation=-40,
    textfont=dict(size=19),  
    texttemplate='%{value}<br>(%{percent:.2%})',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# ================= Would you like information on our partnered clinical trials? ==================== #

# print("Clinical Trials Unique Before: \n", df['Clinical Trials'].unique().tolist())
# print("Clinical Trials Value Counts: \n", df['Clinical Trials'].value_counts())

df['Clinical Trials'] = (df['Clinical Trials']
    .astype(str)
    .str.strip()
    .replace({
        "" : "N/A"
    })          
)

# print("Clinical Trials Unique After: \n", df['Clinical Trials'].unique().tolist())

df_clinical_trials = df['Clinical Trials'].value_counts().reset_index(name='Count')

clinical_fig = px.bar(
    df_clinical_trials, 
    x='Clinical Trials', 
    y='Count',
    color='Clinical Trials', 
    text='Count',  
).update_layout(
    height=600, 
    width=1050,
    title=dict(
        text=f'{current_month} Interested in Clinical Trials Information?',
        x=0.5, 
        font=dict(
            size=22,
            family='Calibri',
            color='black',
        )
    ),
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    ),
    xaxis=dict(
        title=dict(
            text="Response",
            font=dict(size=20), 
        ),
        tickmode='array',
        tickangle=0,
        # showticklabels=True,
        showticklabels=False,
    ),
    yaxis=dict(
        title=dict(
            text="Count",
            font=dict(size=20), 
        ),
    ),
    legend=dict(
        title='',
        orientation="v",
        x=1.05,
        xanchor="left",
        y=1,
        yanchor="top"
    ),
).update_traces(
    texttemplate='%{text}',
    textfont=dict(size=20),  
    textposition='auto', 
    textangle=0, 
    hovertemplate='<b>Response</b>: %{x}<br><b>Count</b>: %{y}<extra></extra>'
)

clinical_pie = px.pie(
    df_clinical_trials,
    names='Clinical Trials',
    values='Count',
    color='Clinical Trials',
).update_layout(
    height=600,
    title=dict(
        x=0.5,
        text=f'{current_month} Interested in Clinical Trials Information?', 
        font=dict(
            size=22,  
            family='Calibri',  
            color='black'  
        ),
    ),  
    legend=dict(
        title=None,
        orientation="v",
        x=1.05,
        xanchor="left",
        y=1,
        yanchor="top" 
    ),
    margin=dict(t=60, r=0, b=60, l=0)  
).update_traces(
    rotation=-40,
    textfont=dict(size=19),  
    texttemplate='%{value}<br>(%{percent:.2%})',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# =============================== Preferred Method of Contact? ============================ #

# print("Contact Method Unique Before: \n", df['Contact Method'].unique().tolist())
# print("Contact Method Value Counts: \n", df['Contact Method'].value_counts())

df['Contact Method'] = (df['Contact Method']
    .astype(str)
    .str.strip()
    .replace({
        "" : "N/A"
    })          
)

contact_categories = [
    "Email",
    "Text Message",
    "Phone Call",
    "N/A",
]

normalized_categories = {cat.lower().strip(): cat for cat in contact_categories}

# Counter to count matches
counter = Counter()

for entry in df['Contact Method']:
    items = [i.strip().lower() for i in entry.split(",")]
    for item in items:
        if item in normalized_categories:
            counter[normalized_categories[item]] += 1
            
# for category, count in counter.items():
#     print(f"Contact Counts: \n {category}: {count}")

# print("Contact Method Unique After: \n", df['Contact Method'].unique().tolist())

# df_contact_method = df['Contact Method'].value_counts().reset_index(name='Count')

df_contact_method = pd.DataFrame(counter.items(), columns=['Contact Method', 'Count']).sort_values(by='Count', ascending=False)

contact_fig = px.bar(
    df_contact_method, 
    x='Contact Method', 
    y='Count',
    color='Contact Method', 
    text='Count',  
).update_layout(
    height=600, 
    width=1050,
    title=dict(
        text=f'{current_month} Preferred Method of Contact',
        x=0.5, 
        font=dict(
            size=22,
            family='Calibri',
            color='black',
        )
    ),
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    ),
    xaxis=dict(
        title=dict(
            text="Method",
            font=dict(size=20), 
        ),
        tickmode='array',
        tickangle=0,
        showticklabels=False,
    ),
    yaxis=dict(
        title=dict(
            text="Count",
            font=dict(size=20), 
        ),
    ),
    legend=dict(
        title='',
        orientation="v",
        x=1.05,
        xanchor="left",
        y=1,
        yanchor="top"
    ),
).update_traces(
    texttemplate='%{text}',
    textfont=dict(size=20),  
    textposition='auto', 
    textangle=0, 
    hovertemplate='<b>Method</b>: %{x}<br><b>Count</b>: %{y}<extra></extra>'
)

contact_pie = px.pie(
    df_contact_method,
    names='Contact Method',
    values='Count',
    color='Contact Method',
).update_layout(
    height=600,
    title=dict(
        x=0.5,
        text=f'{current_month} Preferred Method of Contact', 
        font=dict(
            size=22,  
            family='Calibri',  
            color='black'  
        ),
    ),  
    legend=dict(
        title=None,
        orientation="v",
        x=1.05,
        xanchor="left",
        y=1,
        yanchor="top" 
    ),
    margin=dict(t=60, r=0, b=60, l=0)  
).update_traces(
    rotation=-40,
    textfont=dict(size=19),  
    texttemplate='%{value}<br>(%{percent:.2%})',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# =============================== Which topics are you interested in? ============================ #

# print("Topics Unique Before: \n", df['Topics'].unique().tolist())
# print("Topics Value Counts: \n", df['Topics'].value_counts())

df['Topics'] = (df['Topics']
    .astype(str)
    .str.strip()
    .replace({
        "" : "N/A",
        "Preventative Care (e.g., screenings, healthy lifestyle)" : "Preventative Care"
    })          
)

topics_categories = [
    "Health Insurance Options",
    "Preventative Care",
    "Mental Health Resources",
    "Chronic Disease Management",
]

normalized_categories = {cat.lower().strip(): cat for cat in topics_categories}

# Counter to count matches
counter = Counter()

for entry in df['Topics']:
    items = [i.strip().lower() for i in entry.split(",")]
    for item in items:
        if item in normalized_categories:
            counter[normalized_categories[item]] += 1
            
# for category, count in counter.items():
#     print(f"Contact Counts: \n {category}: {count}")

# print("Topics Unique After: \n", df['Topics'].unique().tolist())

# df_topics = df['Topics'].value_counts().reset_index(name='Count')

df_topics = pd.DataFrame(counter.items(), columns=['Topics', 'Count']).sort_values(by='Count', ascending=False)

topics_fig = px.bar(
    df_topics, 
    x='Topics', 
    y='Count',
    color='Topics', 
    text='Count',  
).update_layout(
    height=600, 
    width=1050,
    title=dict(
        text=f'{current_month} Topics of Interest',
        x=0.5, 
        font=dict(
            size=22,
            family='Calibri',
            color='black',
        )
    ),
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    ),
    xaxis=dict(
        title=dict(
            text="Topic",
            font=dict(size=20), 
        ),
        tickmode='array',
        tickangle=0,
        showticklabels=False,
    ),
    yaxis=dict(
        title=dict(
            text="Count",
            font=dict(size=20), 
        ),
    ),
    legend=dict(
        title='',
        orientation="v",
        x=1.05,
        xanchor="left",
        y=1,
        yanchor="top"
    ),
).update_traces(
    texttemplate='%{text}',
    textfont=dict(size=20),  
    textposition='auto', 
    textangle=0, 
    hovertemplate='<b>Topic</b>: %{x}<br><b>Count</b>: %{y}<extra></extra>'
)

topics_pie = px.pie(
    df_topics,
    names='Topics',
    values='Count',
    color='Topics',
).update_layout(
    height=600,
    title=dict(
        x=0.5,
        text=f'{current_month} Topics of Interest', 
        font=dict(
            size=22,  
            family='Calibri',  
            color='black'  
        ),
    ),  
    legend=dict(
        title=None,
        orientation="v",
        x=1.05,
        xanchor="left",
        y=1,
        yanchor="top" 
    ),
    margin=dict(t=60, r=0, b=60, l=0)  
).update_traces(
    rotation=-40,
    textfont=dict(size=19),  
    texttemplate='%{value}<br>(%{percent:.2%})',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# ========================== Feedback Table ========================== #

df_feedback = df[['Feedback']]

# exclude empty rows
df_feedback = df_feedback[df_feedback['Feedback'].str.strip() != '']

# Engagement Table
feedback_table = go.Figure(data=[go.Table(
    # columnwidth=[50, 50, 50],  # Adjust the width of the columns
    header=dict(
        values=list(df_feedback.columns),
        fill_color='paleturquoise',
        align='center',
        height=30,  # Adjust the height of the header cells
        # line=dict(color='black', width=1),  # Add border to header cells
        font=dict(size=12)  # Adjust font size
    ),
    cells=dict(
        values=[df[col] for col in df_feedback.columns],
        fill_color='lavender',
        align='left',
        height=25,  # Adjust the height of the cells
        # line=dict(color='black', width=1),  # Add border to cells
        font=dict(size=12)  # Adjust font size
    )
)])

feedback_table.update_layout(
    # margin=dict(l=0, r=0, t=0, b=0),  # Remove margins
    height=500,
    # width=800, 
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)'  # Transparent plot area
)

# ========================== DataFrame Table ========================== #

# Engagement Table
hc_table = go.Figure(data=[go.Table(
    # columnwidth=[50, 50, 50],  # Adjust the width of the columns
    header=dict(
        values=list(df.columns),
        fill_color='paleturquoise',
        align='center',
        height=30,  # Adjust the height of the header cells
        # line=dict(color='black', width=1),  # Add border to header cells
        font=dict(size=12)  # Adjust font size
    ),
    cells=dict(
        values=[df[col] for col in df.columns],
        fill_color='lavender',
        align='left',
        height=25,  # Adjust the height of the cells
        # line=dict(color='black', width=1),  # Add border to cells
        font=dict(size=12)  # Adjust font size
    )
)])

hc_table.update_layout(
    # margin=dict(l=50, r=50, t=30, b=60),  # Remove margins
    height=600,
    # width=2000,  
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)'  # Transparent plot area
)

# ============================== Dash Application ========================== #

app = dash.Dash(__name__)
server= app.server 

app.layout = html.Div(
  children=[ 
    html.Div(
        className='divv', 
        children=[ 
          html.H1(
              'Healthy Cuts Report', 
              className='title'),
          html.H2( 
              f'{current_month} {report_year}', 
              className='title2'),
          html.Div(
              className='btn-box', 
              children=[
                  html.A(
                    'Repo',
                    href= f'https://github.com/CxLos/HC_{current_month}_{report_year}',
                    className='btn'),
    ]),
  ]),    

# Data Table
html.Div(
    className='row0',
    children=[
        html.Div(
            className='table',
            children=[
                html.H1(
                    className='table-title',
                    children='Healthy Cuts Table'
                )
            ]
        ),
        html.Div(
            className='table2', 
            children=[
                dcc.Graph(
                    className='data',
                    figure=hc_table
                )
            ]
        )
    ]
),

html.Div(
    className='row1',
    children=[

        html.Div(
            className='graph11',
            children=[
                html.Div(
                    className='high3',
                    children=[f'{current_month} Healthy Cuts Interactions']
                ),
                html.Div(
                    className='circle2',
                    children=[
                        html.Div(
                            className='hilite',
                            children=[
                                html.H1(
                                    className='high4',
                                    children=[hc_interactions]
                                ),
                            ]
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className='graph22',
            children=[
                html.Div(
                    className='high1',
                    children=[f'{current_month} Placeholder']
                ),
                html.Div(
                    className='circle1',
                    children=[
                        html.Div(
                            className='hilite',
                            children=[
                                html.H1(
                                    className='high2',
                                    # children=[df_duration]
                                ),
                            ]
                        ),
                    ],
                ),
            ],
        ),
    ]
),

# ROW 1
html.Div(
    className='row1',
    children=[
        html.Div(
            className='graph1',
            children=[
                dcc.Graph(
                    figure=age_fig
                )
            ]
        ),
        html.Div(
            className='graph2',
            children=[
                dcc.Graph(
                    figure=age_pie
                )
            ]
        ),
    ]
),

# ROW 1
html.Div(
    className='row1',
    children=[
        html.Div(
            className='graph1',
            children=[
                dcc.Graph(
                    figure=useful_fig
                )
            ]
        ),
        html.Div(
            className='graph2',
            children=[
                dcc.Graph(
                    figure=useful_pie
                )
            ]
        ),
    ]
),

# ROW 1
html.Div(
    className='row1',
    children=[
        html.Div(
            className='graph1',
            children=[
                dcc.Graph(
                    figure=hc_fig
                )
            ]
        ),
        html.Div(
            className='graph2',
            children=[
                dcc.Graph(
                    figure=hc_pie
                )
            ]
        ),
    ]
),

# ROW 1
html.Div(
    className='row1',
    children=[
        html.Div(
            className='graph1',
            children=[
                dcc.Graph(
                    figure=enroll_fig
                )
            ]
        ),
        html.Div(
            className='graph2',
            children=[
                dcc.Graph(
                    figure=enroll_pie
                )
            ]
        ),
    ]
),

# ROW 1
html.Div(
    className='row1',
    children=[
        html.Div(
            className='graph1',
            children=[
                dcc.Graph(
                    figure=mim_fig
                )
            ]
        ),
        html.Div(
            className='graph2',
            children=[
                dcc.Graph(
                    figure=mim_pie
                )
            ]
        ),
    ]
),

# ROW 1
html.Div(
    className='row1',
    children=[
        html.Div(
            className='graph1',
            children=[
                dcc.Graph(
                    figure=vitals_fig
                )
            ]
        ),
        html.Div(
            className='graph2',
            children=[
                dcc.Graph(
                    figure=vitals_pie
                )
            ]
        ),
    ]
),

html.Div(
    className='row1',
    children=[
        html.Div(
            className='graph1',
            children=[
                dcc.Graph(
                    figure=clinical_fig
                )
            ]
        ),
        html.Div(
            className='graph2',
            children=[
                dcc.Graph(
                    figure=clinical_pie
                )
            ]
        ),
    ]
),

# ROW 1
html.Div(
    className='row1',
    children=[
        html.Div(
            className='graph1',
            children=[
                dcc.Graph(
                    figure=contact_fig
                )
            ]
        ),
        html.Div(
            className='graph2',
            children=[
                dcc.Graph(
                    figure=contact_pie
                )
            ]
        ),
    ]
),

# ROW 1
html.Div(
    className='row1',
    children=[
        html.Div(
            className='graph1',
            children=[
                dcc.Graph(
                    figure=topics_fig
                )
            ]
        ),
        html.Div(
            className='graph2',
            children=[
                dcc.Graph(
                    figure=topics_pie
                )
            ]
        ),
    ]
),

html.Div(
    className='row4',
    children=[
        html.Div(
            className='graph5',
            children=[
                dcc.Graph(
                    figure=zip_fig
                )
            ]
        )
    ]
),

html.Div(
    className='row0',
    children=[
        html.Div(
            className='table',
            children=[
                html.H1(
                    className='table-title',
                    children='Feedback Table'
                )
            ]
        ),
        html.Div(
            className='table22', 
            children=[
                dcc.Graph(
                    className='data',
                    figure=feedback_table
                )
            ]
        )
    ]
),
])

print(f"Serving Flask app '{current_file}'! 🚀")

if __name__ == '__main__':
    app.run_server(debug=
                   True)
                #    False)
# =================================== Updated Database ================================= #

# updated_path = f'data/Survey_{current_quarter}_{report_year}.xlsx'
# data_path = os.path.join(script_dir, updated_path)
# df.to_excel(data_path, index=False)
# print(f"DataFrame saved to {data_path}")

# updated_path1 = 'data/service_tracker_q4_2024_cleaned.csv'
# data_path1 = os.path.join(script_dir, updated_path1)
# df.to_csv(data_path1, index=False)
# print(f"DataFrame saved to {data_path1}")

# -------------------------------------------- KILL PORT ---------------------------------------------------

# netstat -ano | findstr :8050
# taskkill /PID 24772 /F
# npx kill-port 8050

# ---------------------------------------------- Host Application -------------------------------------------

# 1. pip freeze > requirements.txt
# 2. add this to procfile: 'web: gunicorn impact_11_2024:server'
# 3. heroku login
# 4. heroku create
# 5. git push heroku main

# Create venv 
# virtualenv venv 
# source venv/bin/activate # uses the virtualenv

# Update PIP Setup Tools:
# pip install --upgrade pip setuptools

# Install all dependencies in the requirements file:
# pip install -r requirements.txt

# Check dependency tree:
# pipdeptree
# pip show package-name

# Remove
# pypiwin32
# pywin32
# jupytercore

# ----------------------------------------------------

# Name must start with a letter, end with a letter or digit and can only contain lowercase letters, digits, and dashes.

# Heroku Setup:
# heroku login
# heroku create mc-impact-11-2024
# heroku git:remote -a mc-impact-11-2024
# git push heroku main

# Clear Heroku Cache:
# heroku plugins:install heroku-repo
# heroku repo:purge_cache -a mc-impact-11-2024

# Set buildpack for heroku
# heroku buildpacks:set heroku/python

# Heatmap Colorscale colors -----------------------------------------------------------------------------

#   ['aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance',
            #  'blackbody', 'bluered', 'blues', 'blugrn', 'bluyl', 'brbg',
            #  'brwnyl', 'bugn', 'bupu', 'burg', 'burgyl', 'cividis', 'curl',
            #  'darkmint', 'deep', 'delta', 'dense', 'earth', 'edge', 'electric',
            #  'emrld', 'fall', 'geyser', 'gnbu', 'gray', 'greens', 'greys',
            #  'haline', 'hot', 'hsv', 'ice', 'icefire', 'inferno', 'jet',
            #  'magenta', 'magma', 'matter', 'mint', 'mrybm', 'mygbm', 'oranges',
            #  'orrd', 'oryel', 'oxy', 'peach', 'phase', 'picnic', 'pinkyl',
            #  'piyg', 'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn',
            #  'puor', 'purd', 'purp', 'purples', 'purpor', 'rainbow', 'rdbu',
            #  'rdgy', 'rdpu', 'rdylbu', 'rdylgn', 'redor', 'reds', 'solar',
            #  'spectral', 'speed', 'sunset', 'sunsetdark', 'teal', 'tealgrn',
            #  'tealrose', 'tempo', 'temps', 'thermal', 'tropic', 'turbid',
            #  'turbo', 'twilight', 'viridis', 'ylgn', 'ylgnbu', 'ylorbr',
            #  'ylorrd'].

# rm -rf ~$bmhc_data_2024_cleaned.xlsx
# rm -rf ~$bmhc_data_2024.xlsx
# rm -rf ~$bmhc_q4_2024_cleaned2.xlsx