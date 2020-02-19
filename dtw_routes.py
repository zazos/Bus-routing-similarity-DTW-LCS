import pandas as pd
import ast
from haversine import haversine
from dtw import dtw
from gmplot import *
import time

start = time.time()

#   convert dataset into tuples [X, Z, Y]
TestSet = pd.read_csv("TestSet1.csv", sep='\t', converters={"Trajectory": ast.literal_eval})

TrainSet = pd.read_csv("TrainSet.csv", converters={"Trajectory": ast.literal_eval})

train_latitudes = []
train_longitudes = []
train_journeyPatternId = []
train_indices = []

#   Elements for the train set
for index, row in TrainSet.iterrows():
    row_latitudes = []
    row_longitudes = []
    for every_row in TrainSet.iloc[index]['Trajectory']:
        row_longitudes.append(every_row[1])
        row_latitudes.append(every_row[2])
    train_latitudes.append(row_latitudes)
    train_longitudes.append(row_longitudes)
    train_journeyPatternId.append(row['Trajectory'])
    train_indices.append(index)

# =============================================================================
# train_points[i]: list (the complete route)
# train_points[i][j]: tuple (point of a route {lon,lat})
# =============================================================================
train_points = []
for i in range(len(TrainSet)):
    train_points.append(list(zip(train_latitudes[i], train_longitudes[i])))

test_latitudes = []
test_longitudes = []
#   Elements for the test set
for index, row in TestSet.iterrows():
    row_latitudes = []
    row_longitudes = []
    for every_row in TestSet.iloc[index]['Trajectory']:
        row_longitudes.append(every_row[1])
        row_latitudes.append(every_row[2])
    test_latitudes.append(row_latitudes)
    test_longitudes.append(row_longitudes)

# =============================================================================
# test_points[i]: list (the complete route)
# test_points[i][j]: tuple (point of a route {lon,lat})
# =============================================================================
test_points = []
for i in range(len(TestSet)):
    test_points.append(list(zip(test_latitudes[i], test_longitudes[i])))

K = 5
total_DT = 0
for i in range(len(test_points)):
    dtw_start = time.time()
    print("Test Trip {0}".format(i+1))
    sorted_distances = []
    # =============================================================================
    # dist = haversine without parameters, to check which function to call
    # and not how to call it. Furthermore, parameters are test_points, train_points
    # =============================================================================
    for j in range(K):
        dtw_dist = dtw(test_points[i], train_points[j], dist=haversine)[0]
        sorted_distances.append((dtw_dist, train_indices[j]))
    sorted_distances = sorted(sorted_distances, key=lambda tup: tup[0])

    # =============================================================================
    # storing in memory a list of 5 elements
    # if an element is pushed: push->sort->pop the biggest element of the list
    # =============================================================================
    for j in range(K, len(train_points)):
        dtw_dist = dtw(test_points[i], train_points[j], dist=haversine)[0]
        distances = (dtw_dist, train_indices[j])
        for w in range(len(sorted_distances)):
            if distances[0] < sorted_distances[w][0]:
                sorted_distances.append(distances)
                sorted_distances = sorted(sorted_distances, key=lambda tup: tup[0])
                sorted_distances.pop()
                break

    # =============================================================================
    # plot path of queries from test_set_a1.csv
    # =============================================================================
    query_latitudes = []
    query_longitudes = []
    for j in test_points[i]:
        query_longitudes.append(j[1])
        query_latitudes.append(j[0])
    gmap = gmplot.GoogleMapPlotter(query_latitudes[0], query_longitudes[0], 18, apikey="AIzaSyCy1v52WYnyTuCiAqoNC_QB2aQM_qCja7E")
    gmap.plot(query_latitudes, query_longitudes, 'green', edge_width=3)
    name = "dtw_query_map" + str(i)
    save = name + ".html"
    gmap.draw(save)

    # =============================================================================
    # plot dtw_maps for i-th query
    # =============================================================================
    for j in range(K):
        # train_points[i][0][0]: lat
        # train_points[i][0][1]: lon
        gmap = gmplot.GoogleMapPlotter(train_points[i][0][0], train_points[i][0][1], 18, apikey="AIzaSyCy1v52WYnyTuCiAqoNC_QB2aQM_qCja7E")
        nearest_latitudes = []
        nearest_longitudes = []
        # find the exact route from TrainSet
        for k in TrainSet.loc[sorted_distances[j][1]]['Trajectory']:
            nearest_longitudes.append(k[1])
            nearest_latitudes.append(k[2])
        gmap.plot(nearest_latitudes, nearest_longitudes, 'blue', edge_width=3)
        name = "dtw_map" + str(i*5 + j)
        save = name + ".html"
        gmap.draw(save)
        print("\tNeighbor {0} \n JP_ID {1} \n DTW = {2}km \n".format(j+1, TrainSet.loc[sorted_distances[i][1]]['journeyPatternId'], sorted_distances[i][0]))
    dtw_end = time.time()
    DT = str(float((dtw_end - dtw_start))) + "s"
    print("DT = {0}".format(DT))
end = time.time()
total_DT = float((end - start))
print("Total time = {0}s".format(total_DT))