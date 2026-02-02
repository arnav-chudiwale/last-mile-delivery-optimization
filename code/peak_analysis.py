'''
Peak Season Capacity Analysis
Demonstrates capacity crisis through theoritical calculations
'''

import pandas as pd
import numpy as np 
import json 

class PeakAnalyzer:
    def __init__(self):
        #loading baseline solution 

        with open ('results/baseline_solution.json', 'r') as f:
            self.baseline = json.load(f)

        #loading data 
        locations = pd.read_csv('data/delivery_locations.csv')

        with open('data/cost_parameters.json', 'r') as f:
            self.costs = json.load(f)

        #Key metrics for baseline scenario
        self.baseline_demand = self.baseline['total_load'] #1490 packages
        self.peak_demand = locations['peak_demand'].sum() 
        self.num_vehicles = 32 #Available Fleet 
        self.vehicle_capacity = 50 
        self.fleet_capacity = self.num_vehicles * self.vehicle_capacity #1600 packages

        print(f"Peak Season Analysis Initialized")
        print(f"="*70)
        print(f"Baseline Demand: {self.baseline_demand} packages")
        print(f"Peak Demand: {self.peak_demand} packages")
        print(f"Surge Factor: {self.peak_demand/self.baseline_demand:.2f}x")
        print(f"Fleet Capacity:{self.fleet_capacity} packages")
        print(f"="*70)

    def analyze_capacity_gap(self):
        #How much can fleet handle?
        max_servable = min(self.fleet_capacity, self.peak_demand)
        #Unserved Packages
        unserved = self.peak_demand - max_servable
        
        #Service level 
        service_level = (max_servable/self.peak_demand) * 100 
        
        return{
            'peak_demand': int(self.peak_demand),
            'fleet_capacity': int(self.fleet_capacity),
            'max_servable': int(max_servable),
            'unserved_packages': int(unserved),
            'service_level': round(service_level, 2),
            'service_failure': round(100 - service_level,2)
                    
                            }
    
    def calculate_do_nothing(self):
        #Cost of operating with existing fleet working normal hours

        gap = self.analyze_capacity_gap()

        #Baseline operations costs(for what we can deliver)
        baseline_ops_cost = self.baseline['costs']['total_costs']

        #Late delivery penalty for unserved packages
        late_penalty = gap['unserved_packages'] * self.costs['late_penalty_per_package']

        #Total costs of 'do nothing' strategy
        total_costs = baseline_ops_cost + late_penalty

        return{
            'strategy': 'Do Nothing (Base Fleet + Normal Hours)',
            'packages_served': gap['max_servable'],
            'packages_unserved': gap['unserved_packages'],
            'service_level': gap["service_level"],
            'baseline_operations_costs': baseline_ops_cost,
            'late_penalty_costs': late_penalty,
            'total_cost': round(total_costs, 2),
            'cost_per_package_attempted': round (total_costs/self.peak_demand,2)
        }
    
    def print_crisis_analysis(self):
        gap = self.analyze_capacity_gap()
        do_nothing = self.calculate_do_nothing()

        print(f"="*70)
        print(f'CAPACITY CRISIS - ANALYSIS')
        print(f"="*70)

        print(f'\n Demand vs Capacity')
        print(f"Peak Demand: {gap['peak_demand']:,} packages")
        print(f"Fleet Capacity: {gap['fleet_capacity']:,} packages")
        print(f"Vehicles Available: {self.num_vehicles}")
        print(f" Vehciles Needed (Theoretical): {int(np.ceil(gap['peak_demand']/self.vehicle_capacity))}")

        print(f"\n Capacity Shortfall")
        print(f"Unserved Packages: {gap['unserved_packages']:,}")
        print(f"Service Failure rate: {gap['service_failure']:.1f}")
        print(f"CRISIS: Can only serve {gap['service_level']:.1f}% of the peak demand")

        print(f"=*70")
        print("DO NOTHING SCENARIO - COST ANALYSIS")
        print(f"=*70")
        print(f"If we operate with existing fleet (with normal working hours) during peak:")
        print(f"Packages Delivered: {do_nothing['packages_served']:,}")
        print(f"Packages FAILED to be Delivered: {do_nothing['packages_unserved']:,}")
        print(f"Service level: {do_nothing['service_level']:.1f}%")

        print(f"\n Cost Breakdown")
        print(f"Baseline Operations: ${do_nothing['baseline_operations_costs']:,.2f}")
        print(f"Missed Delivery Penalities: ${do_nothing['late_penalty_costs']:,.2f}")
        print(f"TOTAL COST: ${do_nothing['total_cost']:,.2f}")

        print(f"\n Business Impact (5-day peak period):")
        five_day_cost = do_nothing['total_cost']*5
        five_day_unserved = do_nothing['packages_unserved']*5
        print(f"Total unserved:{five_day_unserved} packages") 
        print(f"Total Cost (with penalties): ${five_day_cost:,.2f}")
        print(f"Lost Revenue (estimated as $30/missed order): ${five_day_cost *30:,.2f}")

        #Saving data 
        crisis_data = {
            'capacity_gap' : gap,
            'do_nothing_scneario': do_nothing
        }

        with open('results/capacity_crisis.json', 'w') as f:
            json.dump(crisis_data, f, indent = 2)
        
        print(f"Crisis analysis saved to results/capacity_crisis.json")

        return crisis_data
    
if __name__ == "__main__":
    analyzer = PeakAnalyzer()
    analyzer.print_crisis_analysis()

    


