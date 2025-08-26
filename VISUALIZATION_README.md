# 🎨 CAD Quoting Engine - Visualization Tools

Transform your CAD quoting results into professional, interactive visualizations that showcase the transformation from 3D CAD files to detailed cost estimates.

## 🚀 Quick Start

### 1. Install Visualization Dependencies
```bash
pip install -r requirements_visualization.txt
```

### 2. Run Demo Visualizations
```bash
python src/demo_visualizations.py
```

### 3. Generate Visualizations with Real Quotes
```bash
# Single part with visualizations
python src/quote_with_visualizations.py data/suspension-mount.step

# Batch analysis with visualizations
python src/quote_with_visualizations.py --batch data/*.step
```

## 📊 Visualization Types

### 1. **Cost Breakdown Charts** 📈
- **Pie Chart**: Visual representation of cost components (Material, Machine Time, Labor, Overhead)
- **Bar Chart**: Side-by-side comparison of cost breakdowns
- **Features**: Color-coded components, percentage labels, value annotations

### 2. **Complexity Analysis** 🎯
- **Complexity Gauge**: 0-10 scale with visual meter
- **Part Dimensions**: 3D-like representation of part geometry
- **Volume vs Surface Area**: Scatter plot showing geometric relationships
- **Material Efficiency**: Waste percentage and optimization analysis

### 3. **Pricing Comparison** 💰
- **Per-Unit vs Total Cost**: Quantity-based cost analysis
- **Lead Time Analysis**: Shipping tier impact on delivery
- **Cost Efficiency**: Cost per mm³ analysis with industry benchmarks
- **Quantity Discounts**: Visual representation of bulk pricing

### 4. **Interactive Dashboards** 🖥️
- **Plotly-based**: Zoomable, hoverable charts
- **Multi-panel Layout**: 6 different chart types in one view
- **Responsive Design**: Works on desktop and mobile
- **Export Options**: Save as HTML for web sharing

### 5. **Professional Reports** 📋
- **HTML Format**: Styled, presentation-ready reports
- **Key Metrics**: Highlighted cost and complexity information
- **Feature Analysis**: Detailed breakdown of detected features
- **Material Analysis**: Waste percentage and optimization data

### 6. **Batch Analysis** 📈
- **Multi-Part Comparison**: Side-by-side analysis across parts
- **Cost Trends**: Visual patterns in pricing
- **Complexity Distribution**: Range and distribution of complexity scores
- **Volume Relationships**: Cost vs volume correlations

## 🛠️ Usage Examples

### Basic Visualization Generation
```python
from visualizer import CADVisualizer

# Initialize visualizer
visualizer = CADVisualizer()

# Sample quote data
quote_data = {
    'part_name': 'Suspension Mount',
    'per_unit_cost': 245.67,
    'material_cost': 45.23,
    'machine_time_cost': 89.45,
    'labor_cost': 67.89,
    'overhead_cost': 43.10,
    'complexity_score': 6.8,
    # ... other data
}

# Generate visualizations
visualizer.create_cost_breakdown_chart(quote_data, 'cost_breakdown.png')
visualizer.create_complexity_analysis_chart(quote_data, 'complexity.png')
visualizer.create_interactive_dashboard(quote_data, 'dashboard.html')
```

### Integration with CAD Quoting Engine
```python
from quote_with_visualizations import run_quote_with_visualizations

# Generate quote with automatic visualizations
quote_data = run_quote_with_visualizations(
    'data/suspension-mount.step',
    quantity=10,
    shipping='economy'
)
```

### Batch Processing
```python
from quote_with_visualizations import run_batch_analysis

# Process multiple STEP files
step_files = ['data/part1.step', 'data/part2.step', 'data/part3.step']
run_batch_analysis(step_files, quantity=5, shipping='standard')
```

## 📁 Output Structure

```
outputs/
├── individual/              # Single part visualizations
│   ├── cost_breakdown.png
│   ├── complexity_analysis.png
│   └── pricing_comparison.png
├── batch/                   # Multi-part comparisons
│   └── batch_analysis.png
├── dashboard/               # Interactive dashboards
│   ├── dashboard_1_Suspension_Mount.html
│   ├── dashboard_2_Piston_Head.html
│   └── dashboard_3_Control_Bracket.html
├── reports/                 # Professional HTML reports
│   ├── report_1_Suspension_Mount.html
│   ├── report_2_Piston_Head.html
│   └── report_3_Control_Bracket.html
├── quantity/                # Quantity variation analysis
│   ├── quantity_analysis.png
│   └── report_qty_*.html
└── batch_analysis/          # Batch processing results
    ├── batch_comparison.png
    ├── Suspension_Mount/
    ├── Piston_Head/
    └── batch_results.json
```

## 🎨 Customization Options

### Color Schemes
```python
# Customize colors for different components
visualizer.colors = {
    'material': '#FF6B6B',      # Red for material costs
    'machine_time': '#4ECDC4',  # Teal for machine time
    'labor': '#45B7D1',         # Blue for labor
    'overhead': '#96CEB4',      # Green for overhead
    'total': '#FFEAA7',         # Yellow for total costs
    'complexity': '#DDA0DD',    # Purple for complexity
    'efficiency': '#98D8C8'     # Mint for efficiency
}
```

### Chart Styling
```python
# Customize chart appearance
plt.style.use('seaborn-v0_8')  # Modern styling
sns.set_palette("husl")        # Harmonious color palette
```

### Output Formats
```python
# High-resolution PNG output
fig.savefig('output.png', dpi=300, bbox_inches='tight')

# Interactive HTML with Plotly
fig.write_html('dashboard.html')

# Professional HTML reports
report_html = visualizer.create_summary_report(quote_data)
```

## 🔧 Technical Features

### **Static Charts (Matplotlib/Seaborn)**
- **High Resolution**: 300 DPI output for professional printing
- **Vector Graphics**: Scalable without quality loss
- **Custom Styling**: Professional appearance with consistent branding
- **Export Options**: PNG, PDF, SVG formats

### **Interactive Charts (Plotly)**
- **Zoom & Pan**: Interactive exploration of data
- **Hover Information**: Detailed tooltips on hover
- **Responsive Design**: Works on all screen sizes
- **Export Options**: PNG, PDF, HTML formats

### **HTML Reports**
- **CSS Styling**: Professional appearance
- **Responsive Layout**: Mobile-friendly design
- **Embedded Charts**: Charts integrated into reports
- **Cross-Platform**: Works in all modern browsers

## 📊 Sample Data Structure

The visualizer expects quote data in this format:
```python
quote_data = {
    'part_name': 'Part Name',
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
}
```

## 🎯 Use Cases

### **Sales & Marketing**
- **Client Presentations**: Professional cost breakdowns
- **Proposal Documents**: Visual cost analysis
- **Portfolio Showcase**: Demonstrate technical capabilities

### **Engineering & Manufacturing**
- **Cost Analysis**: Visual cost component breakdown
- **Complexity Assessment**: Part difficulty visualization
- **Batch Planning**: Multi-part comparison analysis

### **Project Management**
- **Cost Tracking**: Visual cost progression
- **Resource Planning**: Labor and material analysis
- **Timeline Planning**: Lead time visualization

### **Quality Assurance**
- **Feature Analysis**: Visual representation of detected features
- **Material Optimization**: Waste percentage analysis
- **Efficiency Metrics**: Cost per volume analysis

## 🚀 Advanced Features

### **Batch Processing**
```bash
# Process all STEP files in data directory
python src/quote_with_visualizations.py --batch "data/*.step"

# Custom quantity and shipping for batch
python src/quote_with_visualizations.py --batch "data/*.step" --quantity 10 --shipping economy
```

### **Custom Output Paths**
```python
# Save visualizations to custom directory
output_dir = "my_project/visualizations"
os.makedirs(output_dir, exist_ok=True)

visualizer.create_cost_breakdown_chart(quote_data, f"{output_dir}/costs.png")
```

### **Integration with Existing Workflows**
```python
# Use visualizer with existing quote data
from main import CADQuotingEngine

engine = CADQuotingEngine()
quote_result = engine.generate_quote('part.step')

# Convert to visualization format
quote_data = {
    'part_name': 'My Part',
    'per_unit_cost': quote_result.per_unit_cost,
    # ... convert other fields
}

# Generate visualizations
visualizer.create_summary_report(quote_data, 'my_report.html')
```

## 🔍 Troubleshooting

### **Common Issues**

1. **Missing Dependencies**
   ```bash
   pip install matplotlib seaborn plotly numpy pandas
   ```

2. **Display Issues on Windows**
   ```python
   import matplotlib
   matplotlib.use('Agg')  # Use non-interactive backend
   ```

3. **Plotly Display Issues**
   ```python
   # Use offline mode for local development
   import plotly.offline as pyo
   pyo.init_notebook_mode(connected=True)
   ```

### **Performance Optimization**
```python
# For large datasets, use lower DPI
fig.savefig('output.png', dpi=150)  # Faster rendering

# Disable animations for faster generation
fig.update_layout(showlegend=False, height=600)
```

## 📚 API Reference

### **CADVisualizer Class**

#### **Methods**
- `create_cost_breakdown_chart(quote_data, save_path=None)`
- `create_complexity_analysis_chart(quote_data, save_path=None)`
- `create_pricing_comparison_chart(quote_data, save_path=None)`
- `create_interactive_dashboard(quote_data, save_path=None)`
- `create_summary_report(quote_data, save_path=None)`
- `create_batch_analysis_chart(batch_results, save_path=None)`

#### **Parameters**
- `quote_data`: Dictionary containing quote information
- `save_path`: Optional path to save output file
- `batch_results`: List of quote data dictionaries

#### **Returns**
- **Static Charts**: Matplotlib Figure objects
- **Interactive Dashboards**: HTML string or saved file
- **Reports**: HTML string or saved file

## 🌟 Future Enhancements

### **Planned Features**
- **3D Part Visualization**: Interactive 3D part models
- **Cost Trend Analysis**: Historical cost tracking
- **Machine Learning Integration**: Predictive cost modeling
- **Web Application**: Browser-based visualization interface
- **Real-time Updates**: Live cost calculation updates

### **Customization Options**
- **Template System**: Custom report templates
- **Branding Integration**: Company logo and colors
- **Multi-language Support**: Internationalization
- **Export Formats**: Excel, PowerPoint, PDF

## 📞 Support & Contributing

### **Getting Help**
1. Check the troubleshooting section above
2. Review the demo scripts for examples
3. Examine the sample data structure
4. Check error messages for specific issues

### **Contributing**
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

### **Feature Requests**
- Suggest new visualization types
- Request additional customization options
- Propose integration improvements

---

**🎨 Transform your CAD quotes into compelling visual stories with the CAD Quoting Engine Visualization Tools!**
