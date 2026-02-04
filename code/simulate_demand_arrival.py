import pandas as pd 
import numpy as np 
import json 
import matplotlib.pyplot as plt
import seaborn as sns 

np.random.seed(42)
sns.set_style("whitegrid")

class DemandSimulator:
    def __init__(self):
        #Load peak demand data
        self.locations = pd.read_csv('data/delivery_locations.csv')
        self.total_peak_demand = self.locations['peak_demand'].sum()

        #Taking peak and breaking down into arrival at different time slots 

        print(f" Demand Simulator initialized")
        print(f" Total Peak Demand: {self.total_peak_demand} packages")

    def generate_arrival_pattern(self):
        '''
        Pattern based on e-commerce data: 
        - Early morning (6-9 AM): 25% of orders (overnight accumulation)
        - Mid-Mornning (9-12 PM): 35% of orders (peak shopping) 
        - Afternoon (12-3 PM): 25% of orders
        - Late (3-6 PM): 15% of orders (last minute)
        '''       

        time_windows = [
            {'period': '6-9 AM', 'start':6, 'end':9, 'percentage':0.25},
            {'period': '9-12 PM', 'start':9, 'end':12, 'percentage':0.35},
            {'period': '12-3 PM', 'start':12, 'end':15, 'percentage':0.25},
            {'period': '3-6 PM', 'start':15, 'end':18, 'percentage':0.15},
        ]    

        #Assigning each package to a time window 
        packages =[]
        for idx, row in self.locations.iterrows():
            location_demand = row['peak_demand']

            for pkg in range(location_demand):
                #Randomly assign to time windows based on probabilities
                window_choice = np.random.choice(
                    len(time_windows), #number of time windows to randomly choose from
                    p=[w['percentage'] for w in time_windows] #randomly choosing probabilities based on percentages of time windows
                )

                window = time_windows[window_choice]
                #Random arrival time within the chosen window
                arrival_hour = np.random.uniform(window['start'], window['end']) #uniform choice within the time window

                packages.append({
                    'package_id':len(packages),
                    'location_id': idx,
                    'latitude': row['latitude'],
                    'longitude': row['longitude'],
                    'arrival_hour': arrival_hour,
                    'arrival_period': window['period']
                })
        df_arrivals = pd.DataFrame(packages)
        df_arrivals = df_arrivals.sort_values('arrival_hour').reset_index(drop=True)

        print(f' Generated {len(df_arrivals)} package arrivals')

        return df_arrivals
    
    def create_snapshots(self, df_arrivals):
        '''
        Creating demand snapshots at key decision points
        '''
        decision_times = [8, 10, 12, 14] # 8 AM, 10 AM, 12 PM, 2 PM

        snapshots = {}

        for time in decision_times:
            #Packages known up to this time
            known_packages = df_arrivals[df_arrivals['arrival_hour'] <= time]

            #Aggregate by location - location id 
            location_demand = known_packages.groupby('location_id').size()

            snapshots[f"{time}:00"] = {
                'time': time,
                'total_packages': len(known_packages),
                'locations_with_demand': len(location_demand),
                'demand_by_location': location_demand.to_dict() 
            }
            
            # Note: cumulative packages known up to this time
            print(f" Snapshot at {time}:00 - {len(known_packages)} packages known (cumulative)")

        return snapshots

    def compute_interval_counts(self, df_arrivals):
        """
        Compute new orders per decision interval to complement cumulative snapshots.
        Returns a list of (label, count) and the total.
        """
        intervals = [
            ("Before 8 AM", 0, 8),
            ("8-10 AM", 8, 10),
            ("10-12 PM", 10, 12),
            ("12-2 PM", 12, 14),
            ("After 2 PM", 14, 18),
        ]

        interval_counts = []
        for label, start, end in intervals:
            count = len(df_arrivals[(df_arrivals['arrival_hour'] >= start) & (df_arrivals['arrival_hour'] < end)])
            interval_counts.append((label, count))

        total = sum(c for _, c in interval_counts)
        return interval_counts, total
    
    def visualize_arrival_pattern(self, df_arrivals):
        fig, axes = plt.subplots(2,2, figsize = (12, 10))

        fig.suptitle("Peak Day Demand Arrival Pattern", fontsize = 16, fontweight = 'bold')

        #Chart 1 = Cumulative arrivals over time
        ax1 = axes[0,0]

        hours = np.arange(6, 18, 0.5)
        cumulative = [(len(df_arrivals[df_arrivals['arrival_hour'] <= h])) for h in hours]

        ax1.plot(hours, cumulative, 'b-', linewidth = 2.5)
        ax1.fill_between(hours, cumulative, alpha = 0.3)

        #Mark Decision points
        decision_times = [8, 10, 12, 14]

        for dt in decision_times:
            known = len(df_arrivals[df_arrivals['arrival_hour']<=dt])
            ax1.axvline(dt, color = 'red', linestyle = '--', alpha = 0.7) 
            ax1.text(dt, known + 100, f"{dt}:00\n{known} packages", ha = 'center', fontsize = 9,
                     bbox = dict(boxstyle = 'round', facecolor = 'wheat', alpha = 0.8))
        
        ax1.set_xlabel("Hour of the Day", fontsize = 12)
        ax1.set_ylabel("Cumulative Packages", fontsize = 12)
        ax1.set_title("Cumulative Order Arrivals", fontsize = 13, fontweight = 'bold')

        ax1.grid(True, alpha = 0.3)

        
        #Chart 2 = Arrivals/Hour Histogram 
        ax2 = axes[0,1]
        ax2.hist(df_arrivals['arrival_hour'], bins = 24, color = 'steelblue', edgecolor = 'black', alpha = 0.7)
        ax2.set_xlabel("Hour of the Day", fontsize = 12)
        ax2.set_ylabel("Number of Packages", fontsize = 12)
        ax2.set_title("Order Arrival Distribution", fontsize = 13, fontweight = 'bold')
        ax2.grid(True, alpha = 0.3)

        #Chart 3 = Arrivals by period Pie Chart 
        ax3 = axes[1,0]
        period_counts = df_arrivals['arrival_period'].value_counts().sort_index()
        
        colors_pie = ['skyblue', 'lightgreen', 'lightcoral', 'gold']
        wedges, texts, autotexts = ax3.pie(
            period_counts.values,
            labels = period_counts.index,
            autopct = '%1.1f%%',
            colors = colors_pie
        )

        for autotext in autotexts: 
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax3.set_title("Orders by Time Period", fontsize = 13, fontweight = 'bold')

        #Chart 4 = New orders per decision interval
        ax4 = axes[1,1]

        intervals = [
            ('Before 8 AM', 0, 8),
            ('8-10 AM', 8, 10),
            ('10-12 PM', 10, 12),
            ('12-2 PM', 12, 14),
            ('After 2 PM', 14, 18)

        ]

        interval_counts = []
        interval_labels = []

        for label, start, end, in intervals: 
            count = len(df_arrivals[(df_arrivals['arrival_hour'] >= start) & (df_arrivals['arrival_hour'] < end)])

            interval_counts.append(count)

            interval_labels.append(f"{label}\n{count}")
            
        bars = ax4.bar(range(len(interval_labels)), interval_counts, color = 'lightcoral', edgecolor = 'black', alpha = 0.7)
        
        ax4.set_xticks(range(len(interval_labels)))
        ax4.set_xticklabels(interval_labels, fontsize=10)
        ax4.set_ylabel("New Orders", fontsize = 12)
        ax4.set_title("New Order by Decision Interval", fontsize = 13, fontweight = 'bold')
        ax4.grid(True, alpha = 0.3, axis = 'y')

        plt.tight_layout()
        plt.savefig('results/demand_arrival_pattern.png', dpi = 300, bbox_inches = "tight")

        plt.show()
    
    def save_snapshots(self, snapshots):
        with open('results/demand_snapshots.json', 'w') as f:
            json.dump(snapshots, f, indent = 2)

        print(f" Snapshots saved")

        
if __name__=="__main__":
    simulator = DemandSimulator()

    # Generate Arrival Patterns 
    df_arrivals = simulator.generate_arrival_pattern()                    

    #Create decision point snapshots
    snapshots = simulator.create_snapshots(df_arrivals)

    #Visualise
    simulator.visualize_arrival_pattern(df_arrivals)

    #Save for late use 
    df_arrivals.to_csv('results/package_arrivals.csv', index = False)
    simulator.save_snapshots(snapshots)

    print("\nDEMAND ARRIVAL SIMULATION COMPLETE")
    print(f"="*70)

    print(f" Total packages: {len(df_arrivals)}")
    print(f" Snapshots Summary (cumulative known by time):")
    for time_label, snap in snapshots.items():
        print(f"  - {time_label}: {snap['total_packages']} packages across {snap['locations_with_demand']} locations")

    # Print interval (incremental) summary to avoid confusion
    interval_counts, interval_total = simulator.compute_interval_counts(df_arrivals)
    print("\nInterval Summary (new orders in each window):")
    for label, count in interval_counts:
        print(f"  - {label}: {count} new orders")
    print(f"  - Check: Sum of intervals = {interval_total} (should equal Total packages)")

    