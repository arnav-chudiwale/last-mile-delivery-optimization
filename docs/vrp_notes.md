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

OR Tools Implementation Pattern -
1) Creating RoutingIndexManager - 
inputs that go inside RoutingIndexManager:
- number of rows of the distance matrix: number of locations + depot 
- number of vehicles
- node corresponding to the depot

2) Routing Model - 
Takes the outputs of the RoutingIndexManager as input 

3) Distance Callback - 
function that takes any pair of locations and returns the distance between them. 

the function accepts two indices - 
- from_index
- to_index
and returns the corresponding entry of the distance matrix

4) Search Parameters - 
We use the first_solution_strategy to let the solve find the initial solution
Options for first_solution_strategy:
- AUTOMATIC: Let the solver decide which strategy to choose according to the model being solved 
- PATH_CHEAPEST_ARC: Starting from the "start" node, connect to the node which produces the cheapest route segment and iterate until the "last" node
- BEST_INSERTION	Iteratively build a solution by inserting the cheapest node at its cheapest position; the cost of insertion is based on the global cost function of the routing model. As of 2/2012, only works on models with optional nodes (with finite penalty costs).
- PARALLEL_CHEAPEST_INSERTION	Iteratively build a solution by inserting the cheapest node at its cheapest position; the cost of insertion is based on the arc cost function. Is faster than BEST_INSERTION.
- LOCAL_CHEAPEST_INSERTION	Iteratively build a solution by inserting each node at its cheapest position; the cost of insertion is based on the arc cost function. Differs from PARALLEL_CHEAPEST_INSERTION by the node selected for insertion; here nodes are considered in their order of creation. Is faster than PARALLEL_CHEAPEST_INSERTION.
- GLOBAL_CHEAPEST_ARC	Iteratively connect two nodes which produce the cheapest route segment.
- LOCAL_CHEAPEST_ARC	Select the first node with an unbound successor and connect it to the node which produces the cheapest route segment.

5) Guided Local Search - 
- The routing solver does not always return the optimal solution.
- To find a better solution, a more advanced search strategy is called called "Guided Local Search"
- Enables the solver to escape the local minimum.
- After moving away from the local minimum, the solver continues the search until it reaches the global minimum
- this local search is IDEAL for Vehicle Routing Problems
- this is called Metaheuristics


