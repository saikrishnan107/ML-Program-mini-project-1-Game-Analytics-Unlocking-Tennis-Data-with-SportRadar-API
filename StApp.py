import pandas as pd 
import mysql.connector
import streamlit as st 

#Connection to SQL Server 
def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='12345',
    database='tennis'
    )

# Queries 
def get_summary_stats():
    q1 = "SELECT COUNT(*) as total_competitors FROM competitors"
    q2 = "SELECT COUNT(DISTINCT country) as total_countries FROM competitors"
    q3 = """
        SELECT MAX(cr.points) as highest_points
        FROM competitor_rankings cr
    """
    conn = get_connection()
    total_competitors = pd.read_sql(q1, conn)['total_competitors'][0]
    total_countries = pd.read_sql(q2, conn)['total_countries'][0]
    highest_points = pd.read_sql(q3, conn)['highest_points'][0]
    conn.close()
    return total_competitors, total_countries, highest_points

def get_all_competitors():
    conn = get_connection()
    query = """
        SELECT c.name, cr.`rank`, cr.points 
        FROM competitors c 
        JOIN competitor_rankings cr ON c.competitor_id = cr.competitor_id;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_top_5():
    conn = get_connection()
    query = """
        SELECT c.name, cr.`rank`, cr.points 
        FROM competitors c 
        JOIN competitor_rankings cr ON c.competitor_id = cr.competitor_id
        ORDER BY cr.`rank` ASC 
        LIMIT 5;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_stable_ranks():
    conn = get_connection()
    query = """
        SELECT c.name, cr.`rank`, cr.movement 
        FROM competitors c 
        JOIN competitor_rankings cr ON c.competitor_id = cr.competitor_id
        WHERE cr.movement = 0;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_country_points(country):
    conn = get_connection()
    query = f"""
        SELECT SUM(cr.points) AS total_points
        FROM competitors c 
        JOIN competitor_rankings cr ON c.competitor_id = cr.competitor_id
        WHERE c.country = %s;
    """
    df = pd.read_sql(query, conn, params=(country,))
    conn.close()
    return df

def get_competitor_count_by_country():
    conn = get_connection()
    query = """
        SELECT country, COUNT(*) AS total_competitors
        FROM competitors
        GROUP BY country;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_top_scorer():
    conn = get_connection()
    query = """
        SELECT c.name, cr.points 
        FROM competitors c 
        JOIN competitor_rankings cr ON c.competitor_id = cr.competitor_id
        ORDER BY cr.points DESC 
        LIMIT 1;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df
def search_competitors(name):
    conn = get_connection()
    query = """
        SELECT c.name, cr.`rank`, cr.points 
        FROM competitors c 
        JOIN competitor_rankings cr ON c.competitor_id = cr.competitor_id
        WHERE c.name LIKE %s;
    """
    df = pd.read_sql(query, conn, params=(f"%{name}%",))
    conn.close()
    return df

# --- Streamlit UI ---

st.set_page_config("Tennis Competitor Dashboard", page_icon="🎾", layout="wide")
st.title("Tennis Competitor Rankings Dashboard")

menu = st.sidebar.selectbox("Select View", [
    "Dashboard","All Competitors", "Top 5 Competitors", 
    "Stable Rankers", "Country-wise Points", 
    "Competitors Per Country"
])
if menu == "Dashboard":
    st.header("Dashboard Summary")
    total_competitors, total_countries, highest_points = get_summary_stats()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Competitors", total_competitors)
    col2.metric("Countries Represented", total_countries)
    col3.metric("Highest Points", highest_points)

if menu == "All Competitors":
        st.subheader("Search Competitors")
        search_name = st.text_input("Enter Competitor Name")
        if search_name:
            df = search_competitors(search_name)
            st.dataframe(df if not df.empty else "No competitors found.")
        else:
            st.dataframe(get_all_competitors())

elif menu == "Top 5 Competitors":
    st.subheader("Top 5 Competitors by Rank")
    st.dataframe(get_top_5())

elif menu == "Stable Rankers":
    st.subheader("Competitors with Stable Rank (No Movement)")
    st.dataframe(get_stable_ranks())

elif menu == "Country-wise Points":
    st.subheader("Total Points by Country")
    country = st.text_input("Enter Country Name", value="Croatia")
    if country:
        df = get_country_points(country)
        points = int(df['total_points'].iloc[0]) if not df.empty and df['total_points'].iloc[0] else 0
        st.metric(f"Total Points for {country}", points)

elif menu == "Competitors Per Country":
    st.subheader("Number of Competitors Per Country")
    df = get_competitor_count_by_country().set_index("country")
    st.bar_chart(df)



