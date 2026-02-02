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

    # Create HTML report
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Peak Season Strategy Comparison</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            h1 { color: #333; text-align: center; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #4CAF50; color: white; }
            tr:hover { background-color: #f5f5f5; }
            .feasible { color: green; font-weight: bold; }
            .infeasible { color: red; font-weight: bold; }
            .best { background-color: #e8f5e9; }
            .chart { margin: 30px 0; }
            .bar { height: 30px; background: #4CAF50; margin: 5px 0; display: flex; align-items: center; padding-left: 10px; color: white; }
            .bar-red { background: #f44336; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Peak Season Strategy Comparison</h1>
    """

    # Summary table
    html += """
            <h2>Strategy Summary</h2>
            <table>
                <tr>
                    <th>Strategy</th>
                    <th>Total Cost</th>
                    <th>Service Level</th>
                    <th>Outsource %</th>
                    <th>Feasible</th>
                </tr>
    """

    for i, d in enumerate(data):
        row_class = 'class="best"' if i == 0 and d['feasible'] else ''
        feasible_class = 'feasible' if d['feasible'] else 'infeasible'
        feasible_text = 'Yes' if d['feasible'] else 'No'
        
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
            </table>
    """

    # Cost breakdown
    html += """
            <h2>Cost Breakdown</h2>
            <table>
                <tr>
                    <th>Strategy</th>
                    <th>Baseline</th>
                    <th>Overtime</th>
                    <th>Outsource</th>
                    <th>Penalty</th>
                    <th>Total</th>
                </tr>
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

    html += """
            </table>
    """

    # Visual cost comparison
    html += """
            <h2>Total Cost Comparison</h2>
            <div class="chart">
    """

    max_cost = max(d['total_cost'] for d in data)
    for d in data:
        width = (d['total_cost'] / max_cost) * 100
        bar_class = 'bar-red' if not d['feasible'] else ''
        html += f"""
                <div class="bar {bar_class}" style="width: {width}%;">
                    {d['strategy']}: ${d['total_cost']:,.0f}
                </div>
        """

    html += """
            </div>
        </div>
    </body>
    </html>
    """

    # Save HTML report
    with open('results/strategy_comparison.html', 'w') as f:
        f.write(html)
    
    print("✓ Strategy comparison report saved to: results/strategy_comparison.html")
    print("  Open this file in your web browser to view the results.")

if __name__ == "__main__":
    visualize_strategies()