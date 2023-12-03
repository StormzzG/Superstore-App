import streamlit as st
import plotly.express as px
import pandas as pd
import pickle
import streamlit_authenticator as stauth


st.set_page_config(page_title="Superstore-StormzzG", page_icon=":bar_chart:",layout="wide")

names = ['Stormy Ndonga', 'Anonymous User']
usernames = ['Storm', 'User']

with open('hashed.pkl','rb') as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names,usernames,hashed_passwords,'sales_dash', 'abcde', cookie_expiry_days=1)

name,authentication_status,username = authenticator.login('Login', 'main')
if authentication_status == False:
    st.error('Username/Password is incorrect')
if authentication_status == None:
    st.warning('Please input Username and Password')
if authentication_status:
    st.title(":bar_chart: Sample Superstore EDA")
    st.markdown('<style>div.block-container{padding-top:2rem;}<style>',unsafe_allow_html=True)
    
    fl = st.file_uploader(":File Folder: Upload a File",type=(["csv","txt","xlsx","xls"]))
    if fl is not None:
        filename = fl.name
        st.write(filename)
        df = pd.read_csv(filename, encoding='Latin-1')
    else:
        df = pd.read_csv('SampleSuperstore.csv', encoding='Latin-1')
    st.warning('All this Data is affected by what you pick in the Sidebar Multiselect')
    #Creating 2 columns
    col1, col2 = st.columns((2))
    df['Order Date'] = pd.to_datetime(df['Order Date'])

    #Creating Start and End Date
    startDate = df['Order Date'].min()
    endDate = df['Order Date'].max()

    #Filling each column with their specific dates
    with col1:
        date1 = pd.to_datetime(st.date_input("Start Date", startDate))
    with col2:
        date2 = pd.to_datetime(st.date_input("End Date", endDate))

    #Updating the dataframe dates with the selected dates
    df = df[(df['Order Date'] >= date1) & (df['Order Date'] <= date2)].copy()

    #Creating a Sidebar
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.title(f"Welcome {username}")
    st.sidebar.header("Choose your Filter: ")
    #Create for Region
    region = st.sidebar.multiselect("Pick Your Region", df['Region'].unique())
    if not region:
        df2 = df.copy()
    else:
        df2 = df[df['Region'].isin(region)]
    #create for State
    state = st.sidebar.multiselect('Pick Your State', df2['State'].unique())
    if not state:
        df3 = df2.copy()
    else:
        df3 = df2[df2['State'].isin(state)]
    #Create for City
    city = st.sidebar.multiselect('Pick Your City', df3['City'].unique())

    if not region and not state and not city:
        filtered_df = df
    elif not state and not city:
        filtered_df = df[df['Region'].isin(region)]
    elif not region and not state:
        filtered_df = df[df['City'].isin(city)]
    elif not region and not city:
        filtered_df = df[df['State'].isin(state)]
    elif state and city:
        filtered_df = df3[(df3['State'].isin(state)) & (df3['City'].isin(city))]
    elif region and city:
        filtered_df = df2[(df2['Region'].isin(region)) & (df2['City'].isin(city))]
    elif region and state:
        filtered_df = df3[(df3['Region'].isin(region)) & (df3['State'].isin(state))]
    elif city:
        filtered_df = df3[df3['City'].isin(city)]
    else:
        filtered_df = df3[(df3['Region'].isin(region)) & (df3['State'].isin(state)) & (df3['City'].isin(city))]

    category_df = filtered_df.groupby(by = ['Category'], as_index = False)['Sales'].sum()

    with col1:
        st.subheader('Category Wise Sales')
        fig = px.bar(category_df, x='Category', y='Sales', text=['${:,.2f}'.format(x) for x in category_df['Sales']],
                    template='seaborn')
        st.plotly_chart(fig, use_container_width=True, height=200)

    with col2:
        st.subheader('Region Wise Sales')
        fig = px.pie(filtered_df, values='Sales', names='Region', hole=0.5)
        fig.update_traces(text = filtered_df['Region'], textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    cl1, cl2 = st.columns(2)
    with cl1:
        with st.expander('Category View Data'):
            st.write(category_df.style.background_gradient(cmap='Blues'))
            csv = category_df.to_csv(index = False).encode('utf-8')
            st.download_button('Download Data', data = csv, file_name = 'Category CSV', mime='text/csv',
                            help='Click here to download the csv file')
    with cl2:
        with st.expander('Region View Data'):
            region = filtered_df.groupby(by = ['Region'], as_index=False)['Sales'].sum()
            st.write(region.style.background_gradient(cmap='Blues'))
            csv = region.to_csv(index = False).encode('utf-8')
            st.download_button('Download Data', data = csv, file_name = 'Region CSV', mime='text/csv',
                            help='Click here to download the csv file')
            
    filtered_df['month_year'] = filtered_df['Order Date'].dt.to_period('M')
    st.subheader('Time Series Analysis')

    linechart = pd.DataFrame(filtered_df.groupby(filtered_df['month_year'].dt.strftime('%Y : %b'))['Sales'].sum()).reset_index()
    fig2 = px.line(linechart, x='month_year', y='Sales', labels={'Sales': 'Amount'}, height=500, width=1000,template='gridon')
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander('View Data of TimeSeries'):
        st.write(linechart.T.style.background_gradient(cmap='Blues'))
        csv = linechart.to_csv(index=False).encode('utf-8')
        st.download_button('Download Data', data=csv, file_name='TimeSeries CSV', mime='text/csv', help='Click here to download the file' )

    #Create a tree map based on Region, Category and Sub Category
    st.subheader('Hierarchial view of sales using tree map')
    fig3 = px.treemap(filtered_df, path=['Region','Category','Sub-Category'], values='Sales', hover_data=['Sales'], color='Sub-Category')
    fig3.update_layout(width=800, height=650)
    st.plotly_chart(fig3, use_container_width=True)

    chart1, chart2 = st.columns((2))
    with chart1:
        st.subheader('Segment Wise Sales')
        fig = px.pie(filtered_df, values='Sales', names='Segment', template='plotly_dark')
        fig.update_traces(text=filtered_df['Segment'], textposition='inside')
        st.plotly_chart(fig, use_container_width=True)
    with chart2:
        st.subheader('Category Wise Sales')
        fig = px.pie(filtered_df, values='Sales', names='Category', template='gridon')
        fig.update_traces(text=filtered_df['Category'], textposition='inside')
        st.plotly_chart(fig, use_container_width=True)

    import plotly.figure_factory as ff
    st.subheader(':point_right: Month wise Sub-Category Sales Summary')
    with st.expander('Summary Table'):
        df_sample = filtered_df[0:5][['Region','State','City','Category','Sales','Profit','Quantity']]
        fig = ff.create_table(df_sample, colorscale='Cividis')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('Month-Wise Sub-Category table')
        filtered_df['month'] = filtered_df['Order Date'].dt.month_name()
        sub_category_year = pd.pivot_table(data=filtered_df, values='Sales', index=['Sub-Category'], columns='month')
        st.write(sub_category_year.style.background_gradient(cmap='YlOrBr'))

    #Create a Scatter Plot
    data1 = px.scatter(filtered_df, x='Sales', y='Profit', size='Quantity')
    data1.update_layout(title='Relationship between Sales and Profit using Scatter Plot')

    st.plotly_chart(data1, use_container_width=True)

    with st.expander('View Data'):
        data = filtered_df.iloc[:500,:20:2]
        st.write(data.style.background_gradient(cmap='YlOrBr'))

    #Download Original Dataset
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button('Download Data', data = csv, file_name = 'Superstore.CSV',mime='text/csv', help='Download the whole Dataset')
