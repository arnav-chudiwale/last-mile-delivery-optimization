'''
Creating interactive visualization of routes 
'''
import pandas as pd
import numpy as np 
import json 
import folium 
from folium import plugins

def create_route_map(solution_file, output_file):
    '''
    solution_file = Path to solution JSON file 
    output_file = Path to save HTML Map
    '''

    print(f"Creating route visualization..")

    #Load solution Data 
    with open(solution_file, 'r') as f: 
        solution = json.load(f)

    #Load Locations
    locations = pd.read_csv("data/delivery_locations.csv")

    #Add Depot as the first location 
    depot = pd.DataFrame([{
        'location_id': 0,
        'latitude': 40.7128,
        'longitude': -74.0060,
        'address': 'Distribution Centre'
    }])

    all_locations = pd.concat([depot, locations], ignore_index=True)

    #Create Base Mao 
    center_lat = 40.7128
    center_long = -74.0060

    m = folium.Map(
        location=[center_lat, center_long],
        zoom_start = 12,
        tiles = 'OpenStreetMap'
    )

    #Add depot marker (special icon)
    folium.Marker(
        location=[center_lat, center_long],
        popup = '<b> DEPOT </b> <br> Distribution Center',
        icon = folium.Icon(color = 'red', icon = 'warehouse', prefix = 'fa')
    ).add_to(m)

    #color pallete for routes

    colors = [
        'blue', 'green', 'purple', 'orange', 'darkred', 
        'lightred', 'beige', 'darkblue', 'darkgreen', 
        'cadetblue', 'darkpurple', 'white', 'pink', 
        'lightblue', 'lightgreen', 'gray', 'black', 
        'lightgray'
    ]

    #Plot each route 
    for route_info in solution['routes']:
        vehicle_id = route_info['vehicle_id']
        route = route_info['route']
        color = colors[vehicle_id % len(colors)]

        #Getting co-ordinates for the route
        route_coords = []
        for node_id in route:
            if node_id < len(all_locations):
                loc = all_locations.iloc[node_id]
                route_coords.append((loc['latitude'], loc['longitude']))

        
        #Draw route polyline (only if we have at least two coords)
        if len(route_coords) >= 2:
            folium.PolyLine(
                route_coords,
                color = color, 
                weight = 3,
                opacity = 0.75,
                popup = f"<b> Vehicle {vehicle_id} </b><br>"
                f"Stops: {route_info['num_stops']}<br>"
                f"Distance: {route_info['distance_km']:.1f}km<br>" 
                f"Load: {route_info['load']} packages"

            ).add_to(m)

        #Add markers for delivery stops (skip the depot start/end)
        for i, node_id in enumerate(route[1:-1],1): #skip first and last in the route
            if node_id < len(all_locations):
                loc = all_locations.iloc[node_id]
                
                folium.CircleMarker(
                    location = [loc['latitude'], loc['longitude']],
                    radius = 4,
                    color = color, 
                    fill = True,
                    fillColor = color, 
                    fillOpacity = 0.6,
                    popup = f"<b> Stop #{i}</b><br>"
                    f"Vehicle {vehicle_id}<br>"
                    f"Location{node_id}"
                ).add_to(m)

        #Add legend 
    legend_html = f"""
        <div style="position: fixed; top: 10px; right: 10px; width: 150px; height: auto; background-color: white; border:2px solid grey; z-index:9999; font-size:14px; border-radius:5px; padding: 10px">
        <p><b>{solution['scenario'].upper()} Scenario</b></p>
        <p>Vehicles: {solution['vehicles_used']}</p>
        <p>Total Distance: {solution['total_distance_km']:.1f} km</p>
        <p>Packages Delivered: {solution['total_load']}</p>
        </div>
        """
    m.get_root().html.add_child(folium.Element(legend_html))

    #Ensure output directory exists and save map with a retry to handle intermittent hangs
    import os
    import time

    out_dir = os.path.dirname(output_file) or '.'
    os.makedirs(out_dir, exist_ok=True)

    last_exc = None
    for attempt in range(1, 3):
        try:
            print(f"Saving map (attempt {attempt})...")
            m.save(output_file)
            print(f"Route map saved to {output_file}")
            print(f" Open in browser to view the interactive map.")
            return m
        except Exception as e:
            last_exc = e
            print(f"Warning: failed to save map on attempt {attempt}: {e}")
            time.sleep(1)

    # If we reach here, re-raise the last exception for visibility
    raise last_exc

if __name__ == "__main__":
    create_route_map(
        'results/baseline_solution.json',
        'results/baseline_routes_map.html'
    )



            
