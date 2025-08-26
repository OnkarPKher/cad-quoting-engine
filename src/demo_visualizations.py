#!/usr/bin/env python3
"""
Demo script for CAD Quoting Engine Visualizations
This script demonstrates all visualization capabilities with sample data
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent))

from visualizer import CADVisualizer

def create_sample_data():
    """Create sample quote data for demonstration"""
    sample_parts = [
        {
            'part_name': 'Suspension Mount',
            'per_unit_cost': 245.67,
            'total_cost': 245.67,
            'material_cost': 45.23,
            'machine_time_cost': 89.45,
            'labor_cost': 67.89,
            'overhead_cost': 43.10,
            'bounding_box': {'length': 120.5, 'width': 85.2, 'height': 25.8},
            'volume': 258.7,
            'surface_area': 1250.3,
            'complexity_score': 6.8,
            'lead_time_days': 8,
            'shipping_tier': 'standard',
            'quantity': 1,
            'material_waste_percentage': 28.5,
            'feature_counts': {'holes': 4, 'cavities': 2, 'pockets': 1, 'sharp_edges': 8},
            'timestamp': '2024-12-19 14:30:00'
        },
        {
            'part_name': 'Piston Head',
            'per_unit_cost': 389.45,
            'total_cost': 389.45,
            'material_cost': 67.89,
            'machine_time_cost': 145.67,
            'labor_cost': 98.23,
            'overhead_cost': 77.66,
            'bounding_box': {'length': 95.3, 'width': 95.3, 'height': 45.2},
            'volume': 408.9,
            'surface_area': 1890.7,
            'complexity_score': 8.2,
            'lead_time_days': 12,
            'shipping_tier': 'standard',
            'quantity': 1,
            'material_waste_percentage': 32.1,
            'feature_counts': {'holes': 6, 'cavities': 3, 'pockets': 2, 'sharp_edges': 12},
            'timestamp': '2024-12-19 14:30:00'
        },
        {
            'part_name': 'Control Bracket',
            'per_unit_cost': 156.78,
            'total_cost': 156.78,
            'material_cost': 23.45,
            'machine_time_cost': 45.67,
            'labor_cost': 45.23,
            'overhead_cost': 42.43,
            'bounding_box': {'length': 75.2, 'width': 65.8, 'height': 18.5},
            'volume': 91.8,
            'surface_area': 456.2,
            'complexity_score': 4.1,
            'lead_time_days': 6,
            'shipping_tier': 'standard',
            'quantity': 1,
            'material_waste_percentage': 25.3,
            'feature_counts': {'holes': 2, 'cavities': 1, 'pockets': 0, 'sharp_edges': 6},
            'timestamp': '2024-12-19 14:30:00'
        },
        {
            'part_name': 'Test Gear',
            'per_unit_cost': 523.89,
            'total_cost': 523.89,
            'material_cost': 89.67,
            'machine_time_cost': 234.56,
            'labor_cost': 123.45,
            'overhead_cost': 76.21,
            'bounding_box': {'length': 125.8, 'width': 125.8, 'height': 35.6},
            'volume': 562.3,
            'surface_area': 2890.4,
            'complexity_score': 9.1,
            'lead_time_days': 15,
            'shipping_tier': 'standard',
            'quantity': 1,
            'material_waste_percentage': 35.8,
            'feature_counts': {'holes': 8, 'cavities': 4, 'pockets': 3, 'sharp_edges': 24},
            'timestamp': '2024-12-19 14:30:00'
        }
    ]
    
    # Add quantity variations for one part
    suspension_mount_bulk = sample_parts[0].copy()
    suspension_mount_bulk['quantity'] = 10
    suspension_mount_bulk['per_unit_cost'] = 208.82  # 15% discount
    suspension_mount_bulk['total_cost'] = 2088.20
    suspension_mount_bulk['quantity_discount_percentage'] = 15.0
    suspension_mount_bulk['part_name'] = 'Suspension Mount (Qty: 10)'
    
    # Add expedited shipping example
    piston_head_expedited = sample_parts[1].copy()
    piston_head_expedited['shipping_tier'] = 'expedited'
    piston_head_expedited['lead_time_days'] = 8  # 30% faster
    piston_head_expedited['per_unit_cost'] = 506.29  # 30% premium
    piston_head_expedited['total_cost'] = 506.29
    piston_head_expedited['part_name'] = 'Piston Head (Expedited)'
    
    sample_parts.extend([suspension_mount_bulk, piston_head_expedited])
    
    return sample_parts

def demo_individual_visualizations():
    """Demonstrate individual visualization components"""
    print("Generating Individual Visualizations...")
    
    visualizer = CADVisualizer()
    sample_data = create_sample_data()
    
    # Create output directory
    os.makedirs('outputs/individual', exist_ok=True)
    
    # Generate visualizations for the first part (Suspension Mount)
    part = sample_data[0]
    
    # 1. Cost Breakdown Chart
    print("  Creating cost breakdown chart...")
    fig1 = visualizer.create_cost_breakdown_chart(part, 'outputs/individual/cost_breakdown.png')
    print("    Saved: outputs/individual/cost_breakdown.png")
    
    # 2. Complexity Analysis Chart
    print("  Creating complexity analysis chart...")
    fig2 = visualizer.create_complexity_analysis_chart(part, 'outputs/individual/complexity_analysis.png')
    print("    Saved: outputs/individual/complexity_analysis.png")
    
    # 3. Pricing Comparison Chart
    print("  Creating pricing comparison chart...")
    fig3 = visualizer.create_pricing_comparison_chart(part, 'outputs/individual/pricing_comparison.png')
    print("    Saved: outputs/individual/pricing_comparison.png")
    
    print("  Individual visualizations completed!")

def demo_batch_analysis():
    """Demonstrate batch analysis capabilities"""
    print("\nGenerating Batch Analysis...")
    
    visualizer = CADVisualizer()
    sample_data = create_sample_data()
    
    # Create output directory
    os.makedirs('outputs/batch', exist_ok=True)
    
    # Use first 4 parts for batch analysis
    batch_parts = sample_data[:4]
    
    print("  Creating batch comparison charts...")
    fig = visualizer.create_batch_analysis_chart(batch_parts, 'outputs/batch/batch_analysis.png')
    print("    Saved: outputs/batch/batch_analysis.png")
    
    print("  Batch analysis completed!")

def demo_interactive_dashboard():
    """Demonstrate interactive dashboard capabilities"""
    print("\nGenerating Interactive Dashboard...")
    
    visualizer = CADVisualizer()
    sample_data = create_sample_data()
    
    # Create output directory
    os.makedirs('outputs/dashboard', exist_ok=True)
    
    # Generate dashboard for each part
    for i, part in enumerate(sample_data[:3]):  # First 3 parts
        print(f"  Creating dashboard for {part['part_name']}...")
        dashboard_html = visualizer.create_interactive_dashboard(
            part, 
            f'outputs/dashboard/dashboard_{i+1}_{part["part_name"].replace(" ", "_").replace("(", "").replace(")", "").replace(":", "").replace(" ", "_")}.html'
        )
        print(f"    ✓ Saved: outputs/dashboard/dashboard_{i+1}_{part['part_name'].replace(' ', '_').replace('(', '').replace(')', '').replace(':', '').replace(' ', '_')}.html")
    
    print("  Interactive dashboards completed!")

def demo_summary_reports():
    """Demonstrate summary report generation"""
    print("\nGenerating Summary Reports...")
    
    visualizer = CADVisualizer()
    sample_data = create_sample_data()
    
    # Create output directory
    os.makedirs('outputs/reports', exist_ok=True)
    
    # Generate reports for each part
    for i, part in enumerate(sample_data):
        print(f"  📄 Creating report for {part['part_name']}...")
        report_html = visualizer.create_summary_report(
            part, 
            f'outputs/reports/report_{i+1}_{part["part_name"].replace(" ", "_").replace("(", "").replace(")", "").replace(":", "").replace(" ", "_")}.html'
        )
        print(f"    ✓ Saved: outputs/reports/report_{i+1}_{part['part_name'].replace(' ', '_').replace('(', '').replace(')', '').replace(':', '').replace(' ', '_')}.html")
    
    print("  Summary reports completed!")

def demo_quantity_variations():
    """Demonstrate quantity discount visualizations"""
    print("\n🔢 Generating Quantity Variation Analysis...")
    
    visualizer = CADVisualizer()
    
    # Create sample data with different quantities
    quantities = [1, 5, 10, 25, 50]
    base_cost = 245.67
    
    quantity_data = []
    for qty in quantities:
        if qty == 1:
            discount = 0
            unit_cost = base_cost
        elif qty == 5:
            discount = 8
            unit_cost = base_cost * 0.92
        elif qty == 10:
            discount = 15
            unit_cost = base_cost * 0.85
        elif qty == 25:
            discount = 22
            unit_cost = base_cost * 0.78
        else:  # 50
            discount = 30
            unit_cost = base_cost * 0.70
        
        quantity_data.append({
            'part_name': f'Suspension Mount (Qty: {qty})',
            'quantity': qty,
            'per_unit_cost': unit_cost,
            'total_cost': unit_cost * qty,
            'quantity_discount_percentage': discount,
            'material_cost': 45.23 * qty,
            'machine_time_cost': 89.45 * qty,
            'labor_cost': 67.89 * qty,
            'overhead_cost': 43.10 * qty,
            'bounding_box': {'length': 120.5, 'width': 85.2, 'height': 25.8},
            'volume': 258.7,
            'surface_area': 1250.3,
            'complexity_score': 6.8,
            'lead_time_days': 8 + (qty // 10),  # Lead time increases with quantity
            'shipping_tier': 'standard',
            'material_waste_percentage': 28.5,
            'feature_counts': {'holes': 4, 'cavities': 2, 'pockets': 1, 'sharp_edges': 8},
            'timestamp': '2024-12-19 14:30:00'
        })
    
    # Create output directory
    os.makedirs('outputs/quantity', exist_ok=True)
    
    # Generate quantity analysis chart
    print("  Creating quantity discount analysis...")
    fig = visualizer.create_batch_analysis_chart(quantity_data, 'outputs/quantity/quantity_analysis.png')
    print("    ✓ Saved: outputs/quantity/quantity_analysis.png")
    
    # Generate individual reports for each quantity
    for i, data in enumerate(quantity_data):
        print(f"  📄 Creating report for quantity {data['quantity']}...")
        report_html = visualizer.create_summary_report(
            data, 
            f'outputs/quantity/report_qty_{data["quantity"]}.html'
        )
        print(f"    ✓ Saved: outputs/quantity/report_qty_{data['quantity']}.html")
    
    print("  Quantity variation analysis completed!")

def create_readme():
    """Create a README file explaining the visualization outputs"""
    readme_content = """# CAD Quoting Engine - Visualization Outputs

This directory contains all the visualization outputs generated by the CAD Quoting Engine visualizer.

## Directory Structure

### Individual Visualizations (`outputs/individual/`)
- **cost_breakdown.png** - Pie chart and bar chart showing cost breakdown
- **complexity_analysis.png** - Complexity score gauge, dimensions, volume analysis, and material efficiency
- **pricing_comparison.png** - Cost comparisons, lead time analysis, and efficiency metrics

### Batch Analysis (`outputs/batch/`)
- **batch_analysis.png** - Comparison charts across multiple parts showing costs, complexity, volume relationships, and lead times

### Interactive Dashboards (`outputs/dashboard/`)
- **dashboard_*.html** - Interactive Plotly dashboards for each part with zoomable charts and hover information

### Summary Reports (`outputs/reports/`)
- **report_*.html** - Professional HTML reports with styled metrics, cost breakdowns, and part analysis

### Quantity Analysis (`outputs/quantity/`)
- **quantity_analysis.png** - Charts showing how costs change with different quantities
- **report_qty_*.html** - Individual reports for each quantity level

## How to Use

1. **View Static Charts**: Open any `.png` file to see high-resolution charts
2. **Interactive Dashboards**: Open `.html` files in a web browser for interactive exploration
3. **Professional Reports**: Open report HTML files for presentation-ready documentation

## Visualization Features

- **Cost Breakdown**: Material, machine time, labor, and overhead costs
- **Complexity Analysis**: 0-10 complexity scoring with visual gauges
- **Part Dimensions**: 3D-like representations of part geometry
- **Material Efficiency**: Waste percentage and optimization analysis
- **Pricing Trends**: Cost per volume, quantity discounts, and shipping options
- **Lead Time Analysis**: Delivery time based on shipping tiers
- **Batch Comparisons**: Side-by-side analysis of multiple parts

## Technical Details

- **Static Charts**: Generated with Matplotlib and Seaborn (300 DPI PNG)
- **Interactive Charts**: Built with Plotly for web-based exploration
- **HTML Reports**: Responsive design with CSS styling
- **Data Export**: All visualizations can be saved in multiple formats

## Sample Data Used

The visualizations use realistic sample data including:
- Suspension Mount (Simple bracket)
- Piston Head (Complex piston)
- Control Bracket (Simple control component)
- Test Gear (Complex gear with many features)
- Quantity variations (1, 5, 10, 25, 50 units)
- Shipping tier examples (Standard, Expedited)

## Use Cases

- **Sales Presentations**: Professional cost breakdowns for clients
- **Engineering Analysis**: Visual complexity and feature analysis
- **Manufacturing Planning**: Batch analysis for production planning
- **Cost Optimization**: Quantity discount and shipping analysis
- **Portfolio Showcase**: Demonstrate technical capabilities

---
Generated by CAD Quoting Engine Visualizer
"""
    
    with open('outputs/README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("  Created: outputs/README.md")

def main():
    """Main demo function"""
    print("CAD Quoting Engine - Visualization Demo")
    print("=" * 50)
    
    # Create main output directory
    os.makedirs('outputs', exist_ok=True)
    
    try:
        # Run all demo functions
        demo_individual_visualizations()
        demo_batch_analysis()
        demo_interactive_dashboard()
        demo_summary_reports()
        demo_quantity_variations()
        create_readme()
        
        print("\n" + "=" * 50)
        print("All visualizations generated successfully!")
        print("\nOutput files are saved in the 'outputs' directory:")
        print("   ├── individual/     - Static charts for single parts")
        print("   ├── batch/          - Multi-part comparison charts")
        print("   ├── dashboard/      - Interactive Plotly dashboards")
        print("   ├── reports/        - Professional HTML reports")
        print("   ├── quantity/       - Quantity variation analysis")
        print("   └── README.md       - Complete documentation")
        
        print("\nTo view the results:")
        print("   • PNG files: Open in any image viewer")
        print("   • HTML files: Open in a web browser")
        print("   • Interactive dashboards: Best viewed in Chrome/Firefox")
        
    except Exception as e:
        print(f"\nError during visualization generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
