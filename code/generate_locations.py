'''
Generating - 
1) 500 delivery locations (realistic urban distribution)
The locations are generated randomly from the actual lat and long co-ordinates of NYC, USA
2) Co-ordinates 
3) Demand - packages per location 
4) Time preference (time slots for delivery per location)
5) Depot location

'''
import pandas as pd 
import numpy as np
import random 

#reproduccibility
np.random.seed(42)
random.seed(42)

print("Generating Delivery Locations...")

#Choosing the depot location as the co-ordinates of NYC
DEPOT_LAT = 40.7128
DEPOT_LONG = -74.0060

#Generating 8 neighborhood clusters - mimicking realistic urban pattern 
n_clusters = 8 
n_locations = 500 

cluster_centers = []
for i in range(n_clusters):
    #cluster centers are randomly generated as being within 10 kms radius of depot
    lat = DEPOT_LAT + np.random.uniform(-0.09, 0.09)
    long = DEPOT_LONG + np.random.uniform(-0.09, 0.09)

    cluster_centers.append((lat, long))
 
#Randomly generating delivery points around the clusters generated above
locations = []
for i in range(n_locations):
    cluster = random.choice(cluster_centers)

    #Adding variation around the cluster center to generate locations around them

    lat = cluster[0] + np.random.normal(0,0.01)
    long = cluster[1] + np.random.normal(0,0.01)

    locations.append({
        'location_id':i,
        'latitude': lat,
        'longitude': long,
        'address':f"{i} Main Street, New York, NY"
    })

df = pd.DataFrame(locations)

#Generating Demand 
# Most locations: 1-3 packages 
# Bulk - 5-10 packages 

base_demand = np.random.choice(
    [2,3,4,8,10],
    size = n_locations, #demand corresponding to the 500 locations
    p = [0.50, 0.30, 0.15, 0.04, 0.01] #weights assigned to each entry in the array above for random selection
)

df['base_demand'] = base_demand

# Peak demand: 2.67x SURGE (1.67% INCREASE)
df['peak_demand']=(df['base_demand']*2.67).round().astype(int)

# Time windows preferences
time_prefs = np.random.choice(
    ['morning', 'afternoon', 'evening'],
    size = n_locations, #mapping it to 500 locations
    p = [0.4, 0.4, 0.2] # 40% weight given to morning and afternoon and 20% weight given to evening for random selection
)

time_windows = {
    'morning':(8,12),
    'afternoon':(12, 16),
    'evening':(16,20)
}

df['time_window_start'] = [time_windows[p][0] for p in time_prefs]
df['time_window_end'] = [time_windows[p][1] for p in time_prefs]

#Saving the dataset

df.to_csv('data/delivery_locations.csv', index=False)

print(f"Generated {n_locations} Locations")
print(f" Base Total Demand: {df['base_demand'].sum()} packages")
print(f" Peak Total Demand: {df['peak_demand'].sum()} packages")
print(f" Surge Factor: {df['peak_demand'].sum() / df['base_demand'].sum():.2f} x")

