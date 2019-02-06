#!/usr/bin/env python
# coding: utf-8

# Peer Assignment Part 3

# In[1]:


import numpy as np # library to handle data in a vectorized manner

import pandas as pd # library for data analsysis
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import json # library to handle JSON files

#!conda install -c conda-forge geopy --yes # uncomment this line if you haven't completed the Foursquare API lab
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

import requests # library to handle requests
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# import k-means from clustering stage
from sklearn.cluster import KMeans

#!conda install -c conda-forge folium=0.5.0 --yes # uncomment this line if you haven't completed the Foursquare API lab
import folium # map rendering library

print('Libraries imported.')


# In[24]:


df_toronto = pd.read_csv("toronto_geo.csv")


# In[27]:


df_toronto.head(20)


# Toronto Map

# In[30]:


latitude = 43.6532
longitude = - 79.3832

toronto_map = folium.Map(location=[latitude, longitude], zoom_start=10)

# add markers to map
for lat, lng, borough, neighborhood in zip(df_toronto['Latitude'], df_toronto['Longitude'], df_toronto['Borough'], df_toronto['Neighbourhood']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(toronto_map)  
    
toronto_map


# Let's Explore A Burough: North York

# In[75]:


downtown_data = df_toronto[df_toronto['Borough'] == 'Downtown Toronto'].reset_index(drop=True)
downtown_data.head(10)


# Let's Create A map of North York

# In[78]:


latitude_downtown = 43.6543
longitude_downtown = -79.3860

map_downtown = folium.Map(location=[latitude_downtown, longitude_downtown], zoom_start=12)

# add markers to map
for lat, lng, label in zip(downtown_data['Latitude'], downtown_data['Longitude'], downtown_data['Neighbourhood']):
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7).add_to(map_downtown)  
    
map_downtown


# Foursquare Login

# In[38]:


CLIENT_ID = 'XFAQWDOTBHM21V31EO0GLP1BZWMPXEOUWS3UCHJIPRWBCZ4K' # your Foursquare ID
CLIENT_SECRET = 'LRODUIDEQKZALMTF5G3NZJTYFP2OFW5FDYK4EJSF4AIEZVEV' # your Foursquare Secret
VERSION = '20180605' # Foursquare API version

print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# In[82]:


# let's explore first neighbourhood in North York Dataframe

downtown_data.loc[5, 'Neighbourhood']


# In[85]:


neighborhood_latitude = downtown_data.loc[5, 'Latitude'] # neighborhood latitude value
neighborhood_longitude = downtown_data.loc[5, 'Longitude'] # neighborhood longitude value

neighborhood_name = downtown_data.loc[5, 'Neighbourhood'] # neighborhood name

print('Latitude and longitude values of {} are {}, {}.'.format(neighborhood_name, 
                                                               neighborhood_latitude, 
                                                               neighborhood_longitude))


# #### Now, let's get the top 100 venues that are in Parkwoods within a radius of 500 meters.

# In[91]:


LIMIT = 100
radius = 500

url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
    CLIENT_ID, 
    CLIENT_SECRET, 
    VERSION, 
    neighborhood_latitude, 
    neighborhood_longitude, 
    radius, 
    LIMIT)


# In[92]:


results = requests.get(url).json()
results


# In[93]:


# function that extracts the category of the venue
def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']


# In[94]:


venues = results['response']['groups'][0]['items']
    
nearby_venues = json_normalize(venues) # flatten JSON

# filter columns
filtered_columns = ['venue.name', 'venue.categories', 'venue.location.lat', 'venue.location.lng']
nearby_venues =nearby_venues.loc[:, filtered_columns]

# filter the category for each row
nearby_venues['venue.categories'] = nearby_venues.apply(get_category_type, axis=1)

# clean columns
nearby_venues.columns = [col.split(".")[-1] for col in nearby_venues.columns]

nearby_venues.head(10)


# In[95]:


print('{} venues were returned by Foursquare.'.format(nearby_venues.shape[0]))


# In[96]:


def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighbourhood', 
                  'Neighbourhood Latitude', 
                  'Neighbourhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[99]:


# get venues for each neighbourhood in downtown toronto

downtown_venues = getNearbyVenues(names=downtown_data['Neighbourhood'],
                                   latitudes=downtown_data['Latitude'],
                                   longitudes=downtown_data['Longitude'])


# In[102]:


print(downtown_venues.shape)
downtown_venues.head(10)


# In[103]:


downtown_venues.groupby('Neighbourhood').count()


# In[104]:


print('There are {} uniques categories.'.format(len(downtown_venues['Venue Category'].unique())))


# In[105]:


# analyze each neighbourhood

# one hot encoding
downtown_onehot = pd.get_dummies(downtown_venues[['Venue Category']], prefix="", prefix_sep="")

# add neighborhood column back to dataframe
downtown_onehot['Neighbourhood'] = downtown_venues['Neighbourhood'] 

# move neighborhood column to the first column
fixed_columns = [downtown_onehot.columns[-1]] + list(downtown_onehot.columns[:-1])
downtown_onehot = downtown_onehot[fixed_columns]

downtown_onehot.head()


# In[107]:


downtown_onehot.shape


# In[108]:


downtown_grouped = downtown_onehot.groupby('Neighbourhood').mean().reset_index()
downtown_grouped


# In[109]:


downtown_grouped.shape


# In[111]:


#top 5 in each neighbourhood

num_top_venues = 5

for hood in downtown_grouped['Neighbourhood']:
    print("----"+hood+"----")
    temp = downtown_grouped[downtown_grouped['Neighbourhood'] == hood].T.reset_index()
    temp.columns = ['venue','freq']
    temp = temp.iloc[1:]
    temp['freq'] = temp['freq'].astype(float)
    temp = temp.round({'freq': 2})
    print(temp.sort_values('freq', ascending=False).reset_index(drop=True).head(num_top_venues))
    print('\n')


# In[112]:


def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    
    return row_categories_sorted.index.values[0:num_top_venues]


# In[115]:


num_top_venues = 10

indicators = ['st', 'nd', 'rd']

# create columns according to number of top venues
columns = ['Neighbourhood']
for ind in np.arange(num_top_venues):
    try:
        columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind+1))

# create a new dataframe
neighbourhoods_venues_sorted = pd.DataFrame(columns=columns)
neighbourhoods_venues_sorted['Neighbourhood'] = downtown_grouped['Neighbourhood']

for ind in np.arange(downtown_grouped.shape[0]):
    neighbourhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(downtown_grouped.iloc[ind, :], num_top_venues)

neighbourhoods_venues_sorted.head()


# In[116]:


# cluster neighbourhoods


# In[117]:


# set number of clusters
kclusters = 5

downtown_grouped_clustering = downtown_grouped.drop('Neighbourhood', 1)

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(downtown_grouped_clustering)

# check cluster labels generated for each row in the dataframe
kmeans.labels_[0:10] 


# In[119]:


# add clustering labels
neighbourhoods_venues_sorted.insert(0, 'Cluster Labels', kmeans.labels_)

downtown_merged = downtown_data

# merge toronto_grouped with toronto_data to add latitude/longitude for each neighborhood
downtown_merged = downtown_merged.join(neighbourhoods_venues_sorted.set_index('Neighbourhood'), on='Neighbourhood')

downtown_merged.head() # check the last columns!


# In[120]:


# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# create map
map_clusters = folium.Map(location = [latitude_downtown, longitude_downtown], zoom_start=11)

# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i+x+(i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, poi, cluster in zip(downtown_merged['Latitude'], downtown_merged['Longitude'], downtown_merged['Neighbourhood'], downtown_merged['Cluster Labels']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters


# In[121]:


# examine clusters


# In[122]:


#cluster 1

downtown_merged.loc[downtown_merged['Cluster Labels'] == 0,downtown_merged.columns[[1] + list(range(5, downtown_merged.shape[1]))]]


# In[123]:


#cluster 2

downtown_merged.loc[downtown_merged['Cluster Labels'] == 1,downtown_merged.columns[[1] + list(range(5, downtown_merged.shape[1]))]]


# In[124]:


#cluster 3

downtown_merged.loc[downtown_merged['Cluster Labels'] == 2,downtown_merged.columns[[1] + list(range(5, downtown_merged.shape[1]))]]


# In[125]:


#cluster 4

downtown_merged.loc[downtown_merged['Cluster Labels'] == 3,downtown_merged.columns[[1] + list(range(5, downtown_merged.shape[1]))]]


# In[126]:


#cluster 5

downtown_merged.loc[downtown_merged['Cluster Labels'] == 4,downtown_merged.columns[[1] + list(range(5, downtown_merged.shape[1]))]]


# In[ ]:





# In[ ]:




