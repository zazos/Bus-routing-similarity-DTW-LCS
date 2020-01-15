import pandas as pd
import ast
from haversine import haversine
from gmplot import *
import time

def lcs(a, b):
    lengths = [[0 for j in range(len(b)+1)] for i in range(len(a)+1)]
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if (haversine(x, y) <= 0.2):
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = max(lengths[i+1][j], lengths[i][j+1])
    result = []
    x, y = len(a), len(b)
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x-1][y]:
            x -= 1
        elif lengths[x][y] == lengths[x][y-1]:
            y -= 1
        else:
            result.append(a[x-1])
            x -= 1
            y -= 1
    return result, lengths[-1][-1]

start = time.time()

#   convert dataset into tuples [X, Z, Y]
TestSet = pd.read_csv("TestSet2.csv", sep='\t', converters={"Trajectory": ast.literal_eval})

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
        row_latitudes.append(every_row[1])
        row_longitudes.append(every_row[2])
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
        row_latitudes.append(every_row[1])
        row_longitudes.append(every_row[2])
    test_latitudes.append(row_latitudes)
    test_longitudes.append(row_longitudes)

# =============================================================================
# test_points[i]: list (the complete route)
# test_points[i][j]: tuple (point of a route {lon,lat})
# =============================================================================
test_points = []
for i in range(len(TestSet)):
    test_points.append(list(zip(test_latitudes[i], test_longitudes[i])))


MP = 5
total_DT = 0
for i in range(len(test_points)):
    lcs_start = time.time()
    print("Test Trip {0}".format(i+1))
    best_matching_paths = []
    # =============================================================================
    # dist = haversine without parameters, to check which function to call
    # and not how to call it. Furthermore, parameters are test_points, train_points
    # =============================================================================
    for j in range(MP):
        # lcs_dist: (lat, lon) that had the best sub-distance
        lcs_dist, matching_points = lcs(train_points[j], test_points[i])
        best_matching_paths.append((matching_points, lcs_dist, train_indices[j]))
    best_matching_paths = sorted(best_matching_paths, key=lambda tup: tup[0], reverse=True)
    # =============================================================================
    # storing in memory a list of 5 elements
    # if an element is pushed: push->sort->pop the least matching points
    # =============================================================================
    for j in range(MP, len(train_points)):
        lcs_dist, matching_points = lcs(train_points[j], test_points[i])
        distances = (matching_points, lcs_dist, train_indices[j])
        for w in range(len(best_matching_paths)):
            if distances[0] > best_matching_paths[w][0]:
                best_matching_paths.append(distances)
                best_matching_paths = sorted(best_matching_paths, key=lambda tup: tup[0], reverse=True)
                best_matching_paths.pop()
                break
    # =============================================================================
    # plot path of queries from test_set_a2.csv
    # =============================================================================
    query_latitudes = []
    query_longitudes = []
    for j in test_points[i]:
        query_latitudes.append(j[0])
        query_longitudes.append(j[1])
    gmap = gmplot.GoogleMapPlotter(query_latitudes[0], query_longitudes[1], 18, apikey="AIzaSyCy1v52WYnyTuCiAqoNC_QB2aQM_qCja7E")
    # gmap.apikey = "AIzaSyCy1v52WYnyTuCiAqoNC_QB2aQM_qCja7E"
    gmap.plot(query_latitudes, query_longitudes, 'green', edge_width=3)
    name = "lcs_query_map" + str(i)
    save = name + ".html"
    gmap.draw(save)

    # =============================================================================
    # plot dtw_maps for i-th query
    # =============================================================================
    for j in range(MP):
        if len(best_matching_paths[i][1]) == 0:
            continue
        else:
            gmap = gmplot.GoogleMapPlotter(best_matching_paths[i][1][0][0], best_matching_paths[i][1][0][1], 18,
                                           apikey="AIzaSyCy1v52WYnyTuCiAqoNC_QB2aQM_qCja7E")
        nearest_latitudes = []
        nearest_longitudes = []
        lcs_latitudes = []
        lcs_longitudes = []
        for w in best_matching_paths[i][1]:
            lcs_latitudes.append(w[0])
            lcs_longitudes.append(w[1])
        # find the exact route from TrainSet
        for k in TrainSet.loc[best_matching_paths[j][0]]['Trajectory']:
            nearest_longitudes.append(k[1])
            nearest_latitudes.append(k[2])
        gmap.plot(nearest_latitudes, nearest_longitudes, 'blue', edge_width=3)
        name = "lcs_map" + str(i*5 + j)
        save = name + ".html"
        gmap.draw(save)
        print("\tNeighbor {0} \n JP_ID {1} \n DTW = {2}km \n".format(j+1, TrainSet.loc[best_matching_paths[i][2]]['journeyPatternId'], best_matching_paths[i][0]))
    lcs_end = time.time()
    DT = str(float((lcs_end - lcs_start))) + "s"
    print("DT = {0}".format(DT))
end = time.time()
total_DT = float((end - start))
print("Total time = {0}s".format(total_DT))