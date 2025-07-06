import pandas as pd
import streamlit as st
import numpy as np
import mysql.connector
import matplotlib.pyplot as plt
import plotly.express as px
from mysql.connector import Error

#Function to connect to MySQL:

def get_connection():
    return mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "AKsk1705@",
        database = "ma37"
    )

def run_query(query):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]
    cursor.close()
    return pd.DataFrame(rows,columns=col_names)




st.sidebar.title("Navigation")

page = st.sidebar.radio("Insights",["Project Introduction","Temporal Analysis","Spatial Analysis","Species Analysis","Environmental Conditions",
                                "Distance and Behavior","Observer Trends","Conservation Insights"])


#------------------------------------- Project Introduction ---------------------------------------------------------------
if page == "Project Introduction":
    st.title("Bird Species Observation Analysis in Forest and Grassland")
    st.subheader("Geographic and Species Analysis")
    st.image("C:/Users/User/Desktop/guvi project1/Project2/tree_birds_grass.jpg")
    st.write("""
             The project aims to analyse the distribution and diversity of birds species in two distinct ecosystems: Forests and Grasslands. 
             The goal of this project is to understand how the environmental factors like Sky, Wind and climate influence bird populations and behavior.
            

             ** Features : **
                      The findings provide valuable insights into habitat conservation,biodiversity management and 
                      the effects of environment changes on avian communities.
             
             ** Database Used : **
                    MySQL
             """ )
    
# ----------------------------------------- Temporal Analysis ------------------------------------------------------------ 
elif page == "Temporal Analysis":
    st.title("Visualizations on Temporal Data")

    #Date filter
    min_date,max_date = pd.read_sql("SELECT MIN(Date) as Min, MAX(Date) as Max from forest_grassland",con=get_connection()).iloc[0]
    date_range = st.sidebar.date_input("Date Range",[min_date,max_date])
    
    #month filter
    month_list = ["All"] + list(pd.read_sql("SELECT DISTINCT MONTHNAME(Date) as Month FROM forest_grassland ORDER by MONTHNAME(Date)",
                                            con=get_connection())['Month'])
    selected_month=st.sidebar.selectbox("Month",month_list)

    #build where clause
    where = f"WHERE Date BETWEEN '{date_range[0]}' AND '{date_range[1]}'"
    if selected_month != "All": where += f" AND MONTHNAME(Date) = '{selected_month}'"

    # observations per year:
    q1 = f""" SELECT YEAR(Date) AS year, COUNT(*) AS Observation_count 
             from forest_grassland 
             {where}
             group by YEAR(Date)
             order by year;"""
    result1 = run_query(q1)
    st.write("Species Observations per year")
    df_year = pd.DataFrame(result1)
    st.dataframe(df_year)

    #unqiue species per month:
    q2 = f""" SELECT MONTHNAME(Date) as Month,count(distinct Common_Name) as Unique_species
             from forest_grassland
             {where}
             group by MONTH(date), MONTHNAME(Date)
             order by MONTH(Date)"""
    result2 = run_query(q2)
    st.write("Unique species per month")
    df_month = pd.DataFrame(result2)
    st.dataframe(df_month)
    st.subheader("Unique Species observed per month")
    st.bar_chart(df_month.set_index('Month'))

    #Daily observations timeline
    q3 = f""" SELECT Date,count(*) as OBSERVATIONS
              FROM forest_grassland
              {where}
              group by Date
              order by Date;
         """
    result3 = run_query(q3)
    st.write("Daily observations")
    df_day = pd.DataFrame(result3)
    st.dataframe(df_day)
    st.area_chart(df_day.set_index("Date"))

#---------------------------------------SPATIAL ANALYSIS--------------------------------------------------------------------------------------
elif page == "Spatial Analysis":
    st.title("Spatial Analysis of Bird species Observations")
    # Filter options
    #Location_Type
    locations = ["All"] + list(pd.read_sql("SELECT DISTINCT Location_Type FROM forest_grassland",con=get_connection())['Location_Type'])
    # Plots
    plots = ["All"] + list(pd.read_sql("SELECT DISTINCT Plot_Name FROM forest_grassland",con=get_connection())['Plot_Name'])
    # Regions
    regions= ["All"] +list(pd.read_sql("SELECT DISTINCT Admin_Unit_Code FROM forest_grassland",con=get_connection())['Admin_Unit_Code'])

    #Side bar filters:
    loc = st.sidebar.selectbox("Location_Type",locations)
    plot = st.sidebar.selectbox("Plot_Name",plots)
    region = st.sidebar.selectbox("Admin_Unit_Code",regions)

    #Where clause
    clauses = []
    if loc != "All":
        clauses.append(f"Location_Type = '{loc}'")
    if plot != "All":
        clauses.append(f"Plot_Name = '{plot}'")
    if region != "All":
        clauses.append(f"Admin_Unit_Code = '{region}'")

    where_sql = "WHERE " + "AND".join(clauses) if clauses else "" 

    #Location type query
    q4 = f"""SELECT Location_Type, COUNT(DISTINCT Common_Name) as Unique_species
             FROM forest_grassland
             {where_sql}
             group by Location_Type;
         """
    result4 = run_query(q4)
    df_loc = pd.DataFrame(result4)
    st.subheader("Unique species by Location_Type")
    st.dataframe(df_loc)
    st.bar_chart(df_loc.set_index("Location_Type"))

    #Unique species by Admin unit
    q5 = f"""SELECT Admin_Unit_Code, COUNT(DISTINCT Common_Name) as Unique_species 
             FROM forest_grassland
             {where_sql}
             group by Admin_Unit_Code
         """
    result5 =run_query(q5)
    df_adm = pd.DataFrame(result5)
    st.subheader("Unique species by Admin_Unit")
    st.dataframe(df_adm)
    st.bar_chart(df_adm.set_index("Admin_Unit_Code"))

    #species by plot_name
    q6 = f"""SELECT Plot_Name,COUNT(DISTINCT Common_Name) as Unique_species
             FROM forest_grassland
             {where_sql}
             group by Plot_Name
             order by Unique_species DESC LIMIT 10;
         """
    result6 = run_query(q6)
    df_plot=pd.DataFrame(result6)
    st.subheader("Unique species by plot_name")
    st.dataframe(df_plot)
    st.bar_chart(df_plot.set_index("Plot_Name"))

    #Average distance per species
    q7 = f"""SELECT Common_Name,AVG(Distance) as Avg_distance
             FROM forest_grassland
             {where_sql}
             group by Common_name
             order by Avg_distance DESC
             LIMIT 15;
         """ 
    result7 = run_query(q7)
    df_dist = pd.DataFrame(result7)
    st.subheader("Average distance per species")
    st.dataframe(df_dist)
    st.bar_chart(df_dist.set_index("Common_Name"))

#----------------------------------------------------------Species Analysis----------------------------------------------------------------
elif page == "Species Analysis":
    st.title("Bird Species Observation Dashboard")

    #load all data for filters:
    df_all = pd.read_sql("SELECT * FROM forest_grassland;",con=get_connection())

    #sidebar filters:
    species = st.sidebar.multiselect("Select Species",df_all['Common_Name'].unique())
    loc1= st.sidebar.multiselect("Location_Type",df_all['Location_Type'].unique())
    months = st.sidebar.multiselect("Month",pd.to_datetime(df_all['Date']).dt.month_name().unique())
    observers = st.sidebar.multiselect("Observer",df_all['Observer'].unique())

    #where clause:
    clause1 = []
    if species:
        clause1.append(f"Common_Name IN ({','.join([f'\"{s}\"' for s in species])})")
    if loc1:
        clause1.append(f"Location_Type IN ({','.join([f'\"{l}\"' for l in loc1])})")
    if months:
        clause1.append("MONTHNAME(Date) IN (" + ",".join([f"'{m}'" for m in months]) + ")")
    if observers:
        clause1.append(f"Observer IN ({','.join([f'\"{o}\"' for o in observers])})")

    where_sql1 = "WHERE " + " AND".join(clause1) if clause1 else "" 

    #Top observed species:
    q8 = f"""SELECT Common_Name, COUNT(*) as Observations
             FROM forest_grassland
             {where_sql1}
             group by Common_Name
             order by Observations DESC LIMIT 10;
         """
    result8 = run_query(q8)
    df_species = pd.DataFrame(result8)
    st.dataframe(df_species)
    if not df_species.empty:
        fig1 = px.bar(df_species, x="Common_Name",y="Observations",title="Top 10 observed species")
        st.plotly_chart(fig1)

    #Time series
    q9 = f"""SELECT Date,Common_Name,COUNT(*) as observations
             from forest_grassland
             {where_sql1}
             group by Date,Common_Name
             order by observations DESC LIMIT 20;
          """
    
    result9 = run_query(q9)
    df_ts = pd.DataFrame(result9)
    df_ts['Date'] = pd.to_datetime(df_ts['Date'])
    st.dataframe(df_ts)
    if not df_ts.empty:
        fig2 = px.line(df_ts,x="Date",y="observations",color = 'Common_Name',markers=True,title='Species observations over time')
        st.plotly_chart(fig2)

    #Interval length and to analyse ID methods:
    q10 = f"""SELECT Interval_Length,ID_Method,count(*) as Observations
              FROM forest_grassland
              group by Interval_Length,ID_Method
              order by Interval_length,Observations DESC;
           """
    result10 = run_query(q10)
    df_ID = pd.DataFrame(result10)
    st.dataframe(df_ID)
    if not df_ID.empty:
        fig3 = px.bar(df_ID,x="Interval_Length",y="Observations",color = "ID_Method",barmode="group",title="Number of obervations by " \
        "Interval_Length and ID_Method",labels={'Interval_Length':'Interval_Length','Observations':'Count'})
        st.plotly_chart(fig3)
    # Unique species per Admin_Unit and Location_type
    st.title("Heatmap: Species Distribution by Admin_Unit and Location_Type")

    q17 = f"""SELECT Admin_Unit_Code,Location_Type,COUNT(DISTINCT Common_Name) as Species_Count
              FROM forest_grassland
              where Admin_unit_Code is not null AND Location_Type is not null
              group by Admin_Unit_Code, Location_Type
              order by Admin_Unit_Code
            """
    
    result17 = run_query(q17)
    df_adm =pd.DataFrame(result17)
    st.dataframe(df_adm)
    fig10 = px.density_heatmap(df_adm,x="Location_Type",y="Admin_Unit_Code",z="Species_Count",
                               color_continuous_scale="Viridis",title="Species Richness by Admin_Unit and Location_Type")
    st.plotly_chart(fig10)
#----------------------------------------------Environmental Conditions --------------------------------------------------------------------
elif page == "Environmental Conditions":
    st.title("Environmental Impact on Bird Sightings")
    q11 = f"""select ROUND(Humidity,-1) as humidity_bin,count(distinct Common_Name) as Species_Count
              from forest_grassland
              where Humidity is not null
              group by humidity_bin
              order by humidity_bin;
         """
    result11 = run_query(q11)
    df_hum = pd.DataFrame(result11)
    st.dataframe(df_hum)
    st.subheader("Species Count by Humidity")
    fig4 = px.bar(df_hum,x="humidity_bin",y="Species_Count",labels={'Humidity_Bin':'Humidity(%)'})
    st.plotly_chart(fig4)

    #Observation count by sky:
    q12 = f"""SELECT Sky,count(*) as observations
              from forest_grassland
              where sky is not null
              group by sky;
            """
    result12 = run_query(q12)
    df_sky = pd.DataFrame(result12)
    st.dataframe(df_sky)
    st.subheader("Observations by Sky Conditions")
    fig5 = px.pie(df_sky,names = "Sky",values = "observations",title = "Sky Conditions during Sightings")
    st.plotly_chart(fig5)

    #Observation count by wind
    q13 = f"""SELECT Wind,Count(*) as observations
              FROM forest_grassland
              where Wind is not null
              group by Wind;
          """
    result13 = run_query(q13)
    df_wind = pd.DataFrame(result13)
    st.dataframe(df_wind)
    st.subheader("Observations by Wind Conditions")
    fig6 = px.bar(df_wind,x="Wind",y="observations",title="Observation Count by Wind")
    st.plotly_chart(fig6)

    #Distance Vs Disturbance
    q14 = f"""SELECT Disturbance,Distance,COUNT(*) as Observations
              FROM forest_grassland
              where Disturbance is not null AND Distance is not null
              group by Disturbance,Distance
              order by Disturbance
            """
    result14 = run_query(q14)
    df_dist1 = pd.DataFrame(result14)
    st.dataframe(df_dist1)
    st.subheader("Disturbance level Vs Distance")
    fig7 = px.bar(df_dist1,x="Disturbance",y="Observations",color ="Distance",barmode="group",title="Bird Sightings by Disturbance and Distance")
    st.plotly_chart(fig7)

#------------------------------------------------Distance and behaviors----------------------------------------------------------------------
elif page == "Distance and Behavior":
    st.title("Bird Distance and Behavior Dashboard")
    #species count by distance
    q15 = f""" SELECT Distance,COUNT(DISTINCT Common_Name) as Unique_Species
               FROM forest_grassland
               where Distance is not null
               GROUP BY Distance
               ORDER BY Distance;
            """
    result15 = run_query(q15)
    df_beh = pd.DataFrame(result15)
    st.dataframe(df_beh)
    st.subheader("Unique Species by Distance")
    fig8 = px.bar(df_beh,x="Distance",y="Unique_Species",color="Distance")
    st.plotly_chart(fig8)

    # Flyover observed trends
    q16 = f"""SELECT Common_Name,Count(*) as Total_Observations, SUM(Flyover_Observed = TRUE) as Flyover_Count
              FROM forest_grassland
              group by Common_Name
              order by Flyover_Count DESC
              LIMIT 10;
            """
    result16=run_query(q16)
    df_fly = pd.DataFrame(result16)
    df_fly['Flyover_Rate(%)']=(df_fly['Flyover_Count']/df_fly['Total_Observations'])*100
    st.dataframe(df_fly)
    st.subheader("Top 10 Flyover prone Species")
    fig9 = px.bar(df_fly,x='Common_Name',y='Flyover_Rate(%)',title="Flyover Rate by Species")
    st.plotly_chart(fig9)

#----------------------------------------------Observer_Trends------------------------------------------------------------------------------
elif page == "Observer Trends":
    st.title("Observer and Visit trends in species Observations")

    #Total Observations per observer
    q18 = f"""SELECT Observer,COUNT(*) as Total_Observations
              FROM forest_grassland
              where Observer is not null
              group by Observer
              order by Total_Observations DESC; 
            """
    result18 = run_query(q18)
    df_obs = pd.DataFrame(result18)
    st.dataframe(df_obs)
    st.subheader("Observers by Species Total observations")
    fig11 = px.bar(df_obs,x='Observer',y='Total_Observations',color="Observer")
    st.plotly_chart(fig11)
    # Species diversity by Species Diversity
    q19 = f"""SELECT Observer,COUNT(DISTINCT Common_Name) AS Unique_species
              FROM forest_grassland
              where Observer is not null
              group by Observer
              order by Unique_species DESC;
            """
    result19 = run_query(q19)
    df_div = pd.DataFrame(result19)
    st.dataframe(df_div)
    st.subheader("Observers by Species Diversity")
    fig12 = px.bar(df_div,x='Observer',y='Unique_species',color='Observer')
    st.plotly_chart(fig12)
    #Unique Species by visit
    q20 = f"""SELECT Visit,COUNT(DISTINCT Common_Name) as Unique_Species
              FROM forest_grassland
              where Visit is not null
              group by Visit
              order by Visit;
            """
    result20 = run_query(q20)
    df_vis=pd.DataFrame(result20)
    st.dataframe(df_vis)
    st.subheader("Species Diversity by Visit number")
    fig13 = px.line(df_vis,x="Visit",y="Unique_Species",markers=True)
    st.plotly_chart(fig13)

#---------------------------------------------------------Conservation Insights----------------------------------------------------------------
else:
    st.title("Conservation Insights Dashboard")
    q21 = f"""SELECT PIF_Watchlist_Status,Regional_Stewardship_Status,COUNT(DISTINCT Common_Name) as Species_Count
              FROM forest_grassland
              group by PIF_Watchlist_Status,Regional_Stewardship_Status;
            """
    result21=run_query(q21)
    df_risk = pd.DataFrame(result21)
    st.dataframe(df_risk)
    st.subheader("At-Risk Species Summary")
    fig14 = px.bar(df_risk,x="PIF_Watchlist_Status",y="Species_Count",color="Regional_Stewardship_Status",barmode="group",
                   title="Species at risk by PIF and Regional stewardship")
    st.plotly_chart(fig14)
    #Top AOU codes:
    q22 = f"""SELECT AOU_Code,COUNT(DISTINCT Common_Name) as Species_Count
              FROM forest_grassland
              where AOU_Code is not null
              group by AOU_Code
              order by Species_Count DESC
              LIMIT 20;
            """
    result22=run_query(q22)
    df_aou = pd.DataFrame(result22)
    st.dataframe(df_aou)
    st.subheader("Top 20 AOU Codes by Species Count")
    fig15 = px.bar(df_aou,x="AOU_Code",y="Species_Count",title=" Most Represented AOU codes(Top 20)")
    st.plotly_chart(fig15)

    