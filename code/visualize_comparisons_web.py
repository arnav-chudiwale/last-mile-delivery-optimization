import json

def visualize_strategies():
    # Load strategy comparisons
    with open('results/strategy_comparison.json', 'r') as f:
        strategies = json.load(f)

    # Extract data
    data = []
    for key, s in strategies.items():
        data.append({
            'strategy': s['strategy'],
            'total_cost': s['total_cost'],
            'service_level': s['service_level'],
            'outsource_pct': s.get('outsource_percentage', 0),
            'feasible': s['feasible'],
            'baseline_cost': s['baseline_cost'],
            'overtime_cost': s.get('overtime_cost', 0),
            'outsource_cost': s.get('outsource_cost', 0),
            'penalty_cost': s.get('late_penalty_cost', 0)
        })

    # Sort by total cost
    data.sort(key=lambda x: x['total_cost'])

    # Prepare data for JavaScript
    strategies_list = [d['strategy'] for d in data]
    total_costs = [d['total_cost'] for d in data]
    service_levels = [d['service_level'] for d in data]
    outsource_pcts = [d['outsource_pct'] for d in data]
    feasible_list = [d['feasible'] for d in data]
    
    baseline_costs = [d['baseline_cost'] for d in data]
    overtime_costs = [d['overtime_cost'] for d in data]
    outsource_costs = [d['outsource_cost'] for d in data]
    penalty_costs = [d['penalty_cost'] for d in data]

    # Create HTML report with interactive charts
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Peak Season Strategy Comparison</title>
        <meta charset="UTF-8">
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
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
            .charts-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
                gap: 30px;
                margin: 30px 0;
            }}
            .chart-container {{
                background: #f9f9f9;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .chart-title {{
                font-size: 1.3em;
                font-weight: bold;
                color: #333;
                margin-bottom: 15px;
                text-align: center;
            }}
            canvas {{
                max-height: 400px;
            }}
            table {{ 
                width: 100%;
                border-collapse: collapse;
                margin: 30px 0;
                background: white;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border-radius: 10px;
                overflow: hidden;
            }}
            th, td {{ 
                padding: 15px;
                text-align: left;
            }}
            th {{ 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 0.9em;
                letter-spacing: 0.5px;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            tr:hover {{ 
                background-color: #f0f0f0;
                transition: background-color 0.3s;
            }}
            .feasible {{ 
                color: #4CAF50;
                font-weight: bold;
            }}
            .infeasible {{ 
                color: #f44336;
                font-weight: bold;
            }}
            .best {{ 
                background-color: #e8f5e9 !important;
                border-left: 4px solid #4CAF50;
            }}
            .metric-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin: 10px 0;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }}
            .metric-value {{
                font-size: 2.5em;
                font-weight: bold;
                margin: 10px 0;
            }}
            .metric-label {{
                font-size: 1.1em;
                opacity: 0.9;
            }}
            .summary-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            .legend-item {{
                display: inline-flex;
                align-items: center;
                margin-right: 20px;
                font-size: 0.9em;
            }}
            .legend-color {{
                width: 20px;
                height: 20px;
                margin-right: 8px;
                border-radius: 3px;
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
            <h1>📊 Peak Season Strategy Comparison</h1>
            <p class="subtitle">Interactive Dashboard for Delivery Operations Analysis</p>

            <div class="summary-grid">
                <div class="metric-card">
                    <div class="metric-label">Best Strategy</div>
                    <div class="metric-value">{data[0]['strategy'] if data[0]['feasible'] else 'None Feasible'}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Lowest Cost</div>
                    <div class="metric-value">${min([d['total_cost'] for d in data if d['feasible']], default=0):,.0f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Strategies Analyzed</div>
                    <div class="metric-value">{len(data)}</div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">Interactive Visualizations</div>
                <div class="charts-grid">
                    <div class="chart-container">
                        <div class="chart-title">Total Cost by Strategy</div>
                        <canvas id="costChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-title">Service Level Achievement</div>
                        <canvas id="serviceChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-title">Cost Breakdown</div>
                        <canvas id="breakdownChart"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-title">Outsourcing Percentage</div>
                        <canvas id="outsourceChart"></canvas>
                    </div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">Detailed Strategy Comparison</div>
                <table>
                    <thead>
                        <tr>
                            <th>Strategy</th>
                            <th>Total Cost</th>
                            <th>Service Level</th>
                            <th>Outsource %</th>
                            <th>Feasible</th>
                        </tr>
                    </thead>
                    <tbody>
    """

    for i, d in enumerate(data):
        row_class = 'class="best"' if i == 0 and d['feasible'] else ''
        feasible_class = 'feasible' if d['feasible'] else 'infeasible'
        feasible_text = '✓ Yes' if d['feasible'] else '✗ No'
        
        html += f"""
                        <tr {row_class}>
                            <td><strong>{d['strategy']}</strong></td>
                            <td>${d['total_cost']:,.0f}</td>
                            <td>{d['service_level']:.1f}%</td>
                            <td>{d['outsource_pct']:.1f}%</td>
                            <td class="{feasible_class}">{feasible_text}</td>
                        </tr>
        """

    html += """
                    </tbody>
                </table>
            </div>

            <div class="section">
                <div class="section-title">Cost Component Breakdown</div>
                <table>
                    <thead>
                        <tr>
                            <th>Strategy</th>
                            <th>Baseline</th>
                            <th>Overtime</th>
                            <th>Outsource</th>
                            <th>Penalty</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
    """

    for d in data:
        html += f"""
                        <tr>
                            <td><strong>{d['strategy']}</strong></td>
                            <td>${d['baseline_cost']:,.0f}</td>
                            <td>${d['overtime_cost']:,.0f}</td>
                            <td>${d['outsource_cost']:,.0f}</td>
                            <td>${d['penalty_cost']:,.0f}</td>
                            <td><strong>${d['total_cost']:,.0f}</strong></td>
                        </tr>
        """

    html += f"""
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            // Data from Python
            const strategies = {json.dumps(strategies_list)};
            const totalCosts = {json.dumps(total_costs)};
            const serviceLevels = {json.dumps(service_levels)};
            const outsourcePcts = {json.dumps(outsource_pcts)};
            const feasible = {json.dumps(feasible_list)};
            const baselineCosts = {json.dumps(baseline_costs)};
            const overtimeCosts = {json.dumps(overtime_costs)};
            const outsourceCosts = {json.dumps(outsource_costs)};
            const penaltyCosts = {json.dumps(penalty_costs)};

            // Colors based on feasibility
            const backgroundColors = feasible.map(f => f ? 'rgba(76, 175, 80, 0.7)' : 'rgba(244, 67, 54, 0.7)');
            const borderColors = feasible.map(f => f ? 'rgba(76, 175, 80, 1)' : 'rgba(244, 67, 54, 1)');

            // Chart 1: Total Cost Comparison
            new Chart(document.getElementById('costChart'), {{
                type: 'bar',
                data: {{
                    labels: strategies,
                    datasets: [{{
                        label: 'Total Cost ($)',
                        data: totalCosts,
                        backgroundColor: backgroundColors,
                        borderColor: borderColors,
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {{
                        legend: {{
                            display: false
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return 'Cost: $' + context.parsed.y.toLocaleString();
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{
                                callback: function(value) {{
                                    return '$' + value.toLocaleString();
                                }}
                            }}
                        }}
                    }}
                }}
            }});

            // Chart 2: Service Level
            new Chart(document.getElementById('serviceChart'), {{
                type: 'bar',
                data: {{
                    labels: strategies,
                    datasets: [{{
                        label: 'Service Level (%)',
                        data: serviceLevels,
                        backgroundColor: backgroundColors,
                        borderColor: borderColors,
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {{
                        legend: {{
                            display: false
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return 'Service Level: ' + context.parsed.y.toFixed(1) + '%';
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 110,
                            ticks: {{
                                callback: function(value) {{
                                    return value + '%';
                                }}
                            }}
                        }}
                    }}
                }}
            }});

            // Chart 3: Stacked Bar Chart - Cost Breakdown
            new Chart(document.getElementById('breakdownChart'), {{
                type: 'bar',
                data: {{
                    labels: strategies,
                    datasets: [
                        {{
                            label: 'Baseline Operations',
                            data: baselineCosts,
                            backgroundColor: 'rgba(70, 130, 180, 0.8)',
                            borderColor: 'rgba(70, 130, 180, 1)',
                            borderWidth: 1
                        }},
                        {{
                            label: 'Overtime',
                            data: overtimeCosts,
                            backgroundColor: 'rgba(255, 159, 64, 0.8)',
                            borderColor: 'rgba(255, 159, 64, 1)',
                            borderWidth: 1
                        }},
                        {{
                            label: 'Outsource',
                            data: outsourceCosts,
                            backgroundColor: 'rgba(240, 128, 128, 0.8)',
                            borderColor: 'rgba(240, 128, 128, 1)',
                            borderWidth: 1
                        }},
                        {{
                            label: 'Late Penalty',
                            data: penaltyCosts,
                            backgroundColor: 'rgba(139, 0, 0, 0.8)',
                            borderColor: 'rgba(139, 0, 0, 1)',
                            borderWidth: 1
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {{
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return context.dataset.label + ': $' + context.parsed.y.toLocaleString();
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            stacked: true
                        }},
                        y: {{
                            stacked: true,
                            beginAtZero: true,
                            ticks: {{
                                callback: function(value) {{
                                    return '$' + value.toLocaleString();
                                }}
                            }}
                        }}
                    }}
                }}
            }});

            // Chart 4: Outsourcing Percentage
            new Chart(document.getElementById('outsourceChart'), {{
                type: 'bar',
                data: {{
                    labels: strategies,
                    datasets: [{{
                        label: 'Outsourcing (%)',
                        data: outsourcePcts,
                        backgroundColor: 'rgba(240, 128, 128, 0.8)',
                        borderColor: 'rgba(240, 128, 128, 1)',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {{
                        legend: {{
                            display: false
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return 'Outsourcing: ' + context.parsed.y.toFixed(1) + '%';
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{
                                callback: function(value) {{
                                    return value + '%';
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

    # Save HTML report
    with open('results/strategy_comparison.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✓ Interactive strategy comparison report saved!")
    print("  📁 Location: results/interactive_comparison.html")
    print("  🌐 Open this file in your web browser to view interactive charts")

if __name__ == "__main__":
    visualize_strategies()