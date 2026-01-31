'''
Vehicles Routing Problem Solver Module
'''
import pandas as pd
import numpy as np 
import json

from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

class VRPSolver: 
    '''
    Class that solves capacitated VRP for last-mile delivery
    '''

    def __init__(self, scenario='base'): 
        '''
        function takes two arguments: 
        scenario: "base" for normal ops, "peak" for demand surges
        '''
        self.scenario = scenario 
        self.load_data()

    def load_data(self):
        print(f"Loading data for {self.scenario} scenario...")

        #Locations 
        self.locations = pd.read_csv('data/delivery_locations.csv')

        #Demand (selecting column based on scenario - base/peak)
        demand_col = 'base_demand' if self.scenario == 'base' else 'peak_demand'
        self.demands = [0] + self.locations[demand_col].tolist()

        #Distance Matrix
        self.distance_matrix = np.load('data/distance_matrix.npy')
        self.time_matrix = np.load('data/time_matrix.npy')

        #Fleet 
        self.fleet = pd.read_csv('data/fleet_data.csv')

        #Costs 
        with open('data/cost_parameters.json', 'r') as f:
            self.costs = json.load(f)

        #Metadata 
        with open('data/distance_metadata.json', 'r') as f:
            self.metadata = json.load(f)

        print(f"Data Loaded")
        print (f" Total Demand: {sum(self.demands)} packages")
        print (f" Locations: {len(self.demands)-1}")

    def create_data_model(self, num_vehicles, vehicle_capacity):
        '''
        Packaging Data for OR Tools 

        function returns:
        dict: data model for routing 

        '''
        data = {}
        data['distance_matrix'] = self.distance_matrix.tolist()
        #coverts numpy array into nested python lists -- OR tools expect native lists and not numpy arrays as inputs
        data['time_matrix'] = self.time_matrix.tolist()
        # OR Tools need integer arc costs, so we convert km floats to integer meters to avoid truncation to zero
        scaled_dist = np.rint(self.distance_matrix * 1000).astype(int)
        data['distance_matrix'] = scaled_dist.tolist()
        #Ensuring time matrix is integer
        data['time_matrix'] = np.rint(self.time_matrix).astype(int).tolist()
        data['demands'] = self.demands
        data['vehicle_capacities'] = [vehicle_capacity]*num_vehicles
        data['num_vehicles'] = num_vehicles

        data['depot'] = 0
        return data
    
    #Creating SOLVE instance 
    def solve(self, num_vehicles, vehicle_capacity, time_limit_seconds=300):
        '''
        :param time_limit_seconds: Maximum Solver time

        returns: 
        dict: Solution with Routes and Costs

        '''
        print(f"\n{'='*70}") # prints a seperator line with 70 ====
        print(f"Solving VRP - {self.scenario.upper()} Scenario")
        print(f"\n{'='*70}") 
        print(f"Vehicles: {num_vehicles}, Capacity: {vehicle_capacity} packages")

        #Create Data Model 
        data = self.create_data_model(num_vehicles, vehicle_capacity)

        #Creating Routing Index Manager - manages the relationship between internal solver indices and our problem's node indices
        manager = pywrapcp.RoutingIndexManager(
            len(data['distance_matrix']),
            data['num_vehicles'],
            data['depot']
        )

        #Creating Routing Model 
        routing = pywrapcp.RoutingModel(manager)

        #Defining distance callback
        # Tells the solver how to compute distances between any two locations

        def distance_callback(from_index, to_index):
            try:
                # Ensure we pass plain Python ints into the C++ API
                from_node = manager.IndexToNode(int(from_index))
                to_node = manager.IndexToNode(int(to_index))
                # Return plain Python int (matrix already contains ints)
                return int(data['distance_matrix'][from_node][to_node])
            except Exception:
                # If anything goes wrong (including interpreter shutdown), return safe default
                return 0
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        #Setting arc cost 
        '''
        this is what the solver will try to minimize 
        '''
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        #Adding Capacity Constraint
        def demand_callback(from_index):
            try:
                # returns demand of the node (cast index to Python int first)
                from_node = manager.IndexToNode(int(from_index))
                return int(data['demands'][from_node])
            except Exception:
                return 0
        
        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,
            data['vehicle_capacities'],
            True,
            'Capacity')
        
        #Set search parameters 
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
        search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        search_parameters.time_limit.seconds = 300  # increase
        #earch_parameters.log_search = True  # enable solver logs

        # try increasing vehicles if minimum fails
        for extra in [0, 2, 5, 10]:
            try_vehicles = num_vehicles + extra
            print(f"Attempting with {try_vehicles} vehicles (extra={extra})")
            data = self.create_data_model(try_vehicles, vehicle_capacity)
            manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'], data['depot'])
            routing = pywrapcp.RoutingModel(manager)
            transit_callback_index = routing.RegisterTransitCallback(distance_callback)
            routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
            demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
            routing.AddDimensionWithVehicleCapacity(demand_callback_index, 0, data['vehicle_capacities'], True, 'Capacity')

            solution = routing.SolveWithParameters(search_parameters)
            if solution:
                print("Solution Found")
                return self.extract_solution(data, manager, routing, solution)

        print("No Solution Found after trying increased vehicles")
        return None
        

    def extract_solution(self, data, manager, routing, solution):
        '''
        Extracts solution details from OR-Tools solution object
        '''
        total_distance_m = 0  # keep meters while summing (we scaled distances to meters)
        total_load = 0 
        routes = []

        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            route = []
            route_distance_m = 0
            route_load = 0

            # Traverse the route for the vehicle
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(int(index))
                route_load += data['demands'][node_index]
                route.append(node_index)

                previous_index = index
                index = solution.Value(routing.NextVar(index))
                # distance matrix values are in meters (integers)
                route_distance_m += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            
            # Add final depot node at the end of the route
            route.append(manager.IndexToNode(int(index)))
 

            # Only store routes with deliveries
            if len(route) > 2:
                routes.append({
                    'vehicle_id': vehicle_id,
                    'route': route,
                    'distance_km': route_distance_m / 1000.0,  # convert back to km for reporting
                    'load': route_load,
                    'num_stops': len(route) - 2
                })

            total_distance_m += route_distance_m
            total_load += route_load
 
        solution_data = {

            'scenario': self.scenario,
            'routes': routes,
            'total_distance_km': total_distance_m / 1000.0,
            'total_load': total_load,
            'total_vehicles_used': len(routes),
            'vehicles_used': len(routes),
            'vehicles_available': data['num_vehicles']
        }
 
        return solution_data
    
    def calculate_costs(self, solution, vehicle_type = 'small_van'):
        '''
        Calculates the total operational costs based on the solution

        solution: dict returned by solve()

        returns:
        dict: Cost breakdown and total costs
        '''
        vehicle_data = self.fleet [
            self.fleet['vehicle_type'] == vehicle_type
        ].iloc[0]

        vehicles_used = solution['total_vehicles_used']
        total_distance = solution['total_distance_km']

        #Fixed Costs (per vehicle per day)
        fixed_cost = vehicles_used * vehicle_data['fixed_cost_per_day']   

        #variable Costs (per km)
        variable_cost = total_distance * vehicle_data['cost_per_km']
        
        #Driver Labor Costs (regular hours - 8 hours)
        driver_cost = vehicles_used * 8 * self.costs['driver_hourly_rate_regular']
        
        total_costs = fixed_cost + variable_cost + driver_cost

        return{
            'fixed_cost': round(fixed_cost,2),
            'variable_cost': round(variable_cost,2),
            'driver_cost': round(driver_cost,2),
            'total_costs': round(total_costs,2),
            'cost_per_package': round(total_costs/solution['total_load'],2) if solution['total_load']>0 else 0
        }
    
    def print_solution(self, solution, costs=None):
        # Prints solution details in a readable format

        print(f"\n{'='*70}")
        print(f"VRP Solution - {self.scenario.upper()} Scenario")
        print(f"{'='*70}\n")
        vehicles_used = solution.get('vehicles_used', solution.get('total_vehicles_used', 0))
        print(f"Vehicles Used: {vehicles_used} / {solution['vehicles_available']}")
        print(f"Total Distance: {solution['total_distance_km']:.2f} km")
        print(f"Total Packages Delivered: {solution['total_load']} packages")

        if vehicles_used > 0:
            print(f"Average Distance per Vehicle: {solution['total_distance_km']/vehicles_used:.2f} km")
        else:
            print("Average Distance per Vehicle: N/A (no vehicles used)")

        print (f"\n Route Details: PRINTING FIRST 5 ROUTES")

        for route in solution['routes'][:5]: #print first 5 routes
            print(f" Vehicle {route['vehicle_id']}:"
                  f" {route['num_stops']} stops,",
                  f" {route['distance_km']:.1f} km,",
                    f" Load: {route['load']} packages")
        if costs: 
            print(f"\nCost Breakdown:")
            print(f" Fixed Costs: ${costs['fixed_cost']:.2f}")
            print(f" Variable Costs (fuel): ${costs['variable_cost']:.2f}")
            print(f" Driver Costs (Labor): ${costs['driver_cost']:.2f}")
            print(f" Total Costs: ${costs['total_costs']:.2f}")
            print(f" Cost per Package: ${costs['cost_per_package']:.2f}")


if __name__ == "__main__":
    #Solve baseline scenario
    solver = VRPSolver(scenario='base')

    #Calculate minimum number of vehicles needed
    total_demand = sum(solver.demands)
    vehicle_capacity = 50  #Assumed capacity for small van
    min_vehicles = int(np.ceil(total_demand/vehicle_capacity)) #Ceiling division to ensure enough vehicles

print(f"\nCapacity Analysis:")
print(f" Total Demand: {total_demand} packages")
print(f" Vehicle Capacity: {vehicle_capacity} packages")
print(f" Minimum Vehicles Required: {min_vehicles} vehicles")

#SANITY CHECK:
demands = np.array(solver.demands)   # solver = VRPSolver(...)
print("\n N nodes:", solver.distance_matrix.shape[0])
print("N demands:", len(demands))
print("Max demand per node:", demands.max())
print("Any NaN in demands:", np.isnan(demands).any())
print("Min demand:", demands.min())
# nodes with demand > capacity
over = [(i, d) for i,d in enumerate(demands, start=0) if d > vehicle_capacity]
print("Nodes with demand > capacity (sample):", over[:10])
assert len(demands) == solver.distance_matrix.shape[0], "Demands length mismatch with distance matrix"





#Solve VRP 
solution = solver.solve(
    num_vehicles=min_vehicles,
    vehicle_capacity=vehicle_capacity,
    time_limit_seconds=120
)

if solution:
    #calculate costs
    costs = solver.calculate_costs(solution, vehicle_type='small_van')

    #Print Results 
    solver.print_solution(solution, costs)

    #Save solution to JSON
    solution['costs'] = costs 
    with open('results/baseline_solution.json', 'w') as f:
        json.dump(solution, f, indent=2, default=str)

        print("\nSolution saved to results/baseline_solution.json")

else: 
    print("\n Failed to find a solution for the baseline scenario.")

