Vehicle Routing Problem - My understanding: 

Core Problem:
Fundamentally, VRP is an Optimization problem where we are given - 
- cental depot 
- locations to visit 
- distances between every node to every other node
- number of vehicles
We need to figure out routes for each vehicle that starts from the central depot, so that all the locations are covered in all the routes EXACTLY ONCE and the vehicles return back to the central depot 

Objective - minimize the total distance covered by all the vehicles 

Key Constraints: 
- vehicle capacity: total number of vehicles leaving and returning back to the depot remain constant [each vehicle visits each location exactly once in the route]
[NOTE - Each vehicle does not cover all the locations in its route - ONLY A SUBSET OF THE LOCATIONS]

- Time Windows: 
1) Additional constraints can be added where each location must be visited within a certain time window
2) Here, instead of 'distances' between two nodes, we define time taken from each node to every other node in the data
3) The objective then becomes to minimize the total time taken in all the routes of all vehicles 

- Why it matters in last-mile delivery: 
1) Last mile delivery is the final delivery step of the item from the warehouse to the hands of the customer. 
2) The way VRP maps to last-mile delivery is as follows - 
--> We have customer locations as the delivery locations 
--> Warehouse as the central depot 
--> We need to minimize the total travel time/distance in the routing

WHY - so that more number of packages can be delivered in a day
- this increases the daily throughput of the e-commerce platform
- packages get delivered on time 
- customer satisfaction increases 
- which results in increases customer retention 
- which results in more sale on the platform
- more companies list their products
- revenue increases for the e-commerce platform
