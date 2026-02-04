import pandas as pd
import numpy as np
import json 

class DynamicRoutingManager:
    def __init__(self):
        #Loading baseline solution and costs
        with open('results/baseline_solution.json', 'r') as f: 
            self.baseline = json.load(f)

        with open('data/cost_parameters.json', 'r') as f:
            self.costs = json.load(f)

        #Load demand snapshots
        with open('results/demand_snapshots.json', 'r') as f:
            self.snapshots = json.load(f)

        #Fleet Parameters 
        self.num_vehicles = 32
        self.vehicle_capacity = 50 
        self.packages_per_hour_per_driver = 6 

        print(f" Dynamic Routing Manager Initialized")

        print(f" Fleet: {self.num_vehicles} vehicles")
        print(f" Vehicle Capacity: {self.vehicle_capacity} packages")

    def calculate_capacity_at_time(self, current_hour):
        '''
            Calculates Available Capacity at given time

            Assumptions:
            - Vehicle dispatched at 8 AM
            - Each route takes ~ 4 hours on average for a round trip 
            - Vehicles return and can be reused
            '''  
                 
        if current_hour <= 8:
                #At 8 AM and before: full fleet available to dispatch first batch
            return self.num_vehicles * self.vehicle_capacity
        elif current_hour < 12: 
                # After 8 AM until noon: First batch still out -- ALL in house vehicles busy 
            return 0 
        elif current_hour < 14:
                # First batch returning (12 PM onwards)
                # Approx 50% vehicles available for re-dispatch -- ASSUMPTION!!
            available_vehicles = self.num_vehicles * 0.5 
            return int(available_vehicles * self.vehicle_capacity)
        else: 
                #All vehicles returned
                #Can do second full round
            return self.num_vehicles * self.vehicle_capacity
        
    def make_dispatch_decision(self, time_hour, known_demand):
        '''
        Decision - Dispatch in-house fleet or outsource to 3PL 

        LOGIC - 
        - if known demand <= available capacity : use in-house capacity
        - if known demand > available capacity : use-in house + outsource excess to 3PL 
        '''

        available_capacity = self.calculate_capacity_at_time(time_hour)

        if known_demand <= available_capacity:
            #Can handle with in-house 
            in_house = known_demand
            outsource = 0
        
        else:
            # Need to outsource excess
            in_house = available_capacity
            outsource = known_demand - available_capacity

        return {
            'time': time_hour,
            'known_demand': known_demand,
            'available_capacity': available_capacity,
            'dispatched_in_house': in_house,
            'outsourced': outsource
        }
    
    def simulate_day(self):
        '''
        Simulating dynamic decision making throughout the day
        '''    
        print(f" DYNAMIC ROUTING SIMULATION")
        print(f"="*70)

        decisions = []
        cumulative_in_house = 0
        cumulative_outsource = 0

        for time_label in ['8:00', '10:00', '12:00', '14:00']:
            snap = self.snapshots[time_label]
            time_hour = snap['time']
            known_demand = snap['total_packages']
            
            decision = self.make_dispatch_decision(time_hour, known_demand)
            new_demand = known_demand - cumulative_in_house - cumulative_outsource           
            
            if new_demand > 0: 
                new_decision = self.make_dispatch_decision(time_hour, new_demand)
                cumulative_in_house += new_decision['dispatched_in_house']
                cumulative_outsource += new_decision['outsourced']
                
                decisions.append({
                    'time': time_label,
                    'new_orders': new_demand,
                    'decision': new_decision,
                    'cumulative_in_house': cumulative_in_house,
                    'cumulative_outsource': cumulative_outsource
                })
                
                print(f" Time: {time_label}")
                print(f" New Orders: {new_demand}")
                print(f" Available Capacity: {new_decision['available_capacity']}")
                print(f" Decision: Dispatch {new_decision['dispatched_in_house']} in-house, Outsource {new_decision['outsourced']}")
                print(f" Cumulative In-House: {cumulative_in_house}, Cumulative Outsourced: {cumulative_outsource}")
                print(f"-"*50)
        
        final_summary = self.calculate_costs(cumulative_in_house, cumulative_outsource)
        
        return {
            'decisions': decisions,
            'final_summary': final_summary
        }
    
    def calculate_costs(self, in_house_packages, outsourced_packages):
        #Assume in-house uses same baseline efficiency

        baseline_cost_per_package = self.baseline['costs']['total_costs']/self.baseline['total_load']
        in_house_cost = in_house_packages * baseline_cost_per_package

        #Outsource Cost 
        outsource_cost = outsourced_packages * self.costs['outsource_cost_per_package']

        #Total 
        total_cost = in_house_cost + outsource_cost

        return{
            'in_house_packages': in_house_packages,
            'outsourced_packages': outsourced_packages,
            'in_house_cost': round(in_house_cost, 2),
            'outsource_cost': round(outsource_cost, 2),
            'total_cost': round(total_cost,2),
            'cost_per_package': round(total_cost/(in_house_packages + outsourced_packages),2)
        }
    
    def compare_to_static(self, dynamic_result): 
        '''
        COMPARING DYNAMIC APPROACH TO STATIC APPROACH 
        '''
        #Load static solution 
        with open('results/optimal_outsourcing.json', 'r') as f:
            static = json.load(f)

        # Baseline cost (reference point)
        baseline_cost = self.baseline['costs']['total_costs']
        baseline_packages = self.baseline['total_load']
        
        print(f" STATIC vs DYNAMIC COMPARISON")
        print(f"="*70)

        print(f"\n BASELINE (no outsourcing)")
        print(f" In-House Packages: {baseline_packages} packages")
        print(f" Total Cost: ${baseline_cost:,.2f}")
        
        print(f"\n STATIC SCENARIO (with 2 hr overtime)")
        static_in_house = 1600 + 383
        static_total_cost = baseline_cost + static['total_additional_cost']
        print(f" In-House Packages: {static_in_house} packages")
        print(f" Outsourced Packages: {static['packages_outsourced']} packages")
        print(f" Total Cost: ${static_total_cost:,.2f}")
        print(f" Additional Cost (over baseline): ${static['total_additional_cost']:,.2f}")

        dynamic_summary = dynamic_result['final_summary']
        dynamic_total_cost = dynamic_summary['total_cost']
        dynamic_additional_cost = dynamic_total_cost - baseline_cost
        
        print(f"\n DYNAMIC SCENARIO (with vehicle reuse)")
        print(f" In-House Packages: {dynamic_summary['in_house_packages']} packages")
        print(f" Outsourced Packages: {dynamic_summary['outsourced_packages']} packages")
        print(f" Total Cost: ${dynamic_total_cost:,.2f}")
        print(f" Additional Cost (over baseline): ${dynamic_additional_cost:,.2f}")

        #INSIGHTS 
        print(f"\n COMPARISON:")
        print(f" - Static additional cost: ${static['total_additional_cost']:,.2f}")
        print(f" - Dynamic additional cost: ${dynamic_additional_cost:,.2f}")
        cost_savings = static['total_additional_cost'] - dynamic_additional_cost
        print(f" - Savings with dynamic: ${cost_savings:,.2f}")
        
        print(f"\n KEY INSIGHTS: ")
        outsourcing_reduction = static['packages_outsourced'] - dynamic_summary['outsourced_packages']
        outsourcing_reduction_pct = (outsourcing_reduction / static['packages_outsourced']) * 100
        throughput_increase = ((dynamic_summary['in_house_packages'] - (1600 + 383)) / (1600 + 383)) * 100
        
        print(f"\n 1. Vehicle Reuse Multiplies Capacity:")
        print(f"    - Same 32-vehicle fleet handles {dynamic_summary['in_house_packages']:,} packages (vs {1983:,} static)")
        print(f"    - {throughput_increase:.1f}% throughput increase through two dispatch waves")
        
        print(f"\n 2. Outsourcing Reduced 54% but Still Necessary:")
        print(f"    - Outsourcing drops by {outsourcing_reduction:,} packages ({outsourcing_reduction_pct:.0f}% reduction)")
        print(f"    - However, {dynamic_summary['outsourced_packages']:,} packages still need 3PL (23% of peak demand)")
        print(f"    - Bottleneck: All vehicles in-transit 8 AM-12 PM means zero re-dispatch capacity at 10 AM")
        
        print(f"\n 3. Time-Based Dispatch Windows Are Critical:")
        print(f"    - 8 AM: Full capacity (1,600 packages) → all 668 orders handled in-house")
        print(f"    - 10 AM: Zero capacity → forced to outsource all 793 new orders")
        print(f"    - 12 PM: 50% fleet return (800 capacity) → handle 800 in-house, outsource 99")
        print(f"    - 2 PM: Full reuse (1,600 capacity) → all 677 orders handled in-house")
        
        print(f"\n 4. Financial Impact Justifies Complexity:")
        print(f"    - Cost savings: ${cost_savings:,.2f} ({(cost_savings/static['total_additional_cost']*100):.1f}% reduction in peak-day costs)")
        print(f"    - Cost per package: ${dynamic_summary['cost_per_package']:.2f} (dynamic) vs ${(static['total_additional_cost'] + baseline_cost)/(static['packages_outsourced'] + 1983):.2f} (static)")
        
        print(f"\n 5. Critical Trade-offs:")
        print(f"    ✓ Benefit: {throughput_increase:.0f}% capacity gain; {(cost_savings/static['total_additional_cost']*100):.0f}% cost reduction")
        print(f"    ✗ Cost: Real-time tracking, multi-wave coordination, backlog management required")
        print(f"    ✗ Risk: Single route delay cascades to all downstream decisions")
        print(f"    ✗ Dependency: Must maintain 3PL partnership for residual {dynamic_summary['outsourced_packages']:,} packages")


if __name__=="__main__":
    manager = DynamicRoutingManager()
    result = manager.simulate_day()

    #Compare to static
    manager.compare_to_static(result)

    #Saving results 
    with open('results/dynamic_routing_simulation.json', 'w') as f: 
        json.dump(result, f, indent = 2)

    print(f"\n Dynamic simulation saved")

