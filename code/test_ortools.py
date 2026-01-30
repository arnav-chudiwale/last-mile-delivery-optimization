from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

#5 location test
distance_matrix = [
    [0, 10, 15, 20 ,25],
    [10, 0, 35, 25, 30],
    [15, 35, 0, 30, 20],
    [20, 25, 30, 0, 15],
    [25, 30, 20, 15, 0]
]

manager = pywrapcp.RoutingIndexManager(len(distance_matrix),1,0)
routing = pywrapcp.RoutingModel(manager)

def distance_callback(from_index, to_index):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)

    return distance_matrix[from_node][to_node]

transit_callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

search_parameters = pywrapcp.DefaultRoutingSearchParameters()

solution = routing.SolveWithParameters(search_parameters)

if solution:
    print("Success! OR tools are working")
    print(f"Total distance:{solution.ObjectiveValue()}")
