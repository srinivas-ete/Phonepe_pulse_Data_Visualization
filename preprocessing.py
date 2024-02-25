import pandas as pd
import numpy as np
import mysql.connector
import streamlit as st
import plotly.express as px
import requests
import json
from streamlit_option_menu import option_menu

myconnection=mysql.connector.connect(
    host="localhost",
    user="root",
    password="Yourpassword",
    database="phonepe_pulse"
)
mycursor=myconnection.cursor(buffered=True)

# Setting the page Configuration
st.set_page_config(page_title="Phonepe Pulse Data Visualization ",
                   layout="wide",
                   initial_sidebar_state="expanded",
                   )

# Creating logo and Title of the page
st.image("PhonePe-Logo.png", width=100)

# Home Page
def home_page():
    st.title(":violet[PhonePe Pulse Data Visualization]")

    st.write("""
        ## Welcome to PhonePe Pulse

        PhonePe Pulse is your gateway to understanding digital payment trends in India. Explore insightful information
        and discover how people across the nation are transacting digitally.

        ### Transaction Trends

        Explore transaction trends over time to understand how digital payments are evolving:

        - Analyze transaction volumes month by month.
        - Discover peak transaction periods and seasonal patterns.

        ### Top Categories and Merchants

        Explore the most popular transaction categories and merchants:

        - Discover which categories are most frequently transacted.
        - Find out which merchants attract the highest transaction volumes.

        ### Geographical Insights

        Understand digital payment adoption across different regions of India:

        - Analyze transaction trends by state and city.
        - Explore digital payment patterns in major metropolitan areas.

        """)

#Top Charts Page
def explore_data():
    st.title(':violet[EXPLORE DATA]')
    st.subheader('Analysis done on the basis of All India, States, and Top categories between 2018 and 2023')
    # Create a select widget for navigation
    select = st.selectbox("Select Analysis Type", ["INDIA", "STATES", "TOP CATEGORIES"])
    if select=="INDIA":
        tab1, tab2 = st.tabs(["TRANSACTION", "USER"])
        # TRANSACTION TAB
        with tab1:
            col1, col2, col3 = st.columns(3)
            with col1:
                trans_yr = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='trans_yr')
            with col2:
                trans_qtr = st.selectbox('**Select Quarter**', ('1', '2', '3', '4'), key='trans_qtr')
            with col3:
                trans_type = st.selectbox('**Select Transaction type**',
                                         ('Recharge & bill payments', 'Peer-to-peer payments',
                                          'Merchant payments', 'Financial Services', 'Others'), key='trans_type')

            #Transaction analysis bar chart
            mycursor.execute(
                f"select State, Transaction_amount from agg_trans where Year='{trans_yr}' and Quarter='{trans_qtr}' and Transaction_type='{trans_type}';")
            trans_tab=mycursor.fetchall()
            df_trans_rslt=pd.DataFrame(np.array(trans_tab),columns=['State','Transaction_amount'])
            df_trans_rslt1=df_trans_rslt.set_index(pd.Index(range(1,len(df_trans_rslt)+1)))

            # Transaction Analysis table
            mycursor.execute(
                f"select State, Transaction_count, Transaction_amount from agg_trans where Year = '{trans_yr}' and Quarter = '{trans_qtr}' and Transaction_type = '{trans_type}';")
            anly_tab = mycursor.fetchall()
            df_trans_anly_rslt = pd.DataFrame(np.array(anly_tab),columns=['State', 'Transaction_count', 'Transaction_amount'])
            df_trans_anly_rslt1 = df_trans_anly_rslt.set_index(pd.Index(range(1, len(df_trans_anly_rslt) + 1)))

            # Total Transaction Amount table
            mycursor.execute(
                f"SELECT SUM(Transaction_amount), AVG(Transaction_amount) FROM agg_trans WHERE Year = '{trans_yr}' AND Quarter = '{trans_qtr}' AND Transaction_type = '{trans_type}';")
            trans_amount = mycursor.fetchall()
            df_trans_amount_rslt = pd.DataFrame(np.array(trans_amount), columns=['Total', 'Average'])
            df_trans_amount_rslt1 = df_trans_amount_rslt.set_index(['Average'])

            # Total Transaction Count table
            mycursor.execute(
                f"SELECT SUM(Transaction_count), AVG(Transaction_count) FROM agg_trans WHERE Year = '{trans_yr}' AND Quarter = '{trans_qtr}' AND Transaction_type = '{trans_type}';")
            trans_count = mycursor.fetchall()
            df_trans_count_rslt = pd.DataFrame(np.array(trans_count), columns=['Total', 'Average'])
            df_trans_count_rslt1 = df_trans_count_rslt.set_index(['Average'])

            #Geo Visualization
            # Drop a State column from df_trans_rslt
            df_trans_rslt.drop(columns=['State'], inplace=True)
            # Clone the geo data
            url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
            response = requests.get(url)
            data1 = json.loads(response.content)
            # Extract state names and sort them in alphabetical order
            state_names_tra = [feature['properties']['ST_NM'] for feature in data1['features']]
            state_names_tra.sort()
            # Create a DataFrame with the state names column
            df_state_names_tra = pd.DataFrame({'State': state_names_tra})
            # Combine the Gio State name with df_trans_rslt
            df_state_names_tra['Transaction_amount'] = df_trans_rslt
            # convert dataframe to csv file
            df_state_names_tra.to_csv('Statenames.csv', index=False)
            # Read csv
            df_tra = pd.read_csv('Statenames.csv')
            # Geo plot
            fig_tra = px.choropleth(
                df_tra,
                geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                featureidkey='properties.ST_NM', locations='State', color='Transaction_amount',
                color_continuous_scale='thermal', title='Transaction Analysis')
            fig_tra.update_geos(fitbounds="locations", visible=False)
            fig_tra.update_layout(title_font=dict(size=33), title_font_color='#AD71EF', height=800)
            st.plotly_chart(fig_tra, use_container_width=True)

            #------------------ All India Transaction Analysis Bar Chart --------------------------------------#
            df_trans_rslt1['State'] = df_trans_rslt1['State'].astype(str)
            df_trans_rslt1['Transaction_amount'] = df_trans_rslt1['Transaction_amount'].astype(float)
            df_in_tr_tab_qry_rslt1_fig = px.bar(df_trans_rslt1, x='State', y='Transaction_amount',
                                                color='Transaction_amount', color_continuous_scale='thermal',
                                                title='Transaction Analysis Chart', height=700, )
            df_in_tr_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
            st.plotly_chart(df_in_tr_tab_qry_rslt1_fig, use_container_width=True)

            #------------------------ All India Transaction Calculation Table ----------------------------------#
            st.header(':violet[Total Calculation]')
            col4, col5 = st.columns(2)
            with col4:
                st.subheader(':violet[Transaction Analysis]')
                st.dataframe(df_trans_rslt1)
            with col5:
                st.subheader(':violet[Transaction Amount]')
                st.dataframe(df_trans_amount_rslt1)
                st.subheader(':violet[Transaction Count]')
                st.dataframe(df_trans_count_rslt1)
        #User Tab
        with tab2:
            col1,col2=st.columns(2)
            with col1:
                user_yr=st.selectbox('**Select Year**',('2018','2019','2020','2021','2022','2023'),key='user_yr')
            with col2:
                user_qtr=st.selectbox('**Select Quarter**',('1','2','3','4'),key='user_qtr')
             # User Analysis Bar Chart query
            mycursor.execute(f"SELECT State, SUM(Count) FROM agg_user WHERE Year = '{user_yr}' AND Quarter = '{user_qtr}' GROUP BY State;")
            user_tab= mycursor.fetchall()
            df_user_tab_rslt = pd.DataFrame(np.array(user_tab), columns=['State', 'User Count'])
            df_user_tab_rslt1 = df_user_tab_rslt.set_index(pd.Index(range(1, len(df_user_tab_rslt) + 1)))

            # Total User Count table query
            mycursor.execute(f"SELECT SUM(Count), AVG(Count) FROM agg_user WHERE Year = '{user_yr}' AND Quarter = '{user_qtr}';")
            user_count = mycursor.fetchall()
            df_user_count_rslt = pd.DataFrame(np.array(user_count), columns=['Total', 'Average'])
            df_user_count_rslt1 = df_user_count_rslt.set_index(['Average'])

            # GEO VISUALIZATION FOR USER
            # Drop a State column from df_user_tab_rslt
            df_user_tab_rslt.drop(columns=['State'], inplace=True)
            # Clone the geo data
            url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
            response = requests.get(url)
            data2 = json.loads(response.content)
            # Extract state names and sort them in alphabetical order
            state_names_use = [feature['properties']['ST_NM'] for feature in data2['features']]
            state_names_use.sort()
            # Create a DataFrame with the state names column
            df_state_names_use = pd.DataFrame({'State': state_names_use})
            # Combine the Geo State name with df_user_tab_rslt
            df_state_names_use['User Count'] = df_user_tab_rslt
            # convert dataframe to csv file
            df_state_names_use.to_csv('State_user.csv', index=False)
            # Read csv
            df_use = pd.read_csv('State_user.csv')
            # Geo plot
            fig_use = px.choropleth(
                df_use,
                geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                featureidkey='properties.ST_NM', locations='State', color='User Count',
                color_continuous_scale='thermal', title='User Analysis')
            fig_use.update_geos(fitbounds="locations", visible=False)
            fig_use.update_layout(title_font=dict(size=33), title_font_color='#AD71EF', height=800)
            st.plotly_chart(fig_use, use_container_width=True)

            # ----     All India User Analysis Bar chart       -------- #
            df_user_tab_rslt1['State'] = df_user_tab_rslt1['State'].astype(str)
            df_user_tab_rslt1['User Count'] = df_user_tab_rslt1['User Count'].astype(int)
            df_in_us_tab_qry_rslt1_fig = px.bar(df_user_tab_rslt1, x='State', y='User Count', color='User Count',
                                                color_continuous_scale='thermal', title='User Analysis Chart',
                                                height=700, )
            df_in_us_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
            st.plotly_chart(df_in_us_tab_qry_rslt1_fig, use_container_width=True)

            # -----      All India Total User calculation Table      ----- #
            st.header(':violet[Total calculation]')

            col3, col4 = st.columns(2)
            with col3:
                st.subheader(':violet[User Analysis]')
                st.dataframe(df_user_tab_rslt1)
            with col4:
                st.subheader(':violet[User Count]')
                st.dataframe(df_user_count_rslt1)

    if select =="STATES":
        tab3, tab4=st.tabs(['TRANSACTION','USER'])
        #Transaction tab for state
        with tab3:
            col1,col2,col3=st.columns(3)
            with col1:
                st_trans=st.selectbox('**Select State**',(
                    'andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh', 'assam', 'bihar',
                    'chandigarh', 'chhattisgarh', 'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat',
                    'haryana', 'himachal-pradesh',
                    'jammu-&-kashmir', 'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep', 'madhya-pradesh',
                    'maharashtra', 'manipur',
                    'meghalaya', 'mizoram', 'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan', 'sikkim',
                    'tamil-nadu', 'telangana',
                    'tripura', 'uttar-pradesh', 'uttarakhand', 'west-bengal'),key='st_trans')
            with col2:
                st_yr=st.selectbox('**Select Year**',('2018','2019','2020','2021','2022','2023'),key='st_yr')
            with col3:
                st_qtr=st.selectbox('**Select Quarter**',('1','2','3','4'),key='st_qtr')
            #Transaction Analysis Bar Chart query
            mycursor.execute(f"SELECT Transaction_type, Transaction_amount FROM agg_trans WHERE State = '{st_trans}' AND Year = '{st_yr}' AND Quarter = '{st_qtr}';")
            st_tr_tab_bar_qry_rslt = mycursor.fetchall()
            df_st_tr_tab_bar_qry_rslt = pd.DataFrame(np.array(st_tr_tab_bar_qry_rslt), columns=['Transaction_type', 'Transaction_amount'])
            df_st_tr_tab_bar_qry_rslt1 = df_st_tr_tab_bar_qry_rslt.set_index(pd.Index(range(1, len(df_st_tr_tab_bar_qry_rslt) + 1)))

            # Transaction Analysis table query
            mycursor.execute(f"SELECT Transaction_type, Transaction_count, Transaction_amount FROM agg_trans WHERE State = '{st_trans}' AND Year = '{st_yr}' AND Quarter = '{st_qtr}';")
            st_tr_anly_tab_qry_rslt = mycursor.fetchall()
            df_st_tr_anly_tab_qry_rslt = pd.DataFrame(np.array(st_tr_anly_tab_qry_rslt),
                                                    columns=['Transaction_type', 'Transaction_count',
                                                            'Transaction_amount'])
            df_st_tr_anly_tab_qry_rslt1 = df_st_tr_anly_tab_qry_rslt.set_index(pd.Index(range(1, len(df_st_tr_anly_tab_qry_rslt) + 1)))

            # Total Transaction Amount table query
            mycursor.execute(f"SELECT SUM(Transaction_amount), AVG(Transaction_amount) FROM agg_trans WHERE State = '{st_trans}' AND Year = '{st_yr}' AND Quarter = '{st_qtr}';")
            st_tr_am_qry_rslt = mycursor.fetchall()
            df_st_tr_am_qry_rslt = pd.DataFrame(np.array(st_tr_am_qry_rslt), columns=['Total', 'Average'])
            df_st_tr_am_qry_rslt1 = df_st_tr_am_qry_rslt.set_index(['Average'])

            # Total Transaction Count table query
            mycursor.execute(f"SELECT SUM(Transaction_count), AVG(Transaction_count) FROM agg_trans WHERE State = '{st_trans}' AND Year ='{st_yr}' AND Quarter = '{st_qtr}';")
            st_tr_co_qry_rslt = mycursor.fetchall()
            df_st_tr_co_qry_rslt = pd.DataFrame(np.array(st_tr_co_qry_rslt), columns=['Total', 'Average'])
            df_st_tr_co_qry_rslt1 = df_st_tr_co_qry_rslt.set_index(['Average'])

            # -----       State wise Transaction Analysis Bar Chart     ------ #

            df_st_tr_tab_bar_qry_rslt1['Transaction_type'] = df_st_tr_tab_bar_qry_rslt1['Transaction_type'].astype(str)
            df_st_tr_tab_bar_qry_rslt1['Transaction_amount'] = df_st_tr_tab_bar_qry_rslt1['Transaction_amount'].astype(
                float)
            df_st_tr_tab_bar_qry_rslt1_fig = px.bar(df_st_tr_tab_bar_qry_rslt1, x='Transaction_type',
                                                    y='Transaction_amount', color='Transaction_amount',
                                                    color_continuous_scale='thermal',
                                                    title='Transaction Analysis Chart', height=500, )
            df_st_tr_tab_bar_qry_rslt1_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
            st.plotly_chart(df_st_tr_tab_bar_qry_rslt1_fig, use_container_width=True)

            # ------    State wise Total Transaction Calculation Table    ---- #
            st.header(':violet[Total calculation]')

            col4, col5 = st.columns(2)
            with col4:
                st.subheader(':violet[Transaction Analysis]')
                st.dataframe(df_st_tr_anly_tab_qry_rslt1)
            with col5:
                st.subheader(':violet[Transaction Amount]')
                st.dataframe(df_st_tr_am_qry_rslt1)
                st.subheader(':violet[Transaction Count]')
                st.dataframe(df_st_tr_co_qry_rslt1)
        # User Tab for State
        with tab4:
            col5, col6 = st.columns(2)
            with col5:
                st_us_st = st.selectbox('**Select State**', (
                    'andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh', 'assam', 'bihar',
                    'chandigarh', 'chhattisgarh', 'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat',
                    'haryana', 'himachal-pradesh',
                    'jammu-&-kashmir', 'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep', 'madhya-pradesh',
                    'maharashtra', 'manipur',
                    'meghalaya', 'mizoram', 'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan', 'sikkim',
                    'tamil-nadu', 'telangana',
                    'tripura', 'uttar-pradesh', 'uttarakhand', 'west-bengal'), key='st_us_st')
            with col6:
                st_us_yr = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='st_us_yr')
            # User Analysis Bar chart query
            mycursor.execute(
                f"SELECT Quarter, SUM(Count) FROM agg_user WHERE State = '{st_us_st}' AND Year = '{st_us_yr}' GROUP BY Quarter;")
            st_us_tab_qry_rslt = mycursor.fetchall()
            df_st_us_tab_qry_rslt = pd.DataFrame(np.array(st_us_tab_qry_rslt), columns=['Quarter', 'User Count'])
            df_st_us_tab_qry_rslt1 = df_st_us_tab_qry_rslt.set_index(pd.Index(range(1, len(df_st_us_tab_qry_rslt) + 1)))

            # Total User Count table query
            mycursor.execute(
                f"SELECT SUM(Count), AVG(Count) FROM agg_user WHERE State = '{st_us_st}' AND Year = '{st_us_yr}';")
            st_us_co_qry_rslt = mycursor.fetchall()
            df_st_us_co_qry_rslt = pd.DataFrame(np.array(st_us_co_qry_rslt), columns=['Total', 'Average'])
            df_st_us_co_qry_rslt1 = df_st_us_co_qry_rslt.set_index(['Average'])

            # -----     All India User Analysis Bar chart      ----- #
            df_st_us_tab_qry_rslt1['Quarter'] = df_st_us_tab_qry_rslt1['Quarter'].astype(int)
            df_st_us_tab_qry_rslt1['User Count'] = df_st_us_tab_qry_rslt1['User Count'].astype(int)
            df_st_us_tab_qry_rslt1_fig = px.bar(df_st_us_tab_qry_rslt1, x='Quarter', y='User Count', color='User Count',
                                                color_continuous_scale='thermal', title='User Analysis Chart',
                                                height=500, )
            df_st_us_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
            st.plotly_chart(df_st_us_tab_qry_rslt1_fig, use_container_width=True)

            # ------       State wise User Total User calculation Table      -----#
            st.header(':violet[Total calculation]')

            col3, col4 = st.columns(2)
            with col3:
                st.subheader(':violet[User Analysis]')
                st.dataframe(df_st_us_tab_qry_rslt1)
            with col4:
                st.subheader(':violet[User Count]')
                st.dataframe(df_st_us_co_qry_rslt1)

    if select == "TOP CATEGORIES":
        tab5, tab6 = st.tabs(["TRANSACTION", "USER"])
        #TRANSACTION TAB
        with tab5:
            top_tr_yr = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='top_tr_yr')
            #Top Transaction Analysis bar chart query
            mycursor.execute(
                f"SELECT State, SUM(Transaction_amount) As Transaction_amount FROM top_trans WHERE Year = '{top_tr_yr}' GROUP BY State ORDER BY Transaction_amount DESC LIMIT 10;")
            top_tr_tab_qry_rslt = mycursor.fetchall()
            df_top_tr_tab_qry_rslt = pd.DataFrame(np.array(top_tr_tab_qry_rslt),columns=['State', 'Top Transaction amount'])
            df_top_tr_tab_qry_rslt1 = df_top_tr_tab_qry_rslt.set_index(pd.Index(range(1, len(df_top_tr_tab_qry_rslt) + 1)))

            # Top Transaction Analysis table query
            mycursor.execute(
                f"SELECT State, SUM(Transaction_amount) as Transaction_amount, SUM(Transaction_count) as Transaction_count FROM top_trans WHERE Year = '{top_tr_yr}' GROUP BY State ORDER BY Transaction_amount DESC LIMIT 10;")
            top_tr_anly_tab_qry_rslt = mycursor.fetchall()
            df_top_tr_anly_tab_qry_rslt = pd.DataFrame(np.array(top_tr_anly_tab_qry_rslt),columns=['State', 'Top Transaction amount','Total Transaction count'])
            df_top_tr_anly_tab_qry_rslt1 = df_top_tr_anly_tab_qry_rslt.set_index(pd.Index(range(1, len(df_top_tr_anly_tab_qry_rslt) + 1)))

            # All India Transaction Analysis Bar chart
            df_top_tr_tab_qry_rslt1['State'] = df_top_tr_tab_qry_rslt1['State'].astype(str)
            df_top_tr_tab_qry_rslt1['Top Transaction amount'] = df_top_tr_tab_qry_rslt1[
                'Top Transaction amount'].astype(float)
            df_top_tr_tab_qry_rslt1_fig = px.bar(df_top_tr_tab_qry_rslt1, x='State', y='Top Transaction amount',
                                                color='Top Transaction amount', color_continuous_scale='thermal',
                                                title='Top Transaction Analysis Chart', height=600, )
            df_top_tr_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
            st.plotly_chart(df_top_tr_tab_qry_rslt1_fig, use_container_width=True)

            #All India Total Transaction calculation Table
            st.header(':violet[Total calculation]')
            st.subheader(':violet[Top Transaction Analysis]')
            st.dataframe(df_top_tr_anly_tab_qry_rslt1)
        # USER TAB
        with tab6:
            top_us_yr = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='top_us_yr')
            #Top User Analysis bar chart query
            mycursor.execute(f"SELECT State, SUM(Registered_users) AS Top_user FROM top_user WHERE Year='{top_us_yr}' GROUP BY State ORDER BY Top_user DESC LIMIT 10;")
            top_us_tab_qry_rslt = mycursor.fetchall()
            df_top_us_tab_qry_rslt = pd.DataFrame(np.array(top_us_tab_qry_rslt), columns=['State', 'Total User count'])
            df_top_us_tab_qry_rslt1 = df_top_us_tab_qry_rslt.set_index(pd.Index(range(1, len(df_top_us_tab_qry_rslt) + 1)))
            #All India User Analysis Bar chart
            df_top_us_tab_qry_rslt1['State'] = df_top_us_tab_qry_rslt1['State'].astype(str)
            df_top_us_tab_qry_rslt1['Total User count'] = df_top_us_tab_qry_rslt1['Total User count'].astype(float)
            df_top_us_tab_qry_rslt1_fig = px.bar(df_top_us_tab_qry_rslt1, x='State', y='Total User count',
                                                color='Total User count', color_continuous_scale='thermal',
                                                title='Top User Analysis Chart', height=600, )
            df_top_us_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
            st.plotly_chart(df_top_us_tab_qry_rslt1_fig, use_container_width=True)
            #All India Total Transaction calculation Table
            st.header(':violet[Total calculation]')
            st.subheader(':violet[Total User Analysis]')
            st.dataframe(df_top_us_tab_qry_rslt1)

def execute_query(query):
    mycursor=myconnection.cursor()
    mycursor.execute(query)
    results=mycursor.fetchall()
    columns=[col[0] for col in mycursor.description]
    df=pd.DataFrame(results,columns=columns)
    return df

def top_charts():
    st.title(':violet[TOP CHARTS]')
    options = ["--select--",
               "1. Top 10 Brands of Mobiles Used",
               "2. States with Lowest Transaction Amount",
               "3. Districts with Highest Transaction Amount",
               "4. Least 10 States and Districts based on Registered_users",
               "5. Top 10 States with AppOpens",
               "6. Least 10 Districts based on the Transaction Amount",
               "7. Top 10 Districts based on the Transaction count",
               "8. Top 10 States based on the Transaction count",
               "9. Top Transaction types based on the Transaction Amount",
               "10. Least 10 States with AppOpens"]
    select = st.selectbox(":violet[Select the option]", options)
    if select =="1. Top 10 Brands of Mobiles Used":
        query="select Brands, sum(Count)as Transaction_count from agg_user group by Brands order by Transaction_count desc limit 10;"
        df=execute_query(query)
        fig=px.pie(df,values='Transaction_count',names="Brands",title='Top 10 Mobile Brands by Transaction Count')
        st.plotly_chart(fig, use_container_width=True)
    if select=="2. States with Lowest Transaction Amount":
        query="select State,Year,sum(Transaction_amount) as Total_amount from agg_trans group by State, Year order by Total_amount asc limit 10;"
        df=execute_query(query)
        fig=px.bar(df,x="State",y="Total_amount",title="States With Lowest Transaction Amount",
                   color_discrete_sequence=px.colors.sequential.OrRd)
        st.plotly_chart(fig)
    if select=="3. Districts with Highest Transaction Amount":
        query="SELECT District, SUM(Amount) AS Total_Amount FROM map_trans GROUP BY District ORDER BY Total_Amount DESC LIMIT 10;"
        df=execute_query(query)
        fig=px.pie(df,values='Total_Amount',names="District",title="Top 10 Districts with Highest Transaction Amount")
        st.plotly_chart(fig)
    if select=="4. Least 10 States and Districts based on Registered_users":
        query="SELECT State, SUM(Registered_user) AS Total_Registered_users FROM map_user GROUP BY State ORDER BY Total_Registered_users ASC LIMIT 10;"
        df=execute_query(query)
        fig=px.bar(df,x="State",y="Total_Registered_users",title="Least 10 States based on Registered_users")
        st.plotly_chart(fig)
        query = "SELECT District, SUM(Registered_user) AS Total_Registered_users FROM map_user GROUP BY District ORDER BY Total_Registered_users ASC LIMIT 10;"
        df = execute_query(query)
        fig = px.bar(df, x="District", y="Total_Registered_users", title="Least 10 States based on Registered_users")
        st.plotly_chart(fig)
    if select=="5. Top 10 States with AppOpens":
        query="SELECT State, SUM(App_opens) AS Total_App_opens FROM map_user GROUP BY State ORDER BY Total_App_opens DESC LIMIT 10;"
        df=execute_query(query)
        fig=px.pie(df,values='Total_App_opens',names="State",title="Top 10 States with AppOpens ")
        st.plotly_chart(fig)
    if select=="6. Least 10 Districts based on the Transaction Amount":
        query="SELECT District, SUM(Amount) AS Total_Amount FROM map_trans GROUP BY District ORDER BY Total_Amount asc LIMIT 10;"
        df=execute_query(query)
        fig=px.bar(df,x="District",y="Total_Amount",title="Least 10 Districts based on Transaction Amounnt")
        st.plotly_chart(fig)
    if select=="7. Top 10 Districts based on the Transaction count":
        query="select District,sum(Count) as Transaction_count from map_trans group by District order by Transaction_count desc limit 10;"
        df=execute_query(query)
        fig=px.pie(df,values="Transaction_count",names="District",title="Top 10 Districts based on Transaction Count")
        st.plotly_chart(fig)
    if select=="8. Top 10 States based on the Transaction count":
        query="select State,sum(Count) as Transaction_count from map_trans group by State order by Transaction_count desc limit 10;"
        df=execute_query(query)
        fig=px.bar(df,x="State",y="Transaction_count",title="Top 10 States based on Transaction Count")
        st.plotly_chart(fig)
    if select=="9. Top Transaction types based on the Transaction Amount":
        query = "select Transaction_type,sum(Transaction_amount) as Total_amount from agg_trans group by Transaction_type order by Total_amount desc;"
        df = execute_query(query)
        fig = px.bar(df, x="Transaction_type", y="Total_amount", title="Top Transaction Types based on the Transaction Amount")
        st.plotly_chart(fig)
    if select=="10. Least 10 States with AppOpens":
        query = "SELECT State, SUM(App_opens) AS Total_App_opens FROM map_user GROUP BY State ORDER BY Total_App_opens asc LIMIT 10;"
        df = execute_query(query)
        fig = px.pie(df, values='Total_App_opens', names="State", title="Least 10 States with AppOpens ")
        st.plotly_chart(fig)


def about_page():
    st.title(":violet[About PhonePe Pulse]")
    st.write(
        """
        **PhonePe Pulse** is your window into the world of digital transactions! 📊💳

        **What is PhonePe Pulse?**
        
        PhonePe Pulse is an analytics platform provided by PhonePe, India's leading digital payments platform. It offers deep insights into transactional data processed through the PhonePe platform.

        **Why PhonePe Pulse?**
        
        PhonePe Pulse aims to provide businesses, analysts, and stakeholders with actionable insights to understand consumer behavior, trends, and patterns in digital transactions.

        **Features:**
        - **Transaction Analysis:** Dive into detailed transaction analysis, including volumes, amounts, and popular transaction types.
        - **Regional Insights:** Explore transaction data at the state and district levels, revealing regional trends and preferences.
        - **User Engagement Metrics:** Track user engagement metrics like app opens and registered users, helping businesses understand user behavior.
        - **Interactive Visualizations:** Visualize data through interactive charts and graphs for easier interpretation.

        **How to Use:**
        
        Simply select your desired option from the dropdown menu to explore different insights and charts available on PhonePe Pulse.
        """)

def main():
    # Creating option menu
    selected = option_menu(menu_title=None,
                           options=["Home", "Top Charts", "Explore Data", "About"],
                           icons=["house", "graph-up-arrow", "bar-chart-line", "exclamation-circle"],
                           # menu_icon="menu-button-wide",
                           default_index=0,
                           orientation="horizontal",
                           styles={"nav-link": {"font-size": "20px", "text-align": "left", "margin": "-2px",
                                                "--hover-color": "#6F36AD"},
                                   "nav-link-selected": {"background-color": "#6F36AD"}})
    if selected=="Home":
        home_page()
    elif selected=="Top Charts":
        top_charts()
    elif selected=="Explore Data":
        explore_data()
    elif selected=="About":
        about_page()


if __name__=="__main__":
    main()


