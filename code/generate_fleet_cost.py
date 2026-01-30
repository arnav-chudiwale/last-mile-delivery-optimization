import pandas as pd
import json 

print("Generating fleet data...")

# Defining Vehicle Parameters 

vehicles = [
    {
        'vehicle_type':'small_van',
        'capacity_packages':50, # Defining vehicle capacity as 50 packages per trip per vehicle
        'fixed_cost_per_day': 120, # $120/day -- Lease + insurance
        'cost_per_km': 0.5, # Variable cost/km -- Fuel + Mainatainance 
        'speed_kmph': 40, # Taking Urban Average
        'available_count': 8 # Size of the fleet that we own

    },

    {
        'vehicle_type':'large_van',
        'capacity_packages': 100,
        'fixed_cost_per_day':180,
        'cost_per_km': 0.75,
        'speed_kmph': 35,
        'available_count': 4

    }

]

df_fleet = pd.DataFrame(vehicles)
df_fleet.to_csv('data/fleet_data.csv', index=False)

print(f"Fleet Data Saved")
print(f" Total small vans:{df_fleet.loc[0,'available_count']}")
print(f" Total large vans:{df_fleet.loc[1,'available_count']}")

#Defining Cost Paramters 

costs = {
    'outsource_cost_per_package':12.5, #reflecting standard industry 3PL charges 
    'late_penalty_per_package': 5,
    'driver_hourly_rate_regular': 25.00,
    'driver_hourly_rate_overtime': 37.5,
    'regular_shift_hours': 8,
    'max_shift_hours': 10,
    'service_time_minutes_per_stop': 10
}

with open('data/cost_parameters.json','w') as f: 
    json.dump(costs, f, indent =2)

print(f" Cost Parameters Saved")
