# Bus-routing-similarity-DTW-LCS
Find similar bus routes using DTW and LCS methods with given dataset from uni

Extract the dataset from Dataset.rar into the folder of the project and you're ready to go.

Execute dtw_routes with TestSet1 and lcs_routes with TestSet2

Important note about the gmplot library. As of now, Google Maps Cloud changed from free of use and thus you can only plot for developer use only. To fix this, i'm redirecting you to a certain thread on github, where some people of the community have already found the solution to that. "https://github.com/pbugnion/gmaps/issues/237"
Basically, claiming an API key for Google and/or enabling Billing will resolve this problem. 

Using the DTW method, along with haversine metric to calculate distances, i'm able to compare points {latitude, longitude}
and thus compare lists of points, which are the bus routes. 
Finding the K similar bus routes of given route from test_sets, i'm plotting, using gmplot library, these routes. 

Finally, im creating html files, 5 * queries from test files. For example, dtw_map0 to dtw_map4 are the 5 similar bus routes to dtw_query_map0.

Update: Added LCS (least common subsequence) algorithm, which will help to find the bus routes that have the most common sub-route with the lcs_query_map. (looking at MP common subsequences, which in my project is 5)
