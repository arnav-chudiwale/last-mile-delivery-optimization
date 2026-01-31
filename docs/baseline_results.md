Baseline Scenario Results

1) Problem Setup
- Demand: 1,490 packages (total demand served)
- Fleet: 32 small vans (50-package capacity each)
- Objective: Minimize total operational cost (fixed + fuel + labor) / total distance while serving all demand subject to vehicle capacity constraints

'''Assumed Data (Industry Standards)
Fleet costs - 
- Small Vans (used for base case):
a) Capacity - 50 Packages/vehicle
b) Fixed Cost/day - $120
c) Variable Cost (fuel) - $0.5/km
d) average speed of commute - 40 kmph

Driver Costs - 
a) Driver Hourly Rate (Regular time) - 25$/hour
b) Regular shift hours - 8 hours/day'''

2) Solution Summary
Performance Metrics -- 
- Vehicles Used: 31 (96.9% fleet utilization)
- Total Distance: 612.204 km
- Total Packages: 1,490
- Average Distance per Route: 19.75 km
- Average Load per Vehicle: 48.06 packages (96.1% of vehicle capacity)
- Fleet Utilization: 96.9%
Notes: route distances range from 8.47 km to 30.67 km; route loads range from 39 to 50 packages.

3) Cost Breakdown
a) Fixed (Vehicles) - 
Amount - $3,720.00
% of Total - 36.4%

b) Variable (Fuel) - 
Amount - $306.10
% of Total - 3.0%

c) Labor (Drivers) - 
Amount - $6,200.00	
% of total - 60.6%

Cost per Package: $6.86

4) Key Insights - 
- Efficiency
a) Route Balance: Routes are mostly balanced — many vehicles operate at or near full capacity (49–50 packages), though a few are underutilized (loads as low as 39). 

b) Capacity Utilization: 96.1% average — excellent usage of vehicle capacity; limited headroom for consolidation. 

c) Distance Efficiency: Average route length (19.8 km) is moderate; a small number of routes (30.4 km) are significantly longer, indicating geographic spread or outliers that could be targeted for further optimization. 

- Constraints
a) All capacity constraints satisfied ✓
b) All demand served ✓
c) All vehicles return to depot ✓

5) Visualization 
Route map: baseline_routes_map.html ✅
Analysis charts: baseline_analysis.png ✅
