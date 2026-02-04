Project - Last Mile Delivery Optimization for Peak Season Demand Variability

Problem Statement - 
E-commerce fulfillment centers face capacity constraints during peak shopping seasons when demand surges roughly by 167% (Avg variability across industry standards) above baseline for 5-10 days. 

The project optimizes trade-offs between - 
- Extended driver shifts (overtime delivery premiums) utilizing owned fleet
- Outsourcing to 3PL partners (per package premiums)
- Delayed deliveries (compromising on service levels which incur penalty)

Dataset - 
- 500 urban delivery locations clustered around 8 neighborhoods 
(Used Lat Long co-ordinates of New York, NY as the depot location and the rest of the location co-ordinates randomly generate from the depot co-ordinates)
- Baseline demand: 1490 packages/day
- Peak Demand: 3906 packages/day (162% increase in demand)
- In-House Fleet: 
32 small vans: Capacity - 50 packages/vehicle

Methodology - 
1. Baseline VRP (during normal operations)
2. Peak scenario modelling 
3. Capacity Gap Analysis 
4. Multi-Strategy Optimization
5. Sensitivity Analysis 

Technologies - 
1. Python 3.9+
2. Google OR Tools - for solving VRP
3. Folium - for geospatial visualization
4. Numpy/Pandas - for data processing

Status - 
1) Day 1: Data Generation Complete
2) Day 2.1 - Building VRP Solver and Testing Base Case
3) Day 2.2 - Created Route Visualization and Analysis Charts + Documented Base Base Results
4) Day 3.1 - Performed Peak Season Cost Analysis
5) Day 3.2 - Performed Strategy Comparison for Peak Season 
6) Day 3.3 - Generated Interactive Web Charts for Strategy Comparison
7) Day 3.4 - Performed Overtime_Outsourcing Optimization + Documented Results
8) Day 4 - Dynamic Routing simulation and Sensitivity Analysis


