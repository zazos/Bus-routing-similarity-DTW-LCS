import pandas as pd
import numpy as np
from ast import literal_eval
import gmplot
from dtw import dtw
from haversine import haversine
import time


trainSet = pd.read_csv('train_set.csv', converters={"Trajectory": literal_eval}, index_col='tripId',nrows=100)

testSetA1 = pd.read_csv('test_set_a1.csv', sep='\t', converters={"Trajectory": literal_eval},nrows=100)



test_longitudes = []
test_latitudes = []
gps_test_points = []
# =============================================================================
#           test_set_csv
# append every latitude and longitude in lists
# and then append those lists to the corresponding list of lists
# =============================================================================
for N in range(len(testSetA1)):
    latitudes = []
    longitudes = []
    for deep_row in testSetA1.iloc[N]['Trajectory']:
        longitudes.append(deep_row[1])
        latitudes.append(deep_row[2])
    test_longitudes.append(longitudes)
    test_latitudes.append(latitudes)
# =============================================================================
# formatting them into tuple {latitude, longitude}
# =============================================================================
for N in range(len(testSetA1)):
    gps_test_points.append(zip(test_latitudes[N], test_longitudes[N]))


train_longitudes = []
train_latitudes = []
train_journey_pattern_id = []
gps_train_points = []
indices = []
# =============================================================================
#           train_set_csv
# append every latitude and longitude in lists
# and then append those lists to the corresponding list of lists
# =============================================================================
for index, row in trainSet.iterrows():
    latitudes = []
    longitudes = []
    for traject in row['Trajectory']:
        longitudes.append(traject[1])
        latitudes.append(traject[2])
    train_longitudes.append(longitudes)
    train_latitudes.append(latitudes)
    train_journey_pattern_id.append(row['journeyPatternId'])
    indices.append(index)
    
# =============================================================================
# formatting them into tuple {latitude, longitude}
# =============================================================================    

gps_train_points.append(zip(train_latitudes, train_longitudes))
for lat,lon in zip(train_latitudes, train_longitudes):
    print(lat,lon)
K = 5 # neighbors

for t in range(len(gps_test_points)):
    start = time.time()
    sorted_distances = []
    print ("Test Trip {0}".format(t+1))
    # =============================================================================
    # sorting the first 5 routes, keeping the distance in a tuple
    # and index_id
    # =============================================================================
    for i in range(K):  
        distances = []
        trip_ids = []
        # =============================================================================
        # dist = haversine without parameters, to check which function to call
        # and not how to call it. Furthermore, parameters are gps_test_points, gps_train_points
        # =============================================================================
        # dist = dtw(gps_test_points[0], gps_train_points[i], dist=haversine)
        # print(type(gps_test_points[0]))
        for tuple in gps_test_points:
            print(type(tuple))
            for i,x in tuple:
                print(type(i),type(x))
        dist = dtw(gps_test_points[0], gps_train_points[i], dist=haversine)[0]

        distances.append(dist)
        trip_ids.append(indices[i])
        sorted_distances.append(np.asarray(zip(distances, trip_ids)))

    # sorting with the first element of the tuple
    sorted_distances = sorted(sorted_distances, key=lambda tup: tup[0])

    # =============================================================================
    # storing in memory a list of 5 elements
    # if an element is pushed: push->sort->pop the biggest element of the list
    # =============================================================================
    for j in range(K, len(gps_train_points)):
        distances = []
        ids = []
        dist = dtw(gps_test_points[t], gps_train_points[j], dist=haversine)[0]
        distances.append(dist)
        ids.append(indices[j])
        element = zip(distances, ids)
        for y in range(len(sorted_distances)):
            if element[0][0] < sorted_distances[y][0][0]:
                sorted_distances.append(element)
                sorted_distances = sorted(sorted_distances, key=lambda tup: tup[0])
                sorted_distances.pop()
                break
    
    # =============================================================================
    # plot path of queries from test_set_a1.csv
    # =============================================================================
    query_latitudes = []
    query_longitudes = []
    for k in gps_test_points[t]:
        query_latitudes.append(k[0])
        query_longitudes.append(k[1])
    gmap = gmplot.GoogleMapPlotter(query_latitudes[0], query_longitudes[1], 16)
    gmap.plot(query_latitudes, query_longitudes, 'green', edge_width=3)
    name = "dtw_query_map" + str(t)
    save = name + ".html"
    gmap.draw(save)
    
    # =============================================================================
    # plot dtw_maps for the t-particular query
    # =============================================================================
    for i in range(K):
        gmap = gmplot.GoogleMapPlotter(gps_train_points[t][0][0], gps_train_points[t][0][1], 16) 
        nearest_latitudes = []
        nearest_longitudes = []
        for k in trainSet.loc[sorted_distances[i][0][1]]['Trajectory']:
            nearest_longitudes.append(k[1])
            nearest_latitudes.append(k[2])
        gmap.plot(nearest_latitudes, nearest_longitudes, 'blue', edge_width=3)
        name = "dtw_map" + str(t*5 + i)
        save = name + ".html"
        gmap.draw(save)
        print ("Neighbor {0} \n JP_ID {1} \n DTW = {2}km \n".format(i+1, trainSet.loc[sorted_distances[i][0][1]]['journeyPatternId'],sorted_distances[i][0][0]))
    end = time.time()
    DT = str(int((end - start))) + "s"
    print ("DT = {0}".format(DT)) 
