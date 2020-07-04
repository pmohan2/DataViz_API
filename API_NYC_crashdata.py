import matplotlib.pyplot as plt
import pandas as pd
#!pip install sodapy
from sodapy import Socrata
import seaborn as sns
import gmaps
from ipywidgets.embed import embed_minimal_html

#client = Socrata("data.cityofnewyork.us", None)
username ='Enter User name'
password = 'Enter Password'
MyAppToken = 'Enter Apptoken'
client = Socrata('data.cityofnewyork.us', MyAppToken, username=username,password=password)

results = client.get("h9gi-nx95", limit=100000)
results_df = pd.DataFrame.from_records(results)

#---------------------Visualization using Contributing factors for accidents---
#---------------------Contributing factors for accidents-----------------------
results_df['year'] = pd.DatetimeIndex(results_df['crash_date']).year
results_df['month'] = pd.DatetimeIndex(results_df['crash_date']).month
results_df['weekday'] = pd.DatetimeIndex(results_df['crash_date']).weekday
results_df['hour'] = pd.DatetimeIndex(results_df['crash_time']).hour
df1=results_df[(results_df.year >= 2019)]

df1.loc[:,'number_of_persons_killed'] = df1['number_of_persons_killed'].astype(int)
newframe = pd.DataFrame(df1.groupby(['contributing_factor_vehicle_1'])['number_of_persons_killed'].count())
newframe['Cause']=newframe.index
newframe = newframe.sort_values(by='number_of_persons_killed', ascending=False)
newframe = newframe.reset_index(drop=True)
newframea = newframe[['Cause', 'number_of_persons_killed']]

df1.loc[:,'number_of_persons_injured'] = df1['number_of_persons_injured'].astype(int)
newframe1 = pd.DataFrame(df1.groupby(['contributing_factor_vehicle_1'])['number_of_persons_injured'].sum())
newframe1 = newframe1.sort_values(by='number_of_persons_injured', ascending=False)
newframe1['Cause'] = newframe1.index

newframe2 = pd.merge(newframea, newframe1, on='Cause')
newframe2 = newframe2.head(5)
newframe2.index = newframe2['Cause']
newframe2 = newframe2.rename(columns = {"number_of_persons_injured":"No. of Persons Injured", "number_of_persons_killed":"No. of Accidents"}) 

#---------------------Bar plot-------------------------------------------------
fig,(ax1,ax2) =plt.subplots(2,1,figsize = (12,12))
ax = newframe2.plot.bar(rot=0,ax=ax1, width = 0.7)
ax.legend(fontsize = 14)
ax.xaxis.label.set_size(14)
ax.set_title('Top Five Accident Contributing Factors', fontsize = 15)
plt.xticks(fontsize = 9, wrap = True)

#---------------------Pie plot-------------------------------------------------
newframe3 = pd.DataFrame(df1.groupby(['contributing_factor_vehicle_1'])['number_of_persons_killed'].sum())
Others = sum(newframe3['number_of_persons_killed']==1)
newframe3=newframe3[newframe3['number_of_persons_killed']>1]
newframe3['Cause'] = newframe3.index
newframe3 = newframe3.reset_index(drop=True)
newframe3 = newframe3.append({'number_of_persons_killed':Others,'Cause':'Others'},ignore_index=True)
newframe3 = newframe3.sort_values(by='number_of_persons_killed', ascending=False)
newframe3 = newframe3.head(7)
a=sum(newframe3['number_of_persons_killed'])
newframe3['number_of_persons_killed'] = round((newframe3['number_of_persons_killed']/a)*100,0)

ax2.pie(newframe3['number_of_persons_killed'],labels=newframe3['Cause'],autopct='%1.1f%%')
ax2.set_title('% of Mortality by each Factor', fontsize = 15)
plt.show()
plt.savefig('Bar_Pie.png')
#------------------------------------------------------------------------------

#---------------------Visualization of number of accidents using Heatmap-------
count_data1 = [results_df[results_df['month'] == i].groupby('weekday').size() for i in list(range(1,13))]
count_data2 = [results_df[results_df['weekday'] == i].groupby('hour').size() for i in list(range(0,7))]
month = ['January', 'Febraury', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
weekday = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
hour = list(range(0,24))
data1 = []
data2 = []
for m in range(len(month)):
    for w in range(len(weekday)):
        try:
            data1.append([month[m], weekday[w], count_data1[m][w]])
        except:
            data1.append([month[m], weekday[w], 0])
for w in range(len(weekday)):
    for h in range(len(hour)):
        try:
            data2.append([weekday[w], hour[h], count_data2[w][h]])
        except:
            data1.append([weekday[w], hour[h], 0])
heatmap_df1 = pd.DataFrame(data1, columns = ['Month', 'Weekday', 'Crash_Count'])
heatmap_df2 = pd.DataFrame(data2, columns = ['Weekday', 'Hour', 'Crash_Count'])

#-------------------------Crash count(Monthly vs Weekly)-----------------------

plt.figure(figsize = (15, 9))
file_long = heatmap_df1.pivot("Weekday", "Month", "Crash_Count")
sns.heatmap(file_long, cmap = 'viridis', annot=True, fmt=".0f")
plt.title("Heatmap of Crash Count in New York City (Monthly vs Weekly)", fontsize = 14);

#-------------------------Heatmap for Weekly vs Hourly------------------------- 

plt.figure(figsize = (20, 10))
file_long = heatmap_df2.pivot("Weekday", "Hour", "Crash_Count")
sns.heatmap(file_long, cmap = 'viridis', annot=True, fmt=".0f")
plt.title("Heatmap of Crash Count in New York City (Weekly vs Hourly)", fontsize = 14);

#------------------------Visualizing using Gmaps-------------------------------
results_df = results_df[results_df['latitude'].notna()]
locations=pd.DataFrame(results_df[['latitude','longitude']])
locations[['latitude','longitude']] = locations[['latitude','longitude']].astype(float)
#new=results_df.groupby(['latitude','longitude']).size().reset_index().rename(columns={0:'count'})
#new= new.sort_values('count',ascending=False)
#points = new[new['count'] >= 40] #value to change
#points=points[['latitude','longitude']].astype(float)

gmaps.configure(api_key='Enter api Key')
nyc_coordinates = (40.7128, -74.0060)
fig = gmaps.figure(center=nyc_coordinates, zoom_level=10.5)#map_type='HYBRID'
heatmap_layer=gmaps.heatmap_layer(locations)
heatmap_layer.max_intensity = 200
heatmap_layer.point_radius = 15
#markers = gmaps.marker_layer(points)
#scatter = gmaps.symbol_layer(locations, fill_color='blue', stroke_color='blue', scale=2)
fig.add_layer(heatmap_layer)
embed_minimal_html('export.html', views=[fig])


