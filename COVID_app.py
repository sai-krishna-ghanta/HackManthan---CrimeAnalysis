import json
from datetime import date
from urllib.request import urlopen
import time
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import numpy as np
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
from pandas.io.json import json_normalize
import plotly.graph_objects as go
import plotly.express as px

_ENABLE_PROFILING = False

if _ENABLE_PROFILING:
    import cProfile, pstats, io
    from pstats import SortKey
    pr = cProfile.Profile()
    pr.enable()

today = date.today()

sc1 = pd.read_csv('data/crime/02_01_District_wise_crimes_committed_against_SC_2001_2012.csv')
sc13= pd.read_csv("data/crime/02_01_District_wise_crimes_committed_against_SC_2013.csv")
sc13 = sc13[['STATE/UT', 'DISTRICT', 'Year', 'Murder', 'Rape',
'Kidnapping and Abduction', 'Dacoity', 'Robbery', 'Arson', 'Hurt','Prevention of atrocities (POA) Act','Protection of Civil Rights (PCR) Act','Other Crimes Against SCs']]
frames = [sc1 , sc13]
sc = pd.concat(frames)
sc['STATE/UT'] = sc['STATE/UT'].str.capitalize()
sc['DISTRICT'] = sc['DISTRICT'].str.capitalize()
sc['STATE/UT'].unique()
sc['STATE/UT'].replace(to_replace='Delhi ut',value='Delhi',inplace=True)
sc['STATE/UT'].replace(to_replace='A&n islands',value='A & n islands',inplace=True)
sc['STATE/UT'].replace(to_replace='D&n haveli',value='D & n haveli',inplace=True)
sc['STATE/UT'].unique()
yearw = sc[sc.DISTRICT == 'Total']
yearw = yearw.groupby(['Year'])['Murder', 'Rape','Kidnapping and Abduction', 'Dacoity', 'Robbery', 'Arson', 'Hurt','Prevention of atrocities (POA) Act','Protection of Civil Rights (PCR) Act', 'Other Crimes Against SCs'].sum().reset_index()
yearw['sum'] = yearw.drop('Year', axis=1).sum(axis=1)
yearw = yearw[['Year','sum']]
scy = sc[sc.DISTRICT == 'Total']
scy = scy.groupby(['Year'])['Murder', 'Rape',
            'Kidnapping and Abduction', 'Dacoity', 'Robbery', 'Arson', 'Hurt',
            'Prevention of atrocities (POA) Act',
            'Protection of Civil Rights (PCR) Act', 'Other Crimes Against SCs'].sum().reset_index()

crimes = ['Murder', 'Rape',
            'Kidnapping and Abduction', 'Dacoity', 'Robbery', 'Arson', 'Hurt',
            'Prevention of atrocities (POA) Act',
            'Protection of Civil Rights (PCR) Act', 'Other Crimes Against SCs']

scy = scy.append(scy.sum().rename('total'))
scy['Year'].replace(26091, 'Total', inplace=True)
scy = scy[scy['Year'] == 'Total']
scy_t = scy.T.reset_index()

stateyr = sc[sc.DISTRICT == 'Total']
stateyr = stateyr.groupby(['Year','STATE/UT'])['Murder', 'Rape',
       'Kidnapping and Abduction', 'Dacoity', 'Robbery', 'Arson', 'Hurt',
       'Prevention of atrocities (POA) Act',
       'Protection of Civil Rights (PCR) Act', 'Other Crimes Against SCs'].sum().reset_index()
stateyr['sum'] =  stateyr.iloc[:, 2:].sum(axis=1)
stateyr2 = stateyr.groupby('STATE/UT')['sum'].sum().reset_index()
stateyr2 = stateyr2.sort_values('sum', ascending = False)



st.set_page_config(
    page_title="Crime Analysis",
    layout='wide',
    initial_sidebar_state='auto',
)

sidebar_selection = st.sidebar.radio(
    'Select data:',
    ['Indian Crime Analysis', 'Chattisgarh Crime Analysis', 'Our Analysis Report'],
)



t1, t2 = st.columns(2)
with t1:
    st.markdown('# Crime Data Analysis')

with t2:
    st.write("")
    st.write("")
    st.write("""
    **Sainath** | **Sai Krishna** | **Venu**
    """)

st.write("")


if sidebar_selection == 'Indian Crime Analysis':
    option = st.selectbox(
     'How would you like to be contacted?',
     ('Murders', 'Crime Against SC', 'Specific Purpose of kidnapping', 'Serious Fraud', 'Rape Victims', 'Auto-Theft', 'Crime Against Women'))
    if option == 'Murders':
        murder = pd.read_csv('data/32_Murder_victim_age_sex.csv')
        st.text("Murder is the top most category of crime in India. Currently India's homicide rate is 3.08 per 100,000 population. The objective of this notebook is to see the trend of murder victims over the years as well as murder victims per state. first lets see the data.")
        components.html('''<div class="flourish-embed flourish-bar-chart-race" data-src="visualisation/2693755" data-url="https://flo.uri.sh/visualisation/2693755/embed"><script src="https://public.flourish.studio/resources/embed.js"></script></div>''',height=600,)
        murdergs = murder.groupby(['Area_Name' , 'Sub_Group_Name'])['Victims_Total'].sum().sort_values(ascending = False).reset_index() #groupby state and gender
        murdergs = murdergs[murdergs['Sub_Group_Name']!= '3. Total']
        murdernt = murder[murder['Sub_Group_Name']== '3. Total']
        murdersa = murdernt.groupby(['Area_Name'])['Victims_Upto_10_15_Yrs','Victims_Above_50_Yrs', 'Victims_Upto_10_Yrs', 'Victims_Upto_15_18_Yrs','Victims_Upto_18_30_Yrs','Victims_Upto_30_50_Yrs'].apply(sum).reset_index()
        #murdersa.index = range(len(murdersa.index))
        murdersa = murdersa.melt('Area_Name', var_name='AgeGroup',  value_name='vals') #melting the dataset

        df=pd.read_csv("data/32_Murder_victim_age_sex.csv")
        df=df.groupby("Area_Name").sum().drop("Year",axis=1)

        df=pd.DataFrame(df.sum(axis=1))
        df = df.rename(columns={0:"Total_Murders" })
        df["States"]=df.index
        import json
        india_states = json.load(open("states_india.geojson", "r"))
        state_id_map = {}
        for feature in india_states["features"]:
            feature["id"] = feature["properties"]["state_code"]
            state_id_map[feature["properties"]["st_nm"]] = feature["id"]
        import plotly.io as pio
        pio.renderers.default = 'browser'
        id=[]
        if df["States"][0]=='Andaman & Nicobar Islands':
            id.append(35)
        if df["States"][1]=='Andhra Pradesh':
            id.append(28)
        if df["States"][2]=='Arunachal Pradesh':
            id.append(12)
        if df["States"][3]=='Assam':
            id.append(18)
        if df["States"][4]=='Bihar':
            id.append(10)
        if df["States"][5]=='Chandigarh':
            id.append(4)
        if df["States"][6]=='Chhattisgarh':
            id.append(22)
        if df["States"][7]=='Dadra & Nagar Haveli':
            id.append(26)
        if df["States"][8]=='Daman & Diu':
            id.append(25)
        if df["States"][9]=='Delhi':
            id.append(7)
        if df["States"][10]=='Goa':
            id.append(30)
        if df["States"][11]=='Gujarat':
            id.append(24)
        if df["States"][12]=='Haryana':
            id.append(6)
        if df["States"][13]=='Himachal Pradesh':
            id.append(2)
        if df["States"][14]=='Jammu & Kashmir':
            id.append(1)
        if df["States"][15]=='Jharkhand':
            id.append(20)
        if df["States"][16]=='Karnataka':
            id.append(29)
        if df["States"][17]=='Kerala':
            id.append(32)
        if df["States"][18]=='Lakshadweep':
            id.append(31)
        if df["States"][19]=='Madhya Pradesh':
            id.append(23)
        if df["States"][20]=='Maharashtra':
            id.append(27)
        if df["States"][21]=='Manipur':
            id.append(14)
        if df["States"][22]=='Meghalaya':
            id.append(17)
        if df["States"][23]=='Mizoram':
            id.append(15)
        if df["States"][24]=='Nagaland':
            id.append(13)
        if df["States"][25]=='Odisha':
            id.append(21)
        if df["States"][26]=='Puducherry':
            id.append(34)
        if df["States"][27]=='Punjab':
            id.append(3)
        if df["States"][28]=='Rajasthan':
            id.append(8)
        if df["States"][29]=='Sikkim':
            id.append(11)
        if df["States"][30]=='Tamil Nadu':
            id.append(33)
        if df["States"][31]=='Tripura':
            id.append(16)
        if df["States"][32]=='Uttar Pradesh':
            id.append(9)
        if df["States"][33]=='Uttarakhand':
            id.append(5)
        if df["States"][34]=='West Bengal':
            id.append(19)
        df["id"]=id
        fig = px.choropleth(
            df,
            locations="id",
            geojson=india_states,
            color="Total_Murders",
            hover_name="States",
            hover_data=["Total_Murders"],
            title="India Murder Rate",
        )
        fig.update_geos(fitbounds="locations",visible=False)
        st.write(fig)

        fig = px.choropleth_mapbox(
            df,
            locations="id",
            geojson=india_states,
            color="Total_Murders",
            hover_name="States",
            hover_data=["Total_Murders"],
            title="India Murder Rate",
            mapbox_style="carto-positron",
            center={"lat": 24, "lon": 78},
            zoom=3,
            opacity=0.5,
            )

        st.write(fig)
        
        

        plt.style.use("classic")
        f, axes = plt.subplots(3,2, figsize = (30,30))
        plt.figure(figsize = (14,15))
        sns.set_theme(style="whitegrid")
        sns.barplot(x = 'vals', y = 'Area_Name', data = murdersa[murdersa['AgeGroup']== 'Victims_Upto_10_Yrs'].sort_values(by=['vals'],ascending = False).head(10),ax = axes[0,0],palette= 'colorblind')
        axes[0,0].set_title(' Age 0 - 10', size = 20)
        axes[0,0].set_ylabel('')
        axes[0,0].set_xlabel('No.of Victims')

        sns.barplot(x = 'vals', y = 'Area_Name', data = murdersa[murdersa['AgeGroup']== 'Victims_Upto_10_15_Yrs'].sort_values(by=['vals'],ascending = False).head(10), ax = axes[0,1],palette=  'colorblind')
        axes[0,1].set_title(' Age 10 - 15', size = 20)
        axes[0,1].set_ylabel('')
        axes[0,1].set_xlabel('No.of Victims')    

        sns.barplot(x = 'vals', y = 'Area_Name', data = murdersa[murdersa['AgeGroup']== 'Victims_Upto_15_18_Yrs'].sort_values(by=['vals'],ascending = False).head(10),ax = axes[1,0],palette= 'colorblind')
        axes[1,0].set_title(' Age 15 - 18', size = 20)
        axes[1,0].set_ylabel('')
        axes[1,0].set_xlabel('No.of Victims')  

        sns.barplot(x = 'vals', y = 'Area_Name', data = murdersa[murdersa['AgeGroup']== 'Victims_Upto_18_30_Yrs'].sort_values(by=['vals'],ascending = False).head(10), ax = axes[1,1],palette=  'colorblind')
        axes[1,1].set_title(' Age 18 - 30', size = 20)
        axes[1,1].set_ylabel('')
        axes[1,1].set_xlabel('No.of Victims')  

        sns.barplot(x = 'vals', y = 'Area_Name', data = murdersa[murdersa['AgeGroup']== 'Victims_Upto_30_50_Yrs'].sort_values(by=['vals'],ascending = False).head(10), ax = axes[2,0],palette= 'colorblind')
        axes[2,0].set_title(' Age 30 - 50', size = 20)
        axes[2,0].set_ylabel('')
        axes[2,0].set_xlabel('No.of Victims')  

        sns.barplot(x = 'vals', y = 'Area_Name', data = murdersa[murdersa['AgeGroup']== 'Victims_Above_50_Yrs'].sort_values(by=['vals'],ascending = False).head(10),ax = axes[2,1],palette= 'colorblind')
        axes[2,1].set_title(' Age 50 +', size = 20)
        axes[2,1].set_ylabel('')
        axes[2,1].set_xlabel('No.of Victims')  
        plt.tight_layout()
        st.pyplot(f)
        st.text("Uttarpradesh has the highest number of murder victims in all age group except age group 0 - 10 , Surprisingly Maharashtra has the highest child victims and Gujrat ranks second in case of child victims. Assam is the only north eastern state which comes under these graphs.")
    
    elif option == 'Rape Victims':
        
        df_victim_of_rape = pd.read_csv("data/20_Victims_of_rape.csv")
        df_victim_of_rape = df_victim_of_rape[df_victim_of_rape.Victims_of_Rape_Total> 360]
        f = plt.figure(figsize=(30, 6))
        sns.barplot(x = df_victim_of_rape.Area_Name, y = df_victim_of_rape['Rape_Cases_Reported'], color = "red")
        upto_18 = sns.barplot(x = df_victim_of_rape.Area_Name, y = df_victim_of_rape['Victims_Between_14-18_Yrs'], color = "#a8ddb5")
        topbar = plt.Rectangle((0,0),1,1,fc="red", edgecolor = 'none')
        upto_18 = plt.Rectangle((0,0),1,1,fc='#a8ddb5',  edgecolor = 'none')
        l = plt.legend([upto_18, topbar], ['Victims between 14 to 18 years of Age', 'Total Rape Cases'], loc=1, ncol = 2, prop={'size':16})
        l.draw_frame(False)
        sns.despine(left=True)
        st.pyplot(f)
        
        f = plt.figure(figsize=(20, 6))
        sns.boxplot(df_victim_of_rape.Victims_Upto_10_Yrs, df_victim_of_rape.Area_Name,data = df_victim_of_rape);
        plt.title('Spread of Rapes performed on Children upto 10 Years!');
        st.pyplot(f)

        f = plt.figure(figsize=(30, 6))
        sns.barplot(x = df_victim_of_rape.Area_Name, y = df_victim_of_rape['Rape_Cases_Reported'], color = "red")
        upto_30 = sns.barplot(x = df_victim_of_rape.Area_Name, y = df_victim_of_rape['Victims_Between_18-30_Yrs'], color = "#fe9929")
        topbar = plt.Rectangle((0,0),1,1,fc="red", edgecolor = 'none')
        upto_30 = plt.Rectangle((0,0),1,1,fc='#fe9929',  edgecolor = 'none')
        l = plt.legend([upto_30, topbar], ['Victims between 18 to 30', 'Total Rape Cases'], loc=1, ncol = 2, prop={'size':16})
        l.draw_frame(False)
        sns.despine(left=True)
        st.pyplot(f)

        above_50 = df_victim_of_rape['Victims_Above_50_Yrs'].sum()
        ten_to_14 = df_victim_of_rape['Victims_Between_10-14_Yrs'].sum()
        fourteen_to_18 = df_victim_of_rape['Victims_Between_14-18_Yrs'].sum()
        eighteen_to_30 = df_victim_of_rape['Victims_Between_18-30_Yrs'].sum()
        thirty_to_50 = df_victim_of_rape['Victims_Between_30-50_Yrs'].sum()
        upto_10 = df_victim_of_rape['Victims_Upto_10_Yrs'].sum()
        

        age_grp = ['Upto 10','10 to 14','14 to 18','18 to 30','30 to 50','Above 50']

        age_group_vals = [upto_10,ten_to_14,fourteen_to_18,eighteen_to_30,thirty_to_50,above_50]

        fig1, ax1 = plt.subplots(figsize=(15,15))
    
        ax1.pie(age_group_vals,  labels=age_grp, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig1)
        
    elif option == 'Crime Against Women':
        crime12 = pd.read_csv('data/crime/42_District_wise_crimes_committed_against_women_2001_2012.csv')
        crime13 = pd.read_csv('data/crime/42_District_wise_crimes_committed_against_women_2013.csv')
        crime12.columns = crime12.columns.str.upper()
        crime13.columns = crime13.columns.str.upper()
        crime13['STATE/UT'] = crime13['STATE/UT'].str.upper()
        crime13['DISTRICT'].replace('ZZ TOTAL', 'TOTAL', inplace = True)
        dataframe = pd.concat([crime12, crime13])
        total_crime = dataframe[dataframe['DISTRICT'] == 'TOTAL']
        punjab_crime = total_crime[total_crime['STATE/UT'] == 'PUNJAB']

        f = plt.figure(figsize=(15, 6))
        punjab_crime.set_index('YEAR')[['DOWRY DEATHS', 'CRUELTY BY HUSBAND OR HIS RELATIVES','ASSAULT ON WOMEN WITH INTENT TO OUTRAGE HER MODESTY']].plot(kind = 'line', figsize = (12,8))
        plt.xlabel('Years')
        plt.ylabel('No. of Cases in Punjab')
        plt.title('Domestic Violence against Women')
        st.write(f)
        
        f = plt.figure(figsize=(15, 6))
        data24 = dataframe[(dataframe['DISTRICT'] == 'TOTAL') & (dataframe['YEAR'] == 2013)]
        data24[['RAPE', 'KIDNAPPING AND ABDUCTION','INSULT TO MODESTY OF WOMEN']].plot(kind = 'barh', figsize = (10,13), width = 1)
        plt.xlabel('No. of Cases in 2013')
        plt.ylabel('State')
        st.pyplot(f)

        delhi_crime = dataframe[dataframe['STATE/UT'] == 'DELHI']
        delhi_crime_tot = delhi_crime.groupby('YEAR').sum()
        graph_compare = plt.figure(figsize= (12,8))
        punjab_graph = graph_compare.add_subplot(211)
        delhi_graph = graph_compare.add_subplot(212)
        graph_compare.subplots_adjust(hspace = 0.3)

        f = plt.figure(figsize=(15, 6))
        d = delhi_crime_tot[['RAPE', 'KIDNAPPING AND ABDUCTION']]
        delhi_graph.set_xlabel('Years')
        delhi_graph.set_ylabel('No. of Cases')
        delhi_graph.set_title('Rapes and Kidnaps during past Years in Delhi')
        delhi_graph.plot(d)
        delhi_graph.legend(['Rape', 'Kidnap'])
        st.pyplot(f)

        f = plt.figure(figsize=(15, 6))
        p = punjab_crime.set_index('YEAR')[['RAPE', 'KIDNAPPING AND ABDUCTION']]
        punjab_graph.set_xlabel('Years')
        punjab_graph.set_ylabel('No. of Cases')
        punjab_graph.set_title('Rapes and Kidnaps during past Years in Punjab')
        punjab_graph.plot(p)
        punjab_graph.legend(['Rape', 'Kidnap'])
        st.pyplot(f)

        crimes = dataframe.groupby('STATE/UT').sum()
        crimes.drop('YEAR', axis= 1, inplace= True)
        crimes['TOTAL'] = 0
        for i in range(len(crimes.index)):
            crimes['TOTAL'][i] = crimes.iloc[i].sum()

        f = plt.figure(figsize=(15, 6))
        crimes['TOTAL'].nlargest(10).plot(kind = 'barh', title = 'Most Unsafe States for Women(2001-13)', figsize = (6,5))
        plt.xlabel('No. of Crimes')
        crimes['TOTAL'].nsmallest(10).plot(kind = 'barh', title = 'Safest States for Women(2001-13)', figsize = (6,5))
        plt.xlabel('No. of Crimes')
        st.pyplot(f)

    elif option == "Auto-Theft":
        auto_theft = pd.read_csv('data/30_Auto_theft.csv')
        g5 = pd.DataFrame(auto_theft.groupby(['Area_Name'])['Auto_Theft_Stolen'].sum().reset_index())
        g5.columns = ['State/UT','Vehicle_Stolen']
        g5.replace(to_replace='Arunachal Pradesh',value='Arunanchal Pradesh',inplace=True)
        auto_theft_traced = auto_theft['Auto_Theft_Coordinated/Traced'].sum()
        auto_theft_recovered = auto_theft['Auto_Theft_Recovered'].sum()
        auto_theft_stolen = auto_theft['Auto_Theft_Stolen'].sum()

        vehicle_group = ['Vehicles Stolen','Vehicles Traced','Vehicles Recovered']
        vehicle_vals = [auto_theft_stolen,auto_theft_traced,auto_theft_recovered]
        colors = ['hotpink','purple','red']
        fig1, ax1 = plt.subplots(figsize=(15,15))
    
        ax1.pie(vehicle_vals,  labels=vehicle_group, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig1)

        g5 = pd.DataFrame(auto_theft.groupby(['Year'])['Auto_Theft_Stolen'].sum().reset_index())
        g5.columns = ['Year','Vehicles Stolen']
        fig = px.bar(g5,x='Year',y='Vehicles Stolen',color_discrete_sequence=['#00CC96'])
        st.write(fig)
        
        motor_c = auto_theft[auto_theft['Sub_Group_Name']=='1. Motor Cycles/ Scooters']
        g8 = pd.DataFrame(motor_c.groupby(['Area_Name'])['Auto_Theft_Stolen'].sum().reset_index())
        g8_sorted = g8.sort_values(['Auto_Theft_Stolen'],ascending=True)
        fig = px.scatter(g8_sorted.iloc[-10:,:], y='Area_Name', x='Auto_Theft_Stolen',
                    orientation='h',color_discrete_sequence=["red"])
        st.write(fig)

    elif option == 'Crime Against SC':
        fig = go.Figure()
        fig.add_trace(go.Scatter(x= scy['Year'], y= scy['Murder'],
                            name='Murder',line=dict(color='pink', width=4)))
        fig.add_trace(go.Scatter(x= scy['Year'], y= scy['Rape'],
                            name='Rape',line=dict(color='green', width=4)))
        fig.add_trace(go.Scatter(x= scy['Year'], y= scy['Kidnapping and Abduction'],
                            name='Kidnapping and Abduction',line=dict(color='orange', width=4)))
        fig.add_trace(go.Scatter(x= scy['Year'], y= scy['Dacoity'],
                            name='Dacoity',line=dict(color='yellow', width=4)))
        fig.add_trace(go.Scatter(x= scy['Year'], y= scy['Robbery'],
                            name='Robbery',line=dict(color='black', width=4)))
        fig.add_trace(go.Scatter(x= scy['Year'], y= scy['Arson'],
                            name='Arson',line=dict(color='skyblue', width=4)))
        fig.add_trace(go.Scatter(x= scy['Year'], y= scy['Hurt'],
                            name='Hurt',line=dict(color='royalblue', width=4)))
        fig.add_trace(go.Scatter(x= scy['Year'], y= scy['Prevention of atrocities (POA) Act'],
                            name='Atrocities',line=dict(color='firebrick', width=4)))
        fig.add_trace(go.Scatter(x= scy['Year'], y= scy['Protection of Civil Rights (PCR) Act'],
                            mode='lines+markers',
                            name='Civil Rights Violations'))
        fig.add_trace(go.Scatter(x= scy['Year'], y= scy['Other Crimes Against SCs'],
                            name='Other Crimes',line=dict(color='red', width=4)))

        fig.update_layout(uniformtext_minsize= 20,
            title_text="Total Crimes Against Scs 2001-2013",)
        st.write(fig)

        scy2 = sc[sc.DISTRICT == 'Total']
        scy2 = scy2.groupby(['Year'])['Murder', 'Rape',
            'Kidnapping and Abduction', 'Dacoity', 'Robbery', 'Arson', 'Hurt',
            'Prevention of atrocities (POA) Act',
            'Protection of Civil Rights (PCR) Act', 'Other Crimes Against SCs'].sum().reset_index()

        #Plotting Graphs
        import itertools
        sns.set_context("talk")
        plt.style.use("fivethirtyeight")
        palette = itertools.cycle(sns.color_palette("dark"))
        columns = ['Murder', 'Rape',
            'Kidnapping and Abduction', 'Dacoity', 'Robbery', 'Arson', 'Hurt',
            'Prevention of atrocities (POA) Act',
            'Protection of Civil Rights (PCR) Act', 'Other Crimes Against SCs']
        fig = plt.figure(figsize=(20,30))
        plt.style.use('fivethirtyeight')
        for i,column in enumerate(columns):
            plt.subplot(5,2,i+1)
            ax= sns.barplot(data= scy2,x='Year',y= column ,color=next(palette) )
            plt.xlabel('')
            plt.ylabel('')
            plt.title(column,size = 20)
            for p in ax.patches:
                    ax.annotate("%.f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', fontsize=15, color='black', xytext=(0, 8),
                        textcoords='offset points')
            
        st.pyplot(fig)
        st.text("yes")

        labels = ['Murder', 'Rape','Kidnapping', 'Dacoity', 'Robbery', 'Arson', 'Hurt','Atrocities  Act',
         'Civil Rights Act', 'Other Crimes']
        values = [8576, 17991, 5305, 440,1015,2906, 54055 , 138533, 4332,176488]

        fig = go.Figure(data=[go.Pie(labels=labels, values=values ,textinfo='label+percent',
                                    )])
        fig.update_layout(
            uniformtext_minsize= 20,
            title_text="Distribution of Crimes Against Scs 2001-2013",
            paper_bgcolor='rgb(233,233,233)',
            autosize=False,
            width=700,
            height=700)
        st.write(fig)
        fig = plt.figure(figsize = (12,12))
        sns.set_context("talk")
        plt.style.use("fivethirtyeight")
        ax = sns.barplot(x = 'sum', y = 'STATE/UT', data = stateyr2, palette = 'bright', edgecolor = 'black')
        plt.title('Total crimes against SCs (2001- 2013)')
        for p in ax.patches:
                ax.annotate("%.f" % p.get_width(), xy=(p.get_width(), p.get_y()+p.get_height()/2),
                    xytext=(5, 0), textcoords='offset points', ha="left", va="center")

        st.write(fig)

        states = ['Uttar pradesh','Rajasthan' ,'Madhya pradesh' , 'Andhra pradesh', 'Bihar', 'Karnataka' , 'Odisha' , 'Tamil nadu','Gujarat', 'Maharashtra']
        sns.set_context("talk")
        plt.style.use("fivethirtyeight")
        fig = plt.figure(figsize = (23,28))

        for i, s in enumerate(states):
            plt.subplot(5,2,i+1)
            stateyr3 = stateyr[stateyr['STATE/UT'] == s]
            ax = sns.barplot(x = 'Year' , y = 'sum' , data = stateyr3,ci=None , palette = 'colorblind' , edgecolor = 'blue')
            plt.title(s , size = 25)
            for p in ax.patches:
                    ax.annotate("%.f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', fontsize=15, color='black', xytext=(0, 8),
                        textcoords='offset points')
        plt.tight_layout()
        plt.subplots_adjust(hspace= .3)
        st.write(fig)

        scs = sc[sc.DISTRICT == 'Total']
        scs = scs.groupby(['STATE/UT'])['Murder', 'Rape',
            'Kidnapping and Abduction', 'Dacoity', 'Robbery', 'Arson', 'Hurt',
            'Prevention of atrocities (POA) Act',
            'Protection of Civil Rights (PCR) Act', 'Other Crimes Against SCs'].sum().reset_index()

        scs1 = scs[(scs.Murder > 100) & (scs.Rape > 100)]
        sns.set_context("talk")

        fig = plt.figure(figsize=(20,30))
        plt.style.use('fivethirtyeight')

        for i,column in enumerate(columns):
            scs1 = scs1.sort_values(column,ascending = False)
            plt.subplot(5,2,i+1)
            ax = sns.barplot(data= scs1,x= column ,y='STATE/UT',palette = 'dark' )
            plt.xlabel('')
            plt.ylabel('')
            plt.title(column,size = 20)
            for p in ax.patches:
                ax.annotate("%.f" % p.get_width(), xy=(p.get_width(), p.get_y()+p.get_height()/2),
                    xytext=(5, 0), textcoords='offset points', ha="left", va="center")
        st.write(fig)

        new_row = scs.iloc[[1]]
        scs = scs.append(new_row, ignore_index = True)
        scs.at[35, 'STATE/UT']= 'Telangana'
        scs.at[9,'STATE/UT'] = 'Nct of Delhi'


        scd = sc[sc.DISTRICT != 'Total']
        scd = scd.groupby(['DISTRICT'])['Murder', 'Rape',
            'Kidnapping and Abduction', 'Dacoity', 'Robbery', 'Arson', 'Hurt',
            'Prevention of atrocities (POA) Act',
            'Protection of Civil Rights (PCR) Act', 'Other Crimes Against SCs'].sum().reset_index()


        sns.set_context("talk")

        fig = plt.figure(figsize=(20,30))
        plt.style.use('fivethirtyeight')

        for i,column in enumerate(columns):
            scd1 = scd.sort_values(column,ascending = False)
            scd1 = scd1.head(10)
            plt.subplot(5,2,i+1)
            ax= sns.barplot(data= scd1,x= column ,y='DISTRICT' )
            plt.xlabel('')
            plt.ylabel('')
            plt.title(column,size = 20)
            for p in ax.patches:
                ax.annotate("%.f" % p.get_width(), xy=(p.get_width(), p.get_y()+p.get_height()/2),
                    xytext=(5, 0), textcoords='offset points', ha="left", va="center")
                
        st.write(fig)
        scd['sum'] = scd['Murder']+scd['Rape']+scd['Kidnapping and Abduction']+scd['Dacoity']+scd['Robbery']+scd['Arson']+scd['Hurt']+scd['Prevention of atrocities (POA) Act']+scd['Protection of Civil Rights (PCR) Act']+scd['Other Crimes Against SCs']
        mostviolent = scd.groupby(['DISTRICT'])['sum'].sum().sort_values(ascending = False).reset_index()
        fig = go.Figure(data=[go.Bar(
                    x= mostviolent['DISTRICT'], y= mostviolent['sum'],
                    text= mostviolent['sum'],
                    textposition='auto',marker_color='rgb(255, 22, 22)'
                )])
        st.write(fig)
        

elif sidebar_selection == 'Chattisgarh Crime Analysis':
    st.markdown("## Chattisgarh:")
    st.image("6d820bb7825c2ab33ad28d74896471e9.png")
    st.image("raipur.jpeg")
    df=pd.read_csv('data/crime/01_District_wise_crimes_committed_IPC_2001_2012.csv')
    df=df[df['STATE/UT']=='CHHATTISGARH']
    df=df.groupby("DISTRICT").sum()
    df["district"]=df.index

    

    sns.set_style("dark")
    sns.set_context("talk")
    plt.style.use("fivethirtyeight")


    f, axes = plt.subplots(3,2, figsize = (30,30))
    plt.figure(figsize = (14,15))
    sns.barplot(y = 'district', x = 'DACOITY', data = df.sort_values(by=['DACOITY'],ascending = False).head(10),ax = axes[0,0],palette= 'dark')
    axes[0,0].set_title('DACOITY', size = 20)
    axes[0,0].set_ylabel('')
    axes[0,0].set_xlabel('No.of Victims')

    sns.barplot(x = 'PREPARATION AND ASSEMBLY FOR DACOITY', y = 'district', data = df.sort_values(by=["PREPARATION AND ASSEMBLY FOR DACOITY"],ascending = False).head(10), ax = axes[0,1],palette= 'bright' )
    axes[0,1].set_title('PREPARATION AND ASSEMBLY FOR DACOITY', size = 20)
    axes[0,1].set_ylabel('')
    axes[0,1].set_xlabel('No.of Victims')    


    sns.barplot(x = 'RIOTS', y = 'district', data = df.sort_values(by=['RIOTS'],ascending = False).head(10),ax = axes[1,0],palette= 'dark')
    axes[1,0].set_title('RIOTS', size = 20)
    axes[1,0].set_ylabel('')
    axes[1,0].set_xlabel('No.of Victims')  

    sns.barplot(x = 'ASSAULT ON WOMEN WITH INTENT TO OUTRAGE HER MODESTY', y = 'district', data = df.sort_values(by=['ASSAULT ON WOMEN WITH INTENT TO OUTRAGE HER MODESTY'],ascending = False).head(10), ax = axes[1,1],palette= 'bright' )
    axes[1,1].set_title('ASSAULT ON WOMEN WITH INTENT TO OUTRAGE HER MODESTY', size = 20)
    axes[1,1].set_ylabel('')
    axes[1,1].set_xlabel('No.of Victims')  

    sns.barplot(x = 'BURGLARY', y = 'district', data = df.sort_values(by=['BURGLARY'],ascending = False).head(10), ax = axes[2,0],palette= 'dark')
    axes[2,0].set_title('BURGLARY', size = 20)
    axes[2,0].set_ylabel('')
    axes[2,0].set_xlabel('No.of Victims')  

    sns.barplot(x = 'ARSON', y = 'district', data =df.sort_values(by=['ARSON'],ascending = False).head(10),ax = axes[2,1],palette= 'bright')
    axes[2,1].set_title('ARSON', size = 20)
    axes[2,1].set_ylabel('')
    axes[2,1].set_xlabel('No.of Victims')  
    plt.tight_layout()
    st.write(f)


    sns.set_style("dark")
    sns.set_context("talk")
    plt.style.use("fivethirtyeight")


    f, axes = plt.subplots(3,2, figsize = (30,30))
    plt.figure(figsize = (14,15))
    sns.barplot(x = 'MURDER', y = 'district', data = df.sort_values(by=['MURDER'],ascending = False).head(10),ax = axes[0,0],palette= 'dark')
    axes[0,0].set_title('MURDER', size = 20)
    axes[0,0].set_ylabel('')
    axes[0,0].set_xlabel('No.of Victims')

    sns.barplot(x = 'ATTEMPT TO MURDER', y = 'district', data = df.sort_values(by=['ATTEMPT TO MURDER'],ascending = False).head(10), ax = axes[0,1],palette= 'bright' )
    axes[0,1].set_title('ATTEMPT TO MURDER', size = 20)
    axes[0,1].set_ylabel('')
    axes[0,1].set_xlabel('No.of Victims')    


    sns.barplot(x = 'CRUELTY BY HUSBAND OR HIS RELATIVES', y = 'district', data = df.sort_values(by=['CRUELTY BY HUSBAND OR HIS RELATIVES'],ascending = False).head(10),ax = axes[1,0],palette= 'dark')
    axes[1,0].set_title('CRUELTY BY HUSBAND OR HIS RELATIVES', size = 20)
    axes[1,0].set_ylabel('')
    axes[1,0].set_xlabel('No.of Victims')  

    sns.barplot(x = 'INSULT TO MODESTY OF WOMEN', y = 'district', data = df.sort_values(by=['INSULT TO MODESTY OF WOMEN'],ascending = False).head(10), ax = axes[1,1],palette= 'bright' )
    axes[1,1].set_title('INSULT TO MODESTY OF WOMEN', size = 20)
    axes[1,1].set_ylabel('')
    axes[1,1].set_xlabel('No.of Victims')  

    sns.barplot(x = 'DOWRY DEATHS', y = 'district', data = df.sort_values(by=['DOWRY DEATHS'],ascending = False).head(10), ax = axes[2,0],palette= 'dark')
    axes[2,0].set_title('DOWRY DEATHS', size = 20)
    axes[2,0].set_ylabel('')
    axes[2,0].set_xlabel('No.of Victims')  

    sns.barplot(x = 'IMPORTATION OF GIRLS FROM FOREIGN COUNTRIES', y = 'district', data =df.sort_values(by=['IMPORTATION OF GIRLS FROM FOREIGN COUNTRIES'],ascending = False).head(10),ax = axes[2,1],palette= 'bright')
    axes[2,1].set_title('IMPORTATION OF GIRLS FROM FOREIGN COUNTRIES', size = 20)
    axes[2,1].set_ylabel('')
    axes[2,1].set_xlabel('No.of Victims')  
    plt.tight_layout()
    #plt.subplots_adjust(hspace= .0001)
    st.write(f)




if sidebar_selection == 'Our Analysis Report':
    st.markdown("Since the British Raj, crime in India has been recorded, with complete data currently collected yearly by the National Crime Records Bureau (NCRB), which is part of the Ministry of Home Affairs (MHA). As of **2018**, a total of **50,74,634** cognizable offences were registered across the country, including **31,32,954** Indian Penal Code (IPC) offences and **19,41,680** Special & Local Laws (SLL) crimes. Despite a **1.3% ** yearly rise in case registration (**50,07,044** cases), the crime rate per 100,000 people has decreased somewhat from **388.6** in 2017 to **383.5** in 2018. This Report contains numerous data and infographics concerning various sorts of crimes that have occurred in India during the last **18** years (2001-2018)")

    st.markdown("  **Rape** is the **fourth** most common crime against women in India. Laws against rape come under the **Indian Penal Code 376**. Incest rape cases are registered under the condition where the offender is known to the victim. ")
    victims = pd.read_csv("data/20_Victims_of_rape.csv")
    police_hr = pd.read_csv('data/35_Human_rights_violation_by_police.csv')
    auto_theft = pd.read_csv('data/30_Auto_theft.csv')
    prop_theft = pd.read_csv('data/10_Property_stolen_and_recovered.csv')
    
    inc_victims = victims[victims['Subgroup']=='Victims of Incest Rape']

    g = pd.DataFrame(inc_victims.groupby(['Year'])['Rape_Cases_Reported'].sum().reset_index())
    g.columns = ['Year','Cases Reported']

    fig = px.bar(g,x='Year',y='Cases Reported',color_discrete_sequence=['blue'])
    st.write(fig)

    st.markdown("In 2005, around 750 cases were reported which is the highest number of that decade.The year 2010 recorded the lowest number of cases i.e 288.")
    st.markdown("Top 3 states having highest number of cases - Madhya Pradhesh, Chhatisgarh, RajasthanTop 3 states having lowest number of cases - Tripura, Manipur, Goa")
    above_50 = inc_victims['Victims_Above_50_Yrs'].sum()
    ten_to_14 = inc_victims['Victims_Between_10-14_Yrs'].sum()
    fourteen_to_18 = inc_victims['Victims_Between_14-18_Yrs'].sum()
    eighteen_to_30 = inc_victims['Victims_Between_18-30_Yrs'].sum()
    thirty_to_50 = inc_victims['Victims_Between_30-50_Yrs'].sum()
    upto_10 = inc_victims['Victims_Upto_10_Yrs'].sum()

    age_grp = ['Upto 10','10 to 14','14 to 18','18 to 30','30 to 50','Above 50']
    age_group_vals = [upto_10,ten_to_14,fourteen_to_18,eighteen_to_30,thirty_to_50,above_50]

    fig = go.Figure(data=[go.Pie(labels=age_grp, values=age_group_vals,sort=False,
                                marker=dict(colors=px.colors.qualitative.G10),textfont_size=12)])
    st.write(fig)

    st.markdown("Women between the age group of 18-30 have been most affected. Women between the age group above 50 have been least affected")
    
    st.markdown("Human Rights violation by the Police **Human Rights** in India is an issue complicated by the country's large size and population, widespread poverty, lack of proper education, as well as its diverse culture, despite its status as the world's largest sovereign, secular, democratic republic.")
    
    g3 = pd.DataFrame(police_hr.groupby(['Year'])['Cases_Registered_under_Human_Rights_Violations'].sum().reset_index())
    g3.columns = ['Year','Cases Registered']

    fig = px.bar(g3,x='Year',y='Cases Registered',color_discrete_sequence=['green'])
    st.write(fig)

    st.markdown("- In **2008**, highest number of cases were recorded - **506**.  The year **2006** recorded **least** number of cases i.e **58**")


    st.markdown("Cases have been registered under the following heads: 1) Torture 2) Extortion 3) Disappearance of Persons 4) Atrocities on SC/ST 5) Illegal detention/arrests 6) Indignity to Women 7) Fake encounter killings 8) False implication 9) Violation against terrorists/extremists 10) Failure in taking action 11) Other violations ")
    g4 = pd.DataFrame(police_hr.groupby(['Year'])['Policemen_Chargesheeted','Policemen_Convicted'].sum().reset_index())

    year=['2001','2002','2003','2004','2005','2006','2007','2008','2009','2010']

    fig = go.Figure(data=[
        go.Bar(name='Policemen Chargesheeted', x=year, y=g4['Policemen_Chargesheeted'],
            marker_color='purple'),
        go.Bar(name='Policemen Convicted', x=year, y=g4['Policemen_Convicted'],
            marker_color='red')
    ])

    fig.update_layout(barmode='group',xaxis_title='Year',yaxis_title='Number of policemen')
    st.write(fig)
    st.markdown("- In 2009, **69.87%** of policemen have been convicted - highest of the decade. - For about **three** consecutive years, **2005, 2006, 2007** there has been **no** conviction of policemen.")
        
with st.sidebar.expander("Click to learn more about this project"):
    st.markdown(f"""
    One of the key metrics for which data are widely available is the estimate of **daily new cases per 100,000
    population**.

    Here, in following graphics, we will track:

    (A) Estimates of daily new cases per 100,000 population (averaged over the last seven days)  
    
    (B) Daily incidence (new cases)  
    
    (C) Cumulative cases and deaths  
    
    (D) Daily new tests*  

    Data source: Data for cases are procured automatically from **COVID-19 Data Repository by the Center for Systems Science and Engineering (CSSE) at Johns Hopkins University**.  
    
    The data is updated at least once a day or sometimes twice a day in the [COVID-19 Data Repository](https://github.com/CSSEGISandData/COVID-19).  

    Infection rate, positive test rate, ICU headroom and contacts traced from https://covidactnow.org/.  

    *Calculation of % positive tests depends on consistent reporting of county-wise total number of tests performed routinely. Rolling averages and proportions are not calculated if reporting is inconsistent over a period of 14 days.  

    *Report updated on {str(today)}.*  
    """)

if _ENABLE_PROFILING:
    pr.disable()
    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    ts = int(time.time())
    with open(f"perf_{ts}.txt", "w") as f:
        f.write(s.getvalue())
