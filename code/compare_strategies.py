import pandas as pd 
import numpy as np 
import json 

class StrategyComparator: 
    def __init__(self):
        #Loading Base Solution 
        with open('results/baseline_solution.json', 'r') as f:
            self.baseline = json.load(f)
        
        #Loading Capacity crisis analysis 
        with open ('results/capacity_crisis.json', 'r') as f: 
            crisis = json.load(f)

        #Load cost parameters
        with open ('data/cost_parameters.json', 'r') as f:
            self.costs = json.load(f)
        
        # Extracting Key mentrics 
        self.baseline_demand = self.baseline['total_load']
        self.peak_demand = crisis['capacity_gap']['peak_demand']
        self.baseline_capacity = crisis['capacity_gap']['fleet_capacity']
        self.overflow  = crisis['capacity_gap']['unserved_packages']
        self.num_vehicles = 32

        # Storing 'DO NOTHING' BASELINE FOR COMPARISON 
        self.do_nothing_cost = crisis['do_nothing_scenario']['total_cost']

        print(f"STRATEGY COMPARISON SETUP:")
        print(f" Baseline Demand: {self.baseline_demand} packages")
        print(f" Peak Demand: {self.peak_demand} packages")
        print(f" Surge Factor: {self.peak_demand/self.baseline_demand:.2f}x")
        print(f" Fleet Capacity: {self.baseline_capacity} packages")
        print(f" Overflow to handle: {self.overflow} packages")
        print(f" DO NOTHING costs: ${self.do_nothing_cost:,.2f}")

    def strategy_1_overtime_only(self):
        '''
        Strategy 1 - Maximum Overtime (extended 10 hour shifts vs baseline 8 hour shifts)
        '''
        #overtime parameters
        extra_hours = 2 # 8h --> 10h shifts
        '''
            Productivity Estimate - 
            Baseline = 31 vehicles used, 1490 packages delivered, 8 hour shifts 
            Packages delivered/hour/driver = 1490 / (31*8) = ~6 packages/hour

            '''
        packages_per_hour_per_driver = 6 
        # how many more packages can be delivered with the same number of fleet but the drivers working for 2 more hours
        additional_capacity = extra_hours * self.num_vehicles * packages_per_hour_per_driver

        #Total capacity with overtime
        total_capacity = self.baseline_capacity + additional_capacity

        # Can we serve all demand with just overtime shifts?
        if total_capacity >= self.peak_demand:
            served = self.peak_demand
            unserved = 0
            service_level = 100

        else:
            served = int(total_capacity)
            unserved = self.peak_demand - served
            service_level = (served / self.peak_demand)*100

        #costs 
        baseline_cost = self.baseline['costs']['total_costs']
        overtime_cost = (extra_hours*self.num_vehicles*self.costs['driver_hourly_rate_overtime'])
        late_penalty = unserved * self.costs['late_penalty_per_package']

        additional_cost = overtime_cost + late_penalty
        total_cost = baseline_cost + additional_cost

        return{
            'strategy':'Overtime Only (extended 10 hour shifts)',
            'overtime_hours': extra_hours,
            'capacity_added': additional_capacity,
            'total_capacity': total_capacity,
            'packages_served': served,
            'packages_unserved': unserved,
            'service_level': round(service_level,2),
            'baseline_cost': baseline_cost,
            'overtime_cost': round(overtime_cost, 2),
            'late_penalty_cost': round(late_penalty,2),
            'additional_cost': round(additional_cost, 2),
            'total_cost': round(total_cost,2),
            'cost_per_packages': round(total_cost/self.peak_demand,2),
            'feasible': service_level == 100
        }
    
    def startegy_2_outsource_all_overflow(self):
        '''
        Strategy 2 - Outsource all overflow to 3PL 
        '''
        # Using baseline fleet for what it can handle
        in_house_packages = self.baseline_capacity

        #All overflow goes to 3PL 
        outsourced_packages = self.overflow

        #Costs =
        baseline_cost = self.baseline['costs']['total_costs']
        outsource_cost = outsourced_packages * self.costs['outsource_cost_per_package']

        additional_cost = outsource_cost
        total_cost = baseline_cost + additional_cost

        return{
            'strategy':'Outsource All overflow',
            'in_house_packages': in_house_packages,
            'outsourced_packages': outsourced_packages,
            'outsource_percentage': round((outsourced_packages/self.peak_demand)*100,2),
            'packages_served': self.peak_demand,
            #'packages_unserved': unserved,
            'service_level': 100,
            'baseline_cost': baseline_cost,
            'outsource_cost': round(outsource_cost, 2),
            #'late_penalty_cost': round(late_penalty,2),
            'additional_cost': round(additional_cost, 2),
            'total_cost': round(total_cost,2),
            'cost_per_packages': round(total_cost/self.peak_demand,2),
            'feasible': True
        }
    
    def strategy_3_hybrid(self, extra_hours = 1.6):
        '''
        Strategy 3: Hybrid approach
        overtime + selective outsourcing

        args - 
        extra_hours = average overtime per driver (0-2)
        '''

        # Productivity
        packages_per_hour_per_driver = 6 

        #Capacity from overtime
        overtime_capacity = int(extra_hours * self.num_vehicles * packages_per_hour_per_driver)

        #Total in-house capacity
        in_house_total = self.baseline_capacity + overtime_capacity

        #Remaining for outsourcing
        outsourced = max(0, self.peak_demand - in_house_total)

        #Costs 
        baseline_cost = self.baseline['costs']['total_costs']
        overtime_cost = (extra_hours * self.num_vehicles * self.costs['driver_hourly_rate_overtime'])
        outsource_cost = outsourced * self.costs['outsource_cost_per_package']

        additional_cost = overtime_cost + outsource_cost
        total_cost = baseline_cost + additional_cost

        return{
            'strategy':f"Hybrid (Overtime:{extra_hours} hours + Outsource)",
            'overtime_hours': extra_hours,
            'overtime_capacity': overtime_capacity,
            'in_house_packages': in_house_total,
            'outsourced_packages': outsourced,
            'outsource_percentage': round((outsourced/self.peak_demand)*100,2),
            'packages_served': self.peak_demand,
            'service_level': 100.0,
            'baseline_cost': baseline_cost,
            'outsource_cost': round(outsource_cost, 2),
            #'late_penalty_cost': round(late_penalty,2),
            'additional_cost': round(additional_cost, 2),
            'total_cost': round(total_cost,2),
            'cost_per_packages': round(total_cost/self.peak_demand,2),
            'feasible' : True
        }
    
    def compare_all(self):
        '''
        Run all strategies and compare 
        '''

        strategies = {
            'overtime': self.strategy_1_overtime_only(),
            'outsource': self.startegy_2_outsource_all_overflow(),
            'hybrid_2_hours_extra': self.strategy_3_hybrid(2.0),
            'hybrid_1.6_hours_extra': self.strategy_3_hybrid(1.6),
            'hybrid_1.2_hours_extra': self.strategy_3_hybrid(1.2),
            'hybrid_0.8_hours_extra': self.strategy_3_hybrid(0.8),
        }

        return strategies
    
    def print_comparisons(self, strategies):
        print(f"="*70)
        print(f"STRATEGY COMPARISON - PEAK SEASON")
        print(f"="*70)

        #Creating DataFrame for comparison
        rows = []
        for name, s in strategies.items():
            rows.append({
                'Strategy': s['strategy'],
                'Service_Level': f"{s['service_level']:.1f}%",
                'Total Cost': f"${s['total_cost']:,.0f}",
                'Cost per package': f"${s['cost_per_packages']:.2f}",
                'Outsource percentage of peak demand': f"{s.get('outsource_percentage',0):.1f}%",
                'Feasible': 'YES' if s['feasible'] else 'NO'
            })

        df = pd.DataFrame(rows)
        print(df.to_string(index=False))

        #Detailed Breakdown 
        print(f"="*70)
        print("DETAILED COST BREAKDOWN")
        print(f"="*70)
        for name, s in strategies.items():
            print(f'\n{s['strategy']}:')
            print(f" Service Level: {s['service_level']:.1f}%")
            print(f" Baseline Operations: ${s['baseline_cost']:,.2f}")

            if 'overtime_cost' in s and s['overtime_cost']>0:
                print(f" Overtime Cost: ${s['overtime_cost']:,.2f}")
            if 'outsource_cost' in s and s['outsource_cost']>0:
                print(f" Outsource Cost: ${s['outsource_cost']:,.2f}")
            if 'late_penalty_cost' in s and s['late_penalty_cost']>0:
                print(f" Late Penalty Cost: ${s['late_penalty_cost']:,.2f}")

            print(f" Additional Cost: ${s['additional_cost']:,.2f}")
            print(f" Total Cost: ${s['total_cost']:,.2f}")

            if 'outsourced_packages' in s and s['outsourced_packages']>0:
                print(f" Packages Outsourced: {s['outsourced_packages']}"
                      f"({s['outsource_percentage']:.1f}%)")
                
        # Recommendation
        print(f"="*70)
        print(f"\n RECOMMENDATION")
        print(f"="*70)

        #Finding cheapest feasible strategy
        feasible = {k: v for k, v in strategies.items() if v['feasible']}

        if feasible:
            best_key = min(feasible, key = lambda k: feasible[k]['total_cost'])

            best = feasible[best_key]

            print(f" RECOMMENDED: {best['strategy']}")
            print(f" TOTAL COST: ${best['total_cost']:,.2f}")
            print(f" Cost per package: ${best['cost_per_packages']:.2f}")

            if 'extra_hours' in best: 
                print(f" Overtime: {best['extra_hours']:.1f} hours per driver")
            if 'outsource_percentage' in best:
                print(f" Outsource: {best['outsource_percentage']:.1f} of total volume")
                    
            #Savings and worst feasible
            worst_key = max(feasible, key = lambda k: feasible[k]['total_cost'])
            worst = feasible[worst_key]
            savings = worst['total_cost'] - best['total_cost']

            print(f"\n Savings vs {worst['strategy']}:"
                    f"${savings:,.2f} ({savings/worst['total_cost']*100:.1f}%)")
                
            #Comparing to DO NOTHING scenario
            do_nothing_cost = self.baseline['costs']['total_costs'] + (self.overflow * self.costs['late_penalty_per_package'])
            savings_vs_nothing = do_nothing_cost - best['total_cost']

            print(f" Savings vs Doing Nothing: ${savings_vs_nothing:,.2f}")

if __name__=="__main__":
    comparator = StrategyComparator()
    strategies = comparator.compare_all()
    comparator.print_comparisons(strategies)

#Saving Results
with open("results/strategy_comparison.json", 'w') as f:
    json.dump(strategies,f, indent=2)

print(f"\n Comparison saved to results/strategy_comparison.json")

