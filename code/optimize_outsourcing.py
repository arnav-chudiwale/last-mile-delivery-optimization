'''
Finding optimal overtime-outsourcing mix
'''
import numpy as np 
from scipy.optimize import minimize_scalar
import json 

class OutsourcingOptimizer: 
    def __init__(self):
        #Load Baseline
        with open("results/baseline_solution.json", 'r') as f:
            baseline = json.load(f)
        
        #Load Costs
        with open("data/cost_parameters.json", 'r') as f:
            costs = json.load(f)
        
        #Parameters based on data
        self.baseline_capacity = 1600
        self.num_vehicles = 32
        self.peak_demand = 3906
        self.overflow = self.peak_demand - self.baseline_capacity

        #Costs 
        self.overtime_hourly_rate = costs['driver_hourly_rate_overtime']
        self.outsource_per_package = costs['outsource_cost_per_package']

        #Productivity (From Baseline Performance)
        self.packages_per_hour_per_driver = 6

        print(f"Optimization Setup:")
        print(f"Peak Demand: {self.peak_demand} packages")
        print(f"Baseline Capacity: {self.baseline_capacity} packages")
        print(f"Overflow to handle: {self.overflow} packages")
        print(f"Fleet Size: {self.num_vehicles} vehicles")
        print(f"Productivity: {self.packages_per_hour_per_driver} packages/hour/driver")


    def total_additional_costs(self, extra_hours):
        '''
        extra_hours = Hours of overtime/driver (0-2)

        returns: 
        Total additional cost (overtime + outsourcing)
        '''
        #Constrain extra_hours to the range (0-2)
        extra_hours = np.clip(extra_hours, 0, 2)

        #Additional capacity from overtime
        overtime_capacity = (extra_hours * self.num_vehicles * self.packages_per_hour_per_driver)

        #Packages still needing outsourcing
        outsource_packages = max(0, self.overflow - overtime_capacity)

        #Costs 
        overtime_cost = extra_hours * self.num_vehicles * self.overtime_hourly_rate
        outsource_cost = outsource_packages * self.outsource_per_package

        return overtime_cost + outsource_cost
    
    def optimize(self):
        '''
        Find optimal overtime hours
        '''
        print("\nOptimizing overtime-outsourcing tradeoff...")

        # Using scipy optimization 
        result = minimize_scalar(
            self.total_additional_costs,
            bounds=(0, 2),
            method='bounded'
        )

        optimal_hours = result.x 
        optimal_cost = result.fun 

        #Calculate breakdown at optimal point
        overtime_capacity = (optimal_hours * self.num_vehicles * self.packages_per_hour_per_driver)
        outsource_packages = max(0, self.overflow - overtime_capacity)

        overtime_cost = optimal_hours * self.num_vehicles * self.overtime_hourly_rate
        outsource_cost = outsource_packages * self.outsource_per_package

        solution = {
            'optimal_overtime_hours': round(optimal_hours, 3),
            'capacity_from_overtime': int(overtime_capacity),
            'packages_outsourced': int(outsource_packages),
            'outsource_percentage': round((outsource_packages/self.peak_demand)*100, 3),
            'overtime_cost': round(overtime_cost, 2),
            'outsource_cost': round(outsource_cost, 2),
            'total_additional_cost': round(optimal_cost, 2)
        }
        return solution
    
    def sensitivity_analysis(self):
        '''Analyze cost across overtime range and create interactive visualization'''
        overtime_range = np.linspace(0, 2, 100)

        total_costs = [self.total_additional_costs(h) for h in overtime_range]

        # Component costs 
        overtime_costs = []
        outsource_costs = []

        for h in overtime_range:
            ot_capacity = h * self.num_vehicles * self.packages_per_hour_per_driver
            out_packages = max(0, self.overflow - ot_capacity)

            ot_cost = h * self.num_vehicles * self.overtime_hourly_rate
            out_cost = out_packages * self.outsource_per_package

            overtime_costs.append(ot_cost)
            outsource_costs.append(out_cost)

        # Get optimal solution 
        optimal = self.optimize()

        # Create interactive HTML visualization
        self.create_html_visualization(
            overtime_range.tolist(),
            total_costs,
            overtime_costs,
            outsource_costs,
            optimal
        )

        return optimal 
    
    def create_html_visualization(self, overtime_range, total_costs, overtime_costs, outsource_costs, optimal):
        '''Create interactive HTML visualization using Chart.js'''
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Overtime-Outsourcing Optimization Analysis</title>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1/dist/chartjs-plugin-annotation.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ 
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        h1 {{ 
            color: #333;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 8px;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
        }}
        .charts-container {{
            margin: 30px 0;
        }}
        .chart-wrapper {{
            background: #f9f9f9;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .chart-title {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
            margin-bottom: 20px;
            text-align: center;
        }}
        canvas {{
            max-height: 500px;
        }}
        .optimal-box {{
            background: #e8f5e9;
            border-left: 4px solid #4CAF50;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .optimal-box h3 {{
            color: #2E7D32;
            margin-bottom: 15px;
        }}
        .optimal-detail {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .optimal-item {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .optimal-item-label {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }}
        .optimal-item-value {{
            color: #333;
            font-size: 1.3em;
            font-weight: bold;
        }}
        .section {{
            margin: 40px 0;
        }}
        .section-title {{
            font-size: 1.8em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Overtime-Outsourcing Optimization</h1>
        <p class="subtitle">Sensitivity Analysis & Cost Trade-off Visualization</p>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Optimal Overtime Hours</div>
                <div class="metric-value">{optimal['optimal_overtime_hours']}</div>
                <div class="metric-label">hours per driver</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Additional Cost</div>
                <div class="metric-value">${optimal['total_additional_cost']:,.0f}</div>
                <div class="metric-label">at optimal point</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Packages Outsourced</div>
                <div class="metric-value">{optimal['packages_outsourced']}</div>
                <div class="metric-label">{optimal['outsource_percentage']:.1f}% of peak demand</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Capacity from Overtime</div>
                <div class="metric-value">{optimal['capacity_from_overtime']}</div>
                <div class="metric-label">packages</div>
            </div>
        </div>

        <div class="optimal-box">
            <h3>📊 Optimal Solution Breakdown</h3>
            <div class="optimal-detail">
                <div class="optimal-item">
                    <div class="optimal-item-label">Overtime Cost</div>
                    <div class="optimal-item-value">${optimal['overtime_cost']:,.2f}</div>
                </div>
                <div class="optimal-item">
                    <div class="optimal-item-label">Outsource Cost</div>
                    <div class="optimal-item-value">${optimal['outsource_cost']:,.2f}</div>
                </div>
                <div class="optimal-item">
                    <div class="optimal-item-label">Total Additional</div>
                    <div class="optimal-item-value">${optimal['total_additional_cost']:,.2f}</div>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">Interactive Cost Analysis</div>
            
            <div class="chart-wrapper">
                <div class="chart-title">Total Cost Optimization Curve</div>
                <canvas id="costCurveChart"></canvas>
            </div>

            <div class="chart-wrapper">
                <div class="chart-title">Cost Breakdown by Component</div>
                <canvas id="breakdownChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        const overtimeRange = {json.dumps(overtime_range)};
        const totalCosts = {json.dumps(total_costs)};
        const overtimeCosts = {json.dumps(overtime_costs)};
        const outsourceCosts = {json.dumps(outsource_costs)};
        const optimalHours = {optimal['optimal_overtime_hours']};
        const optimalCost = {optimal['total_additional_cost']};

        // Chart 1: Total Cost Curve with Optimal Point
        new Chart(document.getElementById('costCurveChart'), {{
            type: 'line',
            data: {{
                labels: overtimeRange,
                datasets: [
                    {{
                        label: 'Total Additional Cost',
                        data: totalCosts,
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0
                    }},
                    {{
                        label: 'Optimal Point',
                        data: [{{x: optimalHours, y: optimalCost}}],
                        backgroundColor: 'rgba(255, 99, 132, 1)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        pointRadius: 10,
                        pointHoverRadius: 15,
                        showLine: false
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                interaction: {{
                    intersect: false,
                    mode: 'index'
                }},
                plugins: {{
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                if (context.datasetIndex === 0) {{
                                    return 'Cost: $' + context.parsed.y.toLocaleString();
                                }} else {{
                                    return 'Optimal: $' + context.parsed.y.toLocaleString() + ' at ' + optimalHours.toFixed(3) + ' hours';
                                }}
                            }},
                            title: function(context) {{
                                return 'Overtime Hours: ' + parseFloat(context[0].label).toFixed(2);
                            }}
                        }}
                    }},
                    annotation: {{
                        annotations: {{
                            line1: {{
                                type: 'line',
                                xMin: optimalHours,
                                xMax: optimalHours,
                                borderColor: 'rgba(255, 99, 132, 0.5)',
                                borderWidth: 2,
                                borderDash: [6, 6],
                                label: {{
                                    display: true,
                                    content: 'Optimal: ' + optimalHours.toFixed(3) + ' hrs',
                                    position: 'start'
                                }}
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        title: {{
                            display: true,
                            text: 'Overtime Hours per Driver',
                            font: {{
                                size: 14,
                                weight: 'bold'
                            }}
                        }},
                        ticks: {{
                            callback: function(value, index) {{
                                return index % 10 === 0 ? value.toFixed(1) : '';
                            }}
                        }}
                    }},
                    y: {{
                        title: {{
                            display: true,
                            text: 'Total Additional Cost ($)',
                            font: {{
                                size: 14,
                                weight: 'bold'
                            }}
                        }},
                        ticks: {{
                            callback: function(value) {{
                                return '$' + value.toLocaleString();
                            }}
                        }}
                    }}
                }}
            }}
        }});

        // Chart 2: Stacked Area Chart for Cost Components
        new Chart(document.getElementById('breakdownChart'), {{
            type: 'line',
            data: {{
                labels: overtimeRange,
                datasets: [
                    {{
                        label: 'Overtime Costs',
                        data: overtimeCosts,
                        backgroundColor: 'rgba(255, 159, 64, 0.7)',
                        borderColor: 'rgba(255, 159, 64, 1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0
                    }},
                    {{
                        label: 'Outsource Costs',
                        data: outsourceCosts,
                        backgroundColor: 'rgba(70, 130, 180, 0.7)',
                        borderColor: 'rgba(70, 130, 180, 1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                interaction: {{
                    intersect: false,
                    mode: 'index'
                }},
                plugins: {{
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.dataset.label + ': $' + context.parsed.y.toLocaleString();
                            }},
                            title: function(context) {{
                                return 'Overtime Hours: ' + parseFloat(context[0].label).toFixed(2);
                            }}
                        }}
                    }},
                    annotation: {{
                        annotations: {{
                            line1: {{
                                type: 'line',
                                xMin: optimalHours,
                                xMax: optimalHours,
                                borderColor: 'rgba(255, 99, 132, 0.8)',
                                borderWidth: 2,
                                borderDash: [6, 6],
                                label: {{
                                    display: true,
                                    content: 'Optimal',
                                    position: 'start',
                                    backgroundColor: 'rgba(255, 99, 132, 0.8)'
                                }}
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        title: {{
                            display: true,
                            text: 'Overtime Hours per Driver',
                            font: {{
                                size: 14,
                                weight: 'bold'
                            }}
                        }},
                        ticks: {{
                            callback: function(value, index) {{
                                return index % 10 === 0 ? value.toFixed(1) : '';
                            }}
                        }}
                    }},
                    y: {{
                        stacked: false,
                        title: {{
                            display: true,
                            text: 'Cost ($)',
                            font: {{
                                size: 14,
                                weight: 'bold'
                            }}
                        }},
                        ticks: {{
                            callback: function(value) {{
                                return '$' + value.toLocaleString();
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
        """
        
        with open('results/optimization_sensitivity.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("✓ Sensitivity analysis visualization saved to: results/optimization_sensitivity.html")

    def print_solution(self, solution):
        print("\n" + "="*80)
        print("OPTIMAL SOLUTION")
        print("="*80)
        print(f"Optimal Overtime: {solution['optimal_overtime_hours']} hours/driver")
        print(f"Capacity added by overtime: {solution['capacity_from_overtime']} packages")
        print(f"Packages to outsource: {solution['packages_outsourced']}")

        print(f"\nCost Breakdown:")
        print(f"  Overtime Cost: ${solution['overtime_cost']:,.2f}")
        print(f"  Outsource Cost: ${solution['outsource_cost']:,.2f}")
        print(f"  TOTAL ADDITIONAL: ${solution['total_additional_cost']:,.2f}")

        # Add Baseline cost 
        with open('results/baseline_solution.json', 'r') as f:
            baseline = json.load(f)

        total_peak_cost = baseline['costs']['total_costs'] + solution['total_additional_cost']

        print(f"\nFull Peak Period Cost:")
        print(f"  Baseline Operations: ${baseline['costs']['total_costs']:,.2f}")
        print(f"  Peak Additional: ${solution['total_additional_cost']:,.2f}")
        print(f"  TOTAL: ${total_peak_cost:,.2f}")
        print(f"  Cost per package: ${total_peak_cost/3906:,.2f}")

if __name__ == "__main__": 
    optimizer = OutsourcingOptimizer()
    optimal_solution = optimizer.sensitivity_analysis()
    optimizer.print_solution(optimal_solution)

    # Saving result
    with open('results/optimal_outsourcing.json', 'w') as f:
        json.dump(optimal_solution, f, indent=2)

    print("\n✓ Optimal Solution saved to: results/optimal_outsourcing.json")
    print("✓ Open results/optimization_sensitivity.html in your browser to view interactive charts")