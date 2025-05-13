# =================================== IMPORTS ================================= #
import csv, sqlite3
import re
import numpy as np 
import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt 
import plotly.figure_factory as ff
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
from folium.plugins import MousePosition
import plotly.express as px
from datetime import datetime
import folium
import os
import sys
# ------
import json
import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials
# ------
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.development.base_component import Component

# 'data/~$bmhc_data_2024_cleaned.xlsx'
# print('System Version:', sys.version)
# -------------------------------------- DATA ------------------------------------------- #

current_dir = os.getcwd()
current_file = os.path.basename(__file__)
script_dir = os.path.dirname(os.path.abspath(__file__))
# data_path = 'data/Engagement_March_2025.xlsx'
# file_path = os.path.join(script_dir, data_path)
# data = pd.read_excel(file_path)
# df = data.copy()

# Define the Google Sheets URL
sheet_url = "https://docs.google.com/spreadsheets/d/1D0oOioAfJyNCHhJhqFuhxxcx3GskP9L-CIL1DcOyhug/edit?resourcekey=&gid=1261604285#gid=1261604285"

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

# Authorize and load the sheet
client = gspread.authorize(creds)
sheet = client.open_by_url(sheet_url)
data = pd.DataFrame(client.open_by_url(sheet_url).sheet1.get_all_records())
df = data.copy()

# Trim leading and trailing whitespaces from column names
df.columns = df.columns.str.strip()

# Trim whitespace from values in all columns
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Define a discrete color sequence
# color_sequence = px.colors.qualitative.Plotly

df['Date of Activity'] = pd.to_datetime(df['Date of Activity'], errors='coerce')

# Filtered df where 'Date of Activity:' is january to april
df = df[df['Date of Activity'].dt.month.isin([1, 2, 3, 4])]

# Get the reporting month:
current_month = datetime(2025, 4, 1).strftime("%B")
report_year = datetime(2025, 4, 1).strftime("%Y")

# print(df.head(10))
# print('Total Marketing Events: ', len(df))
# print('Column Names: \n', df.columns.tolist())
# print('DF Shape:', df.shape)
# print('Dtypes: \n', df.dtypes)
# print('Info:', df.info())
# print("Amount of duplicate rows:", df.duplicated().sum())
# print('Current Directory:', current_dir)
# print('Script Directory:', script_dir)
# print('Path to data:',file_path)

# ================================= Columns ================================= #

columns = [
    'Timestamp',
    'Date of Activity', 
    'Person submitting this form:',
    'Activity Duration (minutes):', 
    'Care Network Activity:', 
    'Entity name:', 
    'Brief Description:', 
    'Activity Status:', 
    'BMHC Administrative Activity:', 
    'Total travel time (minutes):', 
    'Community Outreach Activity:', 
    'Number engaged at Community Outreach Activity:', 
    'Any recent or planned changes to BMHC lead services or programs?'
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

# Rename columns
df.rename(
    columns={
        "Activity Duration (minutes):": "Activity Duration",
        "Total travel time (minutes):": "Travel",
        "Person submitting this form:": "Person",
        "Activity Status:": "Activity Status",
        "Entity name:": "Entity",
        "Care Network Activity:": "Care Activity",
        "BMHC Administrative Activity:": "Admin Activity",
        "Community Outreach Activity:": "Outreach Activity",
        "Number engaged at Community Outreach Activity:": "Number Engaged",
    }, 
inplace=True)

# print('Entity Names:', df['Entity'].unique().tolist())

entitiy_unique = [
     'GUD LIFE - BMHC - Pflugerville', 'GUD LIFE met with Dominique', 'GUD LIFE Board & Executive Staff', 'GUD LIFE - Potential with Lone Star Circle of Care', 'GudLife','GUD LIFE: AL Community Development Corporation - ALCDC - BizNess Program,  Helpers of Change','GUD LIFE - Central Texas Learning Festival', 'Unparallel Preparatory Academy', 'GUD LIFE & Building Promises', 'GUD LIFE & ALC', 'Gudlife', 'Bristol Myers', 'Healing Hands Birthing Project', 'American YouthWorks', 'St David’s Foundation', 'Cardurion Pharm', 'GUD LIFE & BMHC & Integral Care Scheduling Meeting - Emails', 'GudLife, Integral Care',"GudLife, Integral Care", "Black Men's Health Clinic, Austin Spurs", "Black Men's Health Clinic, GudLife", 'GudLife, ALCDC Board', "Black Men's Health Clinic, City of Austin"
]

df['Entity'] = (
    df['Entity']
    .replace({
        'GUD LIFE - BMHC - Pflugerville': 'GudLife',
        'GUD LIFE met with Dominique': 'GudLife',
        'GUD LIFE Board & Executive Staff': 'GudLife',
        'GUD LIFE - Potential with Lone Star Circle of Care': 'GudLife',
        'GUD LIFE: AL Community Development Corporation - ALCDC - BizNess Program,  Helpers of Change': 'GudLife',
        'GUD LIFE - Central Texas Learning Festival': 'GudLife',
        'GUD LIFE & Building Promises': 'GudLife',
        'GUD LIFE & ALC': 'GudLife',
        'GudLife': 'GudLife',
        'Gudlife': 'GudLife',
        'GudLife, Integral Care': 'GudLife',
        "GudLife, Integral Care": 'GudLife',
        "Black Men's Health Clinic, GudLife": 'GudLife',
        'GudLife, ALCDC Board': 'GudLife',
        'BMHC': 'BMHC',
        'GUD LIFE (BMHC)': 'GudLife'
    })
)

# Normalize any "Gud Life", "GUD LIFE", "Gudlife", etc., to "GudLife" using regex
df['Entity'] = df['Entity'].str.replace(r'gud\s*life', 'GudLife', flags=re.IGNORECASE, regex=True)


# df['Entity'] = df['Entity'].replace(
#     to_replace=r'\bGUD[\s]?LIFE\b|\bGud[\s]?Life\b', 
#     value='GudLife', 
#     regex=True
# )

# 
df = df[df['Entity'] == 'GudLife']

# ========================= Total Engagements ========================== #

# Total number of engagements:
total_engagements = len(df)
# print('Total Engagements:', total_engagements)

# -------------------------- Engagement Hours -------------------------- #

# Sum of 'Activity Duration (minutes):' dataframe converted to hours:

# Convert 'Activity Duration (minutes):' to numeric
df['Activity Duration'] = pd.to_numeric(df['Activity Duration'], errors='coerce')
engagement_hours = df['Activity Duration'].sum()/60
engagement_hours = round(engagement_hours)

# -------------------------- Total Travel Time ------------------------ #

df['Travel'] = (
    df['Travel']
    .replace({
    'Sustainable Food Center + APH Health Education Strategy Meeting & Planning Activities', 
    0
}))

df['Travel'] = pd.to_numeric(df['Travel'], errors='coerce').fillna(0)

# Sum travel time in hours and round
total_travel_time = round(df['Travel'].sum() / 60)
# print(total_travel_time)

# travel time value counts
# print(df['Total travel time (minutes):'].value_counts())

# ---------------------------- Activity Status ----------------------- #

df_activity_status = df.groupby('Activity Status').size().reset_index(name='Count')

status_bar=px.bar(
    df_activity_status,
    x='Activity Status',
    y='Count',
    color='Activity Status',
    text='Count',
).update_layout(
    height=460, 
    width=780,
    title=dict(
        text='Activity Status',
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
            text="Status",
            font=dict(size=20),  # Font size for the title
        ),
        # showticklabels=False  # Hide x-tick labels
        showticklabels=True  # Hide x-tick labels
    ),
    yaxis=dict(
        title=dict(
            text='Count',
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        # title='Support',
        title_text='',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        # visible=False
        visible=True
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='auto',
    hovertemplate='<b>Status:</b> %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Support Pie Chart
status_pie = px.pie(
    df_activity_status,
    names='Activity Status',
    values='Count',
).update_layout(
    title='Activity Status',
    height=450,
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    rotation=0,
    textinfo='value+percent',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# ----------------------------- Admin Activity --------------------------- #

# print("Admin Unique Before: \n", df['Admin Activity'].unique().tolist())

categories = [
    '100 Black Men of Austin Quarterly Partnership Review (QPR)',
    'Any Baby Can Tour & Partnership Meeting',
    'BMHC + Breakthrough of Central Texas Partnership Discussion',
    'BMHC + Community First Village Neighborhood Care Team Planning Meeting',
    'BMHC + Community First Village Onsite Outreach Strategy Huddle',
    'BMHC + Community First Village Onsite Outreach Strategy Planning Huddle',
    'BMHC + Gudlife Outreach Strategy Huddle',
    'BMHC + Gudlife Strategy Huddle',
    'BMHC + KAZI Basketball Tournament',
    'BMHC Gudlife Meeting',
    'BMHC Pflugerville Asset Mapping Activities',
    'BMHC Tour (Austin Mayor Kirk Watson & Austin City Council Member District 4 "Chito" Vela)',
    'Biweekly PSH staffing with ECHO',
    'Child Inc Travis County HeadStart Program (Fatherhood Program Event)',
    'Communication & Correspondence',
    'Community First Village Onsite Outreach',
    'Community First Village Outreach Strategy Huddle',
    'Compliance & Policy Enforcement',
    'Downtown Austin Community Court Onsite Outreach',
    'End of Week 1 to 1 Performance Review',
    'Financial & Budgetary Management',
    'HR Support',
    'Housing Authority of Travis County (Self-Care Day) Outreach Event',
    'Housing Authority of Travis County Quarterly Partnership Review (QPR)',
    'Impact Forms Follow Up Meeting',
    'Implementation Studios Planning & Strategy Meeting',
    'Meeting with Cameron',
    'Onboarding',
    'Outreach & Navigation Leads 1 to 1 Strategy Meeting',
    'Outreach 1 to 1 Strategy Meetings',
    'Outreach Onboarding (Jordan Calbert)',
    'PSH Audit for ECHO',
    'PSH file updates and case staffing',
    'Record Keeping & Documentation',
    'Research & Planning',
    'PSH support call with Dr Wallace'
]

categories = ['1 to 1 Outreach Strategy Meetings', 'BMHC & GUD LFE Huddle Meeting', 'BMHC & GUD LIFE Weekly Huddle', 'BMHC Gudlife Huddle', 'BMHC Internal & External Emails and Phone Calls Performed', 'BOLO list and placement', 'Bi-Partner Neighbor Partner Engagement Meeting', 'Central Health Virtual Lunch', 'Communication & Correspondence', 'Community Engagement & Events', 'Community First Village Onsite Outreach & Healthy Cuts Preventative Screenings', 'End of Week Outreach Performance Reviews', 'Financial & Budgetary Management', 'HMIS monthly reports submission to ECHO', 'HR Support', 'HSO stakeholder meeting', 'Implementation Studios Planning Meeting', 'In-Person Key Leaders Huddle', 'MOU conversation with Extended Stay America', 'Manor 5K Planning Meeting & Follow Up Activities', 'Meeting', 'Outreach & Navigation Team Leads Huddle', 'Outreach Onboarding Activities (Jordan Calbert)', 'PSH', 'PSH iPilot', 'Record Keeping & Documentation', 'Research & Planning', 'Training', 'client referrals/community partnership', 'homeless advocacy meeting', 'outreach coordination meeting', 'timesheet completion and submit to Dr. Wallace', 'weekly HMIS updates and phone calls for clients on BOLO list']

df['Admin Activity'] = (
    df['Admin Activity']
    .str.strip()
    .replace({
            "" : "N/A",
        })
)


# Group by 'BMHC Administrative Activity:' dataframe:
admin_activity = df.groupby('Admin Activity').size().reset_index(name='Count')
# print(admin_activity["Admin Activity"].unique().tolist())

admin_bar=px.bar(
    admin_activity,
    x="Admin Activity",
    y='Count',
    color="Admin Activity",
    text='Count',
).update_layout(
    height=850, 
    width=1900,
    title=dict(
        text='Admin Activity Bar Chart',
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
        tickangle=-20,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            # text=None,
            text="Admin Activity",
            font=dict(size=20),  # Font size for the title
        ),
        showticklabels=False
    ),
    yaxis=dict(
        title=dict(
            text='Count',
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        title='',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        visible=True
        # visible=False
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='auto',
    hovertemplate='<b></b> %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Insurance Status Pie Chart
admin_pie=px.pie(
    admin_activity,
    names="Admin Activity",
    values='Count'
).update_layout(
    height=850,
    width=1700,
    # showlegend=False,
    showlegend=True,
    title='Admin Activity Pie Chart',
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    rotation=130,
    textinfo='value+percent',
    # textinfo='none',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>',
    # pull = [0.1 if v < 5 else 0.01 + (v / max(admin_activity["Count"]) * 0.05) for v in admin_activity["Count"]]

    # pull=[0.15 if v < 5 else 0.04 for v in admin_activity["Count"]]  # Pull out small slices more, and others slightly
    #  pull=[0.1 if v < 5 else 0 for v in admin_activity["Count"]]  # Pull out small slices more, no pull for large ones
)

# -------------------------- Care Network Activity ----------------------- #

print("Care Network Unique \n", df['Care Activity'].unique().tolist())

df['Care Activity'] = (
    df['Care Activity']
    .str.strip()
    .replace({
            "" : "N/A",
        })
)

# Group by 'Care Network Activity:' dataframe:
care_network_activity = df.groupby('Care Activity').size().reset_index(name='Count')

# print("Care Netowrk Activities: \n", care_network_activity.value_counts())

care_bar=px.bar(
    care_network_activity,
    x="Care Activity",
    y='Count',
    color="Care Activity",
    text='Count',
).update_layout(
    height=850, 
    width=1800,
    title=dict(
        text='Care Network Activity Bar Chart',
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
        tickangle=-20,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            # text=None,
            text="Care Network Activity",
            font=dict(size=20),  # Font size for the title
        ),
        showticklabels = False
    ),
    yaxis=dict(
        title=dict(
            text='Count',
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        title='',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        # visible=False
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='auto',
    hovertemplate='<b></b> %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Insurance Status Pie Chart
care_pie=px.pie(
    care_network_activity,
    names="Care Activity",
    values='Count'
).update_layout(
    height=850,
    width=1700,
    # showlegend=False,
    title='Care Network Activity Pie Chart',
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    rotation=140,
    textinfo='value+percent',
    # textinfo='none',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>',
    # pull=[0.15 if v < 5 else 0.04 for v in admin_activity["Count"]]  # Pull out small slices more, and others slightly
)

# --------------------------Community Outreach Activity ---------------------- #

# Replace values in the original DataFrame before grouping
df['Outreach Activity'] = (
    df['Outreach Activity']
    .str.strip()
    .replace({
            "" : "N/A",
            "NA" : "N/A",
        })
)

# Group by 'Community Outreach Activity:' dataframe
community_outreach_activity = df.groupby('Outreach Activity').size().reset_index(name='Count')

# print(community_outreach_activity.value_counts())

community_bar=px.bar(
    community_outreach_activity,
    x="Outreach Activity",
    y='Count',
    color="Outreach Activity",
    text='Count',
).update_layout(
    height=850, 
    width=1800,
    title=dict(
        text='Community Outreach Activity Bar Chart',
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
        tickangle=-20,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            # text=None,
            text="Community Outreach Activity",
            font=dict(size=20),  # Font size for the title
        ),
        showticklabels=False
        # showticklabels=True 
    ),
    yaxis=dict(
        title=dict(
            text="Count",
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        title="",
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        visible=True
        # visible=False
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textangle=0,
    textposition='auto',
    hovertemplate='<b></b> %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Insurance Status Pie Chart
community_pie=px.pie(
    community_outreach_activity,
    names="Outreach Activity",
    values='Count'
).update_layout(
    height=850,
    width=1700,
    title='Community Outreach Activity Pie Chart',
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    rotation=10,
    textinfo='value+percent',
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>',
    # The code is creating a list called `pull` using a list comprehension. For each value `v` in the
    # "Count" column of the `admin_activity` DataFrame (assuming it's a pandas DataFrame), it assigns
    # 0.15 to the corresponding element in `pull` if `v` is less than 5, and 0.05 if `v` is greater
    # than or equal to 5. This code is essentially adjusting the values based on the condition
    # provided.
    # pull=[0.15 if v < 5 else 0.05 for v in admin_activity["Count"]]  # Pull out small slices more, and others slightly
)

# ------------------------ Person Submitting Form -------------------- #

#  Unique values:

# 'Antonio Montgomery'
#  'Cameron Morgan' 
#  'Dominique Street' 
#  'Jordan Calbert'
#  'KAZI 88.7 FM Radio Interview & Preparation'
#  'Kim Holiday'
#  'Kiounis Williams' 
#  'Larry Wallace Jr.'
#  'Sonya Hosey' 
#  'Toya Craney'

df['Person'] = (
    df['Person']
    .str.strip()
    .replace({
        "Larry Wallace Jr": "Larry Wallace Jr.", 
        "Antonio Montggery": "Antonio Montgomery",
        "KAZI 88.7 FM Radio Interview & Preparation" : "Unknown",
        "Eric roberts" : "Eric Roberts",
        "Eric Robert" : "Eric Roberts",
    })
)

# df['Person submitting this form:'] = df['Person submitting this form:'].replace("Kiounis Williams ", "Kiounis Williams")

df_person = df.groupby('Person').size().reset_index(name='Count')
# print(df_person.value_counts())
# print(df_person["Person submitting this form:"].unique())

person_bar=px.bar(
    df_person,
    x='Person',
    y='Count',
    color='Person',
    text='Count',
).update_layout(
    height=650, 
    width=840,
    title=dict(
        text='People Submitting Forms',
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
        tickangle=-15,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            # text=None,
            text="Name",
            font=dict(size=20),  # Font size for the title
        ),
        showticklabels=False  # Hide x-tick labels
        # showticklabels=True  # Hide x-tick labels
    ),
    yaxis=dict(
        title=dict(
            text='Count',
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        # title='Support',
        title_text='',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        # visible=False
        visible=True
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='outside',
    hovertemplate='<b>Name:</b> %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Person Pie Chart
person_pie=px.pie(
    df_person,
    names="Person",
    values='Count'  # Specify the values parameter
).update_layout(
    height=650, 
    title='Ratio of People Filling Out Forms',
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    rotation=100,
    textposition='auto',
    textinfo='value+percent',
    hovertemplate='<b>%{label} Status</b>: %{value}<extra></extra>',
    # pull = [0.1 if v < 5 else 0.01 + (v / max(admin_activity["Count"]) * 0.05) for v in admin_activity["Count"]]
)

# # ========================== DataFrame Table ========================== #

# Engagement Table
engagement_table = go.Figure(data=[go.Table(
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

engagement_table.update_layout(
    margin=dict(l=50, r=50, t=30, b=40),  # Remove margins
    height=700,
    # width=1500,  # Set a smaller width to make columns thinner
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)'  # Transparent plot area
)

# Group by 'Entity name:' dataframe
entity_name_group = df.groupby('Entity').size().reset_index(name='Count')

# Entity Name Table
entity_name_table = go.Figure(data=[go.Table(
    header=dict(
        values=list(entity_name_group.columns),
        fill_color='paleturquoise',
        align='center',
        height=30,
        font=dict(size=12)
    ),
    cells=dict(
        values=[entity_name_group[col] for col in entity_name_group.columns],
        fill_color='lavender',
        align='left',
        height=25,
        font=dict(size=12)
    )
)])

entity_name_table.update_layout(
    margin=dict(l=50, r=50, t=30, b=40),
    height=900,
    width=780,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

# ============================== Dash Application ========================== #

import dash
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    children=[ 
        html.Div(
            className='divv', 
            children=[ 
                html.H1('GudLife Report', className='title'),
                html.H1('January - April 2025', className='title2'),
                html.Div(
                    className='btn-box', 
                    children=[
                        html.A(
                            'Repo',
                            href='https://github.com/CxLos/Eng_Mar_2025',
                            className='btn'
                        )
                    ]
                )
            ]
        ),
        
        # Data Table
        # html.Div(
        #     className='row0',
        #     children=[
        #         html.Div(
        #             className='table',
        #             children=[
        #                 html.H1(
        #                     className='table-title',
        #                     children='Engagement Data Table'
        #                 )
        #             ]
        #         ),
        #         html.Div(
        #             className='table2', 
        #             children=[
        #                 dcc.Graph(
        #                     className='data',
        #                     figure=engagement_table
        #                 )
        #             ]
        #         )
        #     ]
        # ),

        # Row 1: Engagements and Hours
        html.Div(
            className='row1',
            children=[
                html.Div(
                    className='graph11',
                    children=[
                        html.Div(className='high1', children=['GudLife Engagements:']),
                        html.Div(
                            className='circle1',
                            children=[
                                html.Div(
                                    className='hilite',
                                    children=[html.H1(className='high2', children=[total_engagements])]
                                )
                            ]
                        )
                    ]
                ),
                html.Div(
                    className='graph22',
                    children=[
                        html.Div(className='high3', children=['GudLife Hours:']),
                        html.Div(
                            className='circle2',
                            children=[
                                html.Div(
                                    className='hilite',
                                    children=[html.H1(className='high4', children=[engagement_hours])]
                                )
                            ]
                        ) 
                    ]
                )
            ]
        ),

        # Row 1: Engagements and Hours
        html.Div(
            className='row1',
            children=[
                html.Div(
                    className='graph11',
                    children=[
                        html.Div(className='high1', children=['Travel Hours']),
                        html.Div(
                            className='circle1',
                            children=[
                                html.Div(
                                    className='hilite',
                                    children=[html.H1(className='high2', children=[total_travel_time])]
                                )   
                            ]
                        )
                    ]
                ),
                html.Div(
                    className='graph2',
                    children=[
                        dcc.Graph(
                            figure=status_pie
                        )
                    ]
                )
            ]
        ),
        
        html.Div(
            className='row3',
            children=[
                html.Div(
                    className='graph33',
                    children=[
                        dcc.Graph(
                            figure=admin_bar
                        )
                    ]
                ),
            ]
        ),   
        
        html.Div(
            className='row3',
            children=[
                html.Div(
                    className='graph33',
                    children=[
                        dcc.Graph(
                            figure=admin_pie
                        )
                    ]
                ),
            ]
        ),   

        html.Div(
            className='row3',
            children=[
                html.Div(
                    className='graph33',
                    children=[
                        dcc.Graph(
                            figure=care_bar
                        )
                    ]
                ),
            ]
        ),   

        html.Div(
            className='row3',
            children=[
                html.Div(
                    className='graph33',
                    children=[
                        dcc.Graph(
                            figure=care_pie
                        )
                    ]
                ),
            ]
        ),   

        html.Div(
            className='row3',
            children=[
                html.Div(
                    className='graph33',
                    children=[
                        dcc.Graph(
                            figure=community_bar
                        )
                    ]
                ),
            ]
        ),   

        html.Div(
            className='row3',
            children=[
                html.Div(
                    className='graph33',
                    children=[
                        dcc.Graph(
                            figure=community_pie
                        )
                    ]
                ),
            ]
        ),   

        # html.Div(
        #     className='row3',
        #     children=[
        #         html.Div(
        #             className='graph1',
        #             children=[
        #                 dcc.Graph(
        #                     figure=community_bar
        #                 )
        #             ]
        #         ),
        #         html.Div(
        #             className='graph2',
        #             children=[
        #                 dcc.Graph(
        #                     figure=community_pie
        #                 )
        #             ]
        #         )
        #     ]
        # ),   

        html.Div(
            className='row3',
            children=[
                html.Div(
                    className='graph1',
                    children=[
                        dcc.Graph(
                            figure=person_bar
                        )
                    ]
                ),
                html.Div(
                    className='graph2',
                    children=[
                        dcc.Graph(
                            figure=person_pie
                        )
                    ]
                )
            ]
        ),   
        
# ROW 2
# html.Div(
#     className='row2',
#     children=[
#         html.Div(
#             className='graph3',
#             children=[
#                 html.Div(
#                     className='table',
#                     children=[
#                         html.H1(
#                             className='table-title',
#                             children='Entity Name Table'
#                         )
#                     ]
#                 ),
#                 html.Div(
#                     className='table2', 
#                     children=[
#                         dcc.Graph(
#                             className='data',
#                             # figure=entity_name_table
#                         )
#                     ]
#                 )
#             ]
#         ),
#         html.Div(
#             className='graph4',
#             children=[                
#               html.Div(
#                     className='table',
#                     children=[
#                         html.H1(
#                             className='table-title',
#                             children=''
#                         )
#                     ]
#                 ),
#                 html.Div(
#                     className='table2', 
#                     children=[
#                         dcc.Graph(
                            
#                         )
#                     ]
#                 )
   
#             ]
#         )
#     ]
# ),

        html.Div(
            className='row3',
            children=[
                html.Div(
                    className='graph33',
                    children=[
                        dcc.Graph(
                            figure=entity_name_table
                        )
                    ]
                ),
            ]
        ),   
])

print(f"Serving Flask app '{current_file}'! 🚀")

if __name__ == '__main__':
    app.run_server(debug=True)
                #    False)
# =================================== Updated Database ================================= #

# updated_path = f'data/Engagement_{current_month}_{Report Year}.xlsx'
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