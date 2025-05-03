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

# --- Streamlit UI ---
st.title("🏆 Competitor Rankings Dashboard")

menu = st.sidebar.selectbox("Select View", [
    "All Competitors", "Top 5 Competitors", 
    "Stable Rankers", "Country-wise Points", 
    "Competitors Per Country", "Top Scorer"
])

if menu == "All Competitors":
    st.subheader("All Competitors with Rank and Points")
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
        st.write(get_country_points(country))

elif menu == "Competitors Per Country":
    st.subheader("Number of Competitors Per Country")
    st.bar_chart(get_competitor_count_by_country().set_index("country"))

elif menu == "Top Scorer":
    st.subheader("Competitor with Highest Points")
    st.table(get_top_scorer())

