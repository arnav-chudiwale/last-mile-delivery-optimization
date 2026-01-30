import pandas as pd
import numpy as np 

import json 

print("Calculating distance matrix...")

# KEY CONCEPT - 
'''
VRP solvers need know the distance between ALL pairs of locations 

To store the distances - we use a matrix
size - 501*501 (500 locations + 1 depot)
'''

#Load Locations
df = pd.read_csv("data/delivery_locations.csv")

#Depot co-ordinates
DEPOT_LAT = 40.7128
DEPOT_LONG = -74.0060

#All co-ordinates (depot+delivery locations)
all_lats = np.array([DEPOT_LAT] + df['latitude'].tolist())
all_longs = np.array([DEPOT_LONG] + df['longitude'].tolist())

# Building the function that gives the distance between any two co-ordinates in KM using Haversine Formula
def haversine_distance(lat1, long1, lat2, long2):
    '''
    GOAL - We need to calculate the shortest distance between two points on the surface of the EARTH
    
    this distance is called - Great Circle Distance 

    One method to calculate the Great Circle Distance is to use the Haversine Formula - 
    
    Haversine Formula returns the distance between 2 co-ordinates in kms

    '''
    R = 6371 # Radius of Earth

    #coverting the co-ordinates into radians 

    lat1, long1, lat2, long2 = map(np.radians, [lat1, long1, lat2, long2])

    #Calculating the measure of difference between the radians of lat and long
    d_lat = lat2 - lat1 
    d_long = long2 - long1

    a = np.sin(d_lat/2)**2 + np.cos(lat1)*np.cos(lat2) + np.sin(d_long/2)**2
    c = 2 * np.arcsin(np.sqrt(a))

    return R*c

# Calculating the distance matrix

n = len(all_lats)
distance_matrix = np.zeros((n,n))

print (f"Computing distances for {n} locations...")

for i in range (n):
    for j in range(n):
        if i != j:
            distance_matrix[i,j] = haversine_distance(
                all_lats[i], all_longs[i],
                all_lats[j],all_longs[j]
            )

        #if i % 50 == 0:
            #print(f"Progress : {i}/{n}")

# Calculating time matrix from distance matrix 

SPEED_KMPH = 40 
time_matrix = (distance_matrix/SPEED_KMPH * 60).astype(int) # enters time in MINUTES

#Saving distance matrix and time matrix
np.save('data/distance_matrix.npy', distance_matrix)
np.save('data/time_matrix.npy', time_matrix)

#Saving meta data
metadata = {
    'n_locations':n-1,
    'depot_index':0,
    'speed_kmph': SPEED_KMPH,
    'service_time_minutes': 5,
    'max_distance_km': float(distance_matrix.max()),
    'avg_distance_km': float(distance_matrix[distance_matrix>0].mean())
}

with open('data/distance_metadata.json', 'w') as f:
    json.dump(metadata, f, indent = 2)

print(f"Distance matrix saved")
print(f" Shape: {distance_matrix.shape}")
print(f" Max Distance:{metadata['max_distance_km']:.2f} km")
print(f" Avg Distance:{metadata['avg_distance_km']:.2f} km")



