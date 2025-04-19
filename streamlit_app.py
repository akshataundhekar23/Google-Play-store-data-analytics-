import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Load data
df = pd.read_csv("C:/Users/Lenovo/OneDrive/New folder/playstore_dashboard/googleplaystore.csv")

# Fix and convert Size column
def convert_size(size):
    try:
        if 'M' in size:
            return float(size.replace('M', '').strip())
        elif 'k' in size or 'K' in size:
            return float(size.replace('k', '').replace('K', '').strip()) / 1000
        else:
            return None
    except:
        return None

df['Size'] = df['Size'].astype(str).apply(convert_size)
df = df.dropna(subset=['Size'])

# Clean Installs and Price, calculate Revenue
df['Installs'] = df['Installs'].astype(str).str.replace(r'[+,]', '', regex=True).astype(float)
df['Price'] = df['Price'].astype(str).str.replace('$', '', regex=False)
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

# Calculate Revenue
df['Revenue'] = df['Installs'] * df['Price']

# Current time in IST
now = datetime.now()
current_hour = now.hour

st.title("📊 Google Play Store Dashboard")

# ---------- Task 1: Scatter Plot ----------
st.subheader("1️⃣ Revenue vs Installs (Paid Apps Only)")
paid_apps = df[df['Type'] == 'Paid']
fig1 = px.scatter(
    paid_apps,
    x='Installs',
    y='Revenue',
    color='Category',
    trendline='ols',
    title='Revenue vs Installs for Paid Apps',
    size_max=60,
    template='plotly_white'
)
st.plotly_chart(fig1, use_container_width=True)

# ---------- Task 2: Dual Axis Chart (1 PM - 2 PM IST) ----------
if 00 <= current_hour < 1:
    st.subheader("2️⃣ Free vs Paid Apps: Avg Installs & Revenue (Top 3 Categories)")

    filtered_df = df[
        (df['Installs'] >= 10000) &
        (df['Revenue'] >= 10000) &
        (df['Android Ver'].astype(str).str.extract('(\d+\.\d+)', expand=False).astype(float) > 4.0) &
        (df['Size'] > 15) &
        (df['Content Rating'] == 'Everyone') &
        (df['App'].str.len() <= 30)
    ]

    top3_categories = filtered_df['Category'].value_counts().nlargest(3).index
    filtered_df = filtered_df[filtered_df['Category'].isin(top3_categories)]

    grouped = filtered_df.groupby(['Category', 'Type']).agg({
        'Installs': 'mean',
        'Revenue': 'mean'
    }).reset_index()

    fig2 = px.bar(
        grouped,
        x='Category',
        y='Installs',
        color='Type',
        barmode='group',
        title='Avg Installs by App Type in Top 3 Categories',
        labels={'Installs': 'Average Installs'},
    )

    fig2.add_scatter(
        x=grouped['Category'],
        y=grouped['Revenue'],
        mode='markers+lines',
        name='Revenue',
        marker=dict(size=10, color='black'),
        yaxis='y2'
    )

    fig2.update_layout(
        yaxis=dict(title='Average Installs'),
        yaxis2=dict(title='Average Revenue', overlaying='y', side='right'),
        template='plotly_white'
    )

    st.plotly_chart(fig2, use_container_width=True)

# ---------- Task 3: Violin Plot (4 PM - 6 PM IST) ----------
if 00 <= current_hour < 1:
    st.subheader("3️⃣ Rating Distribution by Category")

    filtered_violin = df[
        (df['App'].str.contains('C', case=False)) &
        (df['Reviews'].astype(float) >= 10) &
        (df['Rating'] < 4.0)
    ]

    category_counts = filtered_violin['Category'].value_counts()
    valid_categories = category_counts[category_counts > 50].index
    filtered_violin = filtered_violin[filtered_violin['Category'].isin(valid_categories)]

    fig3 = px.violin(
        filtered_violin,
        y='Rating',
        x='Category',
        box=True,
        points='all',
        title='Rating Distribution for Selected Categories',
        template='plotly_white'
    )

    st.plotly_chart(fig3, use_container_width=True)

# Footer
st.markdown("---")
st.caption("© 2025 Dhruv | Google Play Store Dashboard")
