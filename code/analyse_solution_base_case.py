'''
Creating 4 charts - 
1) Distance per vehicle (bar chart)
2) Load per vehicle (bar chart with capacity line)
3) stops per vehicle (bar chart)
4) cost breakdown (pie chart)

'''
import pandas as pd 
import json 
#import matplotlib
#matplotlib.use('Agg') #Use non-interactive backend
import matplotlib.pyplot as plt
#import seaborn as sns 
import numpy as np 

#Setting style 
#sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14,10)

def analyze_solution(solution_file, output_file = 'results/baseline_analysis.png'):
    '''
    Creating dashboard
    solution_file = Path to solution JSON 
    output_file = Where to save chart 
    '''
    print("Generating analysis chart...")

    #Lazy import seaborn to avoid importing scipy/seaborn at module import time
    try:
        import seaborn as sns
        sns.set_style("whitegrid")
    except Exception:
        import warnings
        warnings.warn("seaborn not available or failed to import")
        plt.style.use('seaborn-whitegrid')

    #Load Solution
    with open(solution_file, 'r') as f:
        solution = json.load(f)

    #Convert routes to Dataframe 
    routes_df = pd.DataFrame(solution['routes'])

    #create figure with subplots 
    fig, axes = plt.subplots(2,2,figsize = (14,10))
    fig.suptitle(
        f"VRP Analysis - {solution['scenario'].upper()} Scenario",
        fontsize = 16, 
        fontweight = 'bold'
    )

    #Chart 1 - Distance covered per vehicle 
    ax1 = axes [0,0]
    bars1 = ax1.bar(
        routes_df['vehicle_id'],
        routes_df['distance_km'],
        color = 'steelblue',
        edgecolor = 'black',
        linewidth = 0.5
    )

    ax1.axhline(
        y = routes_df['distance_km'].mean(),
        color = 'red',
        linestyle = '--',
        linewidth = 2,
        label = f"Average: {routes_df['distance_km'].mean():.1f} km"
    )

    ax1.set_xlabel('Vehicle ID', fontsize = 12)
    ax1.set_ylabel('Distance (km)', fontsize = 12)
    ax1.set_title('Distance Travelled per Vehicle', fontsize = 13, fontweight = 'bold')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)

    #Chart 2 - Load per Vehicle 
    ax2 = axes [0,1]
    bars2 = ax2.bar(
        routes_df['vehicle_id'],
        routes_df['load'],
        color = 'forestgreen',
        edgecolor = 'black',
        linewidth = 0.5
    )

    ax2.axhline(
        y = 50,
        color = 'red',
        linestyle = '--',
        linewidth = 2,
        label = f"Capacity: 50 packages per vehicle"
    )

    ax2.set_xlabel('Vehicle ID', fontsize = 12)
    ax2.set_ylabel('Packages Delivered', fontsize = 12)
    ax2.set_title('Load per Vehicle', fontsize = 13, fontweight = 'bold')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)

    #Color bars by utilization 
    utilization = routes_df['load']/50*100
    for i, (bar, util) in enumerate (zip(bars2, utilization)):
        if util > 95:
            bar.set_color('darkred')
        elif util > 85: 
            bar.set_color('orange')

    #Chart 3 - Stops per Vehicle 
    ax3 = axes [1,0]
    bars3 = ax3.bar(
        routes_df['vehicle_id'],
        routes_df['num_stops'],
        color = 'mediumorchid',
        edgecolor = 'black',
        linewidth = 0.5
    )

    ax3.axhline(
        y = routes_df['num_stops'].mean(),
        color = 'red',
        linestyle = '--',
        linewidth = 2,
        label = f"Average: {routes_df['num_stops'].mean():.1f} stops"
    )

    ax3.set_xlabel('Vehicle ID', fontsize = 12)
    ax3.set_ylabel('No. of Stops', fontsize = 12)
    ax3.set_title('Delivery Stops per Vehicle', fontsize = 13, fontweight = 'bold')
    ax3.legend()
    ax3.grid(axis='y', alpha=0.3)

    #Chart 4 - Cost breakdown
    ax4 = axes [1,1]
    costs = solution['costs']
    cost_labels = ['Fixed\n(Vehicles)', 'Variable\n(Fuel)', 'Labor\n(Drivers)']
    # Support both singular and plural keys coming from different solution formats
    def _to_float(x):
        try:
            return float(x)
        except Exception:
            return 0.0

    fixed = _to_float(costs.get('fixed_cost', costs.get('fixed_costs', 0)))
    variable = _to_float(costs.get('variable_cost', costs.get('variable_costs', 0)))
    driver = _to_float(costs.get('driver_cost', costs.get('driver_costs', 0)))
    cost_values = [fixed, variable, driver]

    colors_pie = ['#ff9999', '#66b3ff', '#99ff99']

    wedges, texts, autotexts = ax4.pie(
        cost_values,
        labels=cost_labels,
        autopct = '%1.1f%%',
        startangle = 90,
        colors = colors_pie,
        textprops = {'fontsize':11}
    )

    #Make percentage text bolder

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(11)

    ax4.set_title("Cost Breakdown", fontsize = 13, fontweight = 'bold')

    #Adding total cost as text 

    total_cost = costs.get('total_cost', costs.get('total_costs', fixed + variable + driver))
    ax4.text(
        0, -1.3,
        f"Total Cost: ${total_cost:,.2f}\nCost per Package: ${costs['cost_per_package']:.2f}",
        ha = 'center',
        fontsize = 11,
        bbox = dict(boxstyle = 'round', facecolor = 'wheat', alpha = 0.5)
    )    

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches = 'tight')
    print(f"Analysis saved to {output_file}")

    #Printing Statistics 
    print(f"\n{'='*70}")
    print("ROUTE STATISTICS")
    print(f"\n{'='*70}")
    print(f"Average distance per route: {routes_df['distance_km'].mean():.2f} km")
    print(f"Standard Deviation Distance: {routes_df['distance_km'].std():.2f} km")
    print(f"Average load per vehicle: {routes_df['load'].mean():.2f} packages")
    print(f"Average Utilization: {(routes_df['load'].mean()/50*100):.1f}%")
    print(f"Average stops per route: {routes_df['num_stops'].mean():.2f}")
    print(f"Total Cost: ${total_cost:,.2f}")
    print(f"Cost per Package: ${costs['cost_per_package']:.2f}")

    #Checking for imbalances - 
    if routes_df['distance_km'].std() > routes_df['distance_km'].mean()*0.3:
        print("\n High Distance Variance - routes are imbalanced")

    if routes_df['load'].max() == 50:
        print(f" {(routes_df['load'] == 50).sum()} vehicles at max capacity")

if __name__=='__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Analyse VRP solution and save charts')
    parser.add_argument('--show', action='store_true', help='Display charts with plt.show() (blocks execution)')
    args = parser.parse_args()

    analyze_solution('results/baseline_solution.json')
    if args.show:
        plt.show()
    else:
        plt.close('all')

