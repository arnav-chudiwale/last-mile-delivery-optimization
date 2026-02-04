'''
Stress testing optimal solution under various scenarios
'''
import numpy as np 
import pandas as pd
import json 
import matplotlib.pyplot as plt
import seaborn as sns

np.random.seed(42)
sns.set_style("whitegrid")

class SensitivityAnalyzer: 
    def __init__(self):
        #Load optimal solution 
        with open('results/optimal_outsourcing.json', 'r') as f: 
            self.optimal = json.load(f)
        
        with open('results/capacity_crisis.json', 'r') as f: 
            crisis = json.load(f)
        
        with open('data/cost_parameters.json', 'r') as f: 
            self.costs = json.load(f)
        
        #Base Parameters 

        self.base_peak_demand = crisis['capacity_gap']['peak_demand']
        self.base_overtime_hours = self.optimal['optimal_overtime_hours']
        self.num_vehicles = 32
        self.packages_per_hour_per_vehicle = 6

        print("Sensitivity Analyzer Initialized")

        print(f" Base Peak Demand: {self.base_peak_demand} packages")
        print(f" Optimal Overtime : {self.base_overtime_hours} hours" )

    
    def test_demand_variance(self):
        '''
        Testing how solution performs with 20% demand variance
        '''

        print("\n SCENARIO 1: DEMAND VARIANCE")
        print("-"*50)

        #Test Range - -20% to +20% in 5% increments 
        variance_levels = np.arange(-0.2, 0.21, 0.05)

        results = []

        for variance in variance_levels:
            adjusted_demand = int(self.base_peak_demand * (1 + variance))  # variance on peak demand (3906 packages)

            #Using same overtime startegy
            overtime_capacity = (self.base_overtime_hours * self.num_vehicles * self.packages_per_hour_per_vehicle)
            baseline_capacity = 1600
            total_in_house = baseline_capacity + overtime_capacity

            #Calculating outsourcing needs 
            outsource_needed = max(0, adjusted_demand - total_in_house)

            #Costs
            baseline_ops = 10225.81
            overtime_cost = (self.base_overtime_hours * self.num_vehicles * self.costs['driver_hourly_rate_overtime'])
            outsource_cost = outsource_needed * self.costs['outsource_cost_per_package']

            total_cost = baseline_ops + overtime_cost + outsource_cost

            results.append({
                'variance': variance,
                'demand': adjusted_demand,
                'outsource_packages': outsource_needed, 
                'total_cost': total_cost,
                'cost_per_package': total_cost/adjusted_demand if adjusted_demand >0 else 0
            })

            print(f" Demand {variance:+.0%}: {adjusted_demand:,} packages | "
                  f"Outsource: {outsource_needed:,} -> Cost ${total_cost:,.2f}")
            
        df_results = pd.DataFrame(results)

        return df_results
    
    def test_3pl_capacity_constraint(self): 
        '''
        TEST: What if 3PL has Capacity Limitations?
        '''
        print("\n SCENARIO 2: 3PL CAPACITY CONSTRAINT")
        print("-"*50)

        base_outsource = self.optimal['packages_outsourced']

        #Test different 3PL capacity Limits -
        capacity_limits = [1500, 1800, 2000]

        results = []

        for limit in capacity_limits: 
            if limit >= base_outsource: 
                #Can meet demand 
                unserved = 0 
                late_penalty = 0 
                outsource_cost = base_outsource * self.costs['outsource_cost_per_package']
            else: 
                # 3PL hits capacity limits 
                unserved = base_outsource - limit
                late_penalty = unserved * self.costs['late_penalty_per_package']
                outsource_cost = limit * self.costs['outsource_cost_per_package']

            baseline_ops = 10225.81
            overtime_cost= self.optimal['overtime_cost']
            total_cost = baseline_ops + overtime_cost + outsource_cost + late_penalty

            results.append({
                '3pl_capacity_limit': limit,
                'outsourced': min(limit, base_outsource),
                'unserved': unserved,
                'late_penalty': late_penalty,
                'total_cost': total_cost
            })

            status = "OK" if unserved ==0 else f"{unserved} packages unserved"
            print(f" 3PL Limit {limit:,}: {status} -> Total Cost ${total_cost:,.2f}")

        df_results = pd.DataFrame(results)

        return df_results
    
    def test_overtime_feasibility(self):
        '''
        What if drivers can't work overtime?
        
        '''
        print("\n SCENARIO 3: OVERTIME CONSTRAINTS")
        print("-"*50)

        #tesing different overtime constraints
        overtime_limits = [0.5, 1, 1.5, 2] #hours    

        results = []

        for ot_limit in overtime_limits:
            #Capacity from allowed time
            ot_capacity = int(ot_limit * self.num_vehicles * self.packages_per_hour_per_vehicle)    
            total_in_house = 1600 + ot_capacity 

            #outsourcing needed
            outsource_needed = max(0, self.base_peak_demand - total_in_house)

            #Costs 
            baseline_ops = 10225.81
            overtime_cost = (ot_limit * self.num_vehicles * self.costs['driver_hourly_rate_overtime'])
            outsource_cost = outsource_needed * self.costs['outsource_cost_per_package']

            total_cost = baseline_ops + overtime_cost + outsource_cost

            results.append({
                'overtime_limit': ot_limit,
                'overtime_capacity': ot_capacity,
                'outsource_packages': outsource_needed,
                'overtime_cost': overtime_cost,
                'outsource_cost': outsource_cost,
                'total_cost': total_cost
            })

            print(f" Overtime {ot_limit}h: {outsource_needed:,} packages outsourced → ${total_cost:,.2f}")

        df_results = pd.DataFrame(results)

        return df_results
    
    def visualize_scenarios(self, demand_variance, threepl_capacity, overtime_feasibility):
        '''
        Visualizing all scenarios
        '''
        test_demand_variance = demand_variance
        test_3pl_capacity_constraint = threepl_capacity
        test_overtime_feasibility = overtime_feasibility

        fig, axes = plt.subplots(2,2, figsize = (12, 10))
        fig.suptitle("Sensitivity Analysis - Model Robustness", fontsize = 16, fontweight = 'bold')

        #Chart 1 = Demand Variance Impact 
        ax1 = axes[0,0]
        ax1.plot(test_demand_variance['variance']*100, test_demand_variance['total_cost'], 'bo-', linewidth =2, markersize= 8)
        ax1.axvline(0, color='red', linestyle = '--', alpha = 0.7, label = 'Base Case')
        ax1.fill_between(test_demand_variance['variance']*100, test_demand_variance['total_cost'], alpha = 0.2)
        ax1.set_xlabel("Demand Variance (%)", fontsize = 12)
        ax1.set_ylabel("Total Cost ($)", fontsize = 12)
        ax1.set_title("Impact of Demand Variance on Total Cost", fontsize = 13, fontweight = 'bold')
        ax1.legend()
        ax1.grid(True, alpha = 0.3)

        # Chart 2 = 3PL Capacity Constraints 
        ax2 = axes[0,1]
        colors = ['red' if u>0 else 'green' for u in test_3pl_capacity_constraint['unserved']]
        ax2.bar(range(len(test_3pl_capacity_constraint)), test_3pl_capacity_constraint['total_cost'], color = colors, alpha = 0.7, edgecolor = 'black')
        ax2.set_xticks(range(len(test_3pl_capacity_constraint)))
        ax2.set_xticklabels(test_3pl_capacity_constraint['3pl_capacity_limit'], fontsize = 10)
        ax2.set_xlabel("3PL Capacity Limit (packages)", fontsize = 12)
        ax2.set_ylabel("Total Cost ($)", fontsize = 12)
        ax2.set_title("Impact of 3PL Capacity Constraints on Total Cost", fontsize = 13, fontweight = 'bold')
        ax2.grid(True, alpha = 0.3, axis = 'y')

        # Chart 3 = Overtime vs Outsource Tradeoff 
        ax3 = axes [1,0]
        ax3.plot(test_overtime_feasibility['overtime_limit'], test_overtime_feasibility['overtime_cost'], 'bo-', label = 'Overtime Cost', linewidth =2, markersize=8)
        ax3.plot(test_overtime_feasibility['overtime_limit'], test_overtime_feasibility['outsource_cost'], 'go-', label = 'Outsource Cost', linewidth =2, markersize=8)
        ax3.plot(test_overtime_feasibility['overtime_limit'], test_overtime_feasibility['total_cost'], 'ro-', label = 'Total Cost', linewidth =2, markersize=8)
        ax3.axvline(2.0, color='green', linestyle = '--', alpha = 0.7, label = 'Optimal (2hr)')
        ax3.set_xlabel("Overtime Limit (hours)", fontsize = 12)
        ax3.set_ylabel("Cost ($)", fontsize = 12)
        ax3.set_title("Overtime vs Outsource Cost Tradeoff", fontsize = 13, fontweight = 'bold')
        ax3.legend()
        ax3.grid(True, alpha = 0.3)

        #Chart 4 = Cost per package across scenarios
        ax4 = axes [1,1]

        scenario_labels = [
            f"Demand \n{int(v*100):d}%" for v in test_demand_variance['variance']]
        cost_per_package = test_demand_variance['cost_per_package']

        bars = ax4.bar(range(len(scenario_labels)), cost_per_package, color = 'skyblue', alpha = 0.7, edgecolor = 'black')

        #Highlight base case
        base_idx = len(cost_per_package)//2
        bars[base_idx].set_color('orange')

        ax4.set_xticks(range(0, len(scenario_labels),2))
        ax4.set_xticklabels([scenario_labels[i] for i in range(0, len(scenario_labels),2)], fontsize = 10)
        ax4.set_ylabel("Cost per Package ($)", fontsize = 12)
        ax4.set_title("Cost Sensitivity Across Demand Scenarios", fontsize = 13, fontweight = 'bold')
        ax4.axhline(y=cost_per_package[base_idx], color='red', linestyle = '--', alpha = 0.7, label = 'Base Case')
        ax4.legend()
        ax4.grid(True, alpha = 0.3, axis = 'y')
        
        plt.tight_layout()
        plt.savefig('results/sensitivity_analysis.png', dpi = 300, bbox_inches = "tight")
        print(f"\n Sensitivity Analysis saved")
        plt.show()


if __name__=="__main__":
    analyzer = SensitivityAnalyzer()                        
    
    #Run all scenarios 
    demand_variance = analyzer.test_demand_variance()
    threepl_capacity = analyzer.test_3pl_capacity_constraint()
    overtime_feasibility = analyzer.test_overtime_feasibility()

    #Visualize 
    analyzer.visualize_scenarios(demand_variance, threepl_capacity, overtime_feasibility)

    #Save results 
    sensitivity_results = {
        'demand_variance': demand_variance.to_dict(orient = 'records'),
        '3pl_capacity_constraint': threepl_capacity.to_dict(orient = 'records'),
        'overtime_feasibility': overtime_feasibility.to_dict(orient = 'records')
    }
    with open('results/sensitivity_analysis_results.json', 'w') as f:
        json.dump(sensitivity_results, f, indent = 2)

    print(f"\n Sensitivity Analysis Results saved")

