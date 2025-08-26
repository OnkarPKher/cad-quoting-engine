import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import json
import os
from typing import Dict, List, Tuple, Optional
import seaborn as sns
from matplotlib.patches import Rectangle, FancyBboxPatch
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
import trimesh
from mpl_toolkits.mplot3d import Axes3D

class CADVisualizer:
    """Advanced visualization tools for CAD Quoting Engine results"""
    
    def __init__(self):
        # Set style for better-looking plots
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Color schemes for different components
        self.colors = {
            'material': '#FF6B6B',
            'machine_time': '#4ECDC4', 
            'labor': '#45B7D1',
            'overhead': '#96CEB4',
            'total': '#FFEAA7',
            'complexity': '#DDA0DD',
            'efficiency': '#98D8C8',
            'success': '#2ECC71',
            'warning': '#F39C12',
            'danger': '#E74C3C'
        }
        
        # Enhanced color palettes for different chart types
        self.palettes = {
            'cost': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
            'complexity': ['#2ECC71', '#F39C12', '#E74C3C'],
            'efficiency': ['#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
        }
    
    def create_3d_part_visualization(self, mesh: trimesh.Trimesh, save_path: str = None) -> plt.Figure:
        """Create a 3D visualization of the actual CAD part"""
        fig = plt.figure(figsize=(15, 10))
        
        # Create 3D subplot
        ax = fig.add_subplot(111, projection='3d')
        
        # Extract vertices and faces
        vertices = mesh.vertices
        faces = mesh.faces
        
        # Create 3D surface plot
        ax.plot_trisurf(vertices[:, 0], vertices[:, 1], vertices[:, 2], 
                       triangles=faces, alpha=0.8, color='lightblue', edgecolor='navy')
        
        # Add bounding box
        bounds = mesh.bounds
        x_min, y_min, z_min = bounds[0]
        x_max, y_max, z_max = bounds[1]
        
        # Create bounding box wireframe
        for i in range(4):
            ax.plot([x_min, x_max], [y_min, y_min], [z_min + i*(z_max-z_min)/3], 'r--', alpha=0.5)
            ax.plot([x_min, x_min], [y_min, y_max], [z_min + i*(z_max-z_min)/3], 'r--', alpha=0.5)
            ax.plot([x_min, x_max], [y_max, y_max], [z_min + i*(z_max-z_min)/3], 'r--', alpha=0.5)
            ax.plot([x_max, x_max], [y_min, y_max], [z_min + i*(z_max-z_min)/3], 'r--', alpha=0.5)
        
        # Set labels and title
        ax.set_xlabel('Length (mm)')
        ax.set_ylabel('Width (mm)')
        ax.set_zlabel('Height (mm)')
        ax.set_title('3D Part Visualization with Bounding Box', fontsize=14, fontweight='bold')
        
        # Add dimensions text
        dimensions = {
            'length': x_max - x_min,
            'width': y_max - y_min,
            'height': z_max - z_min
        }
        
        ax.text2D(0.02, 0.98, f"Dimensions: {dimensions['length']:.1f} × {dimensions['width']:.1f} × {dimensions['height']:.1f} mm", 
                  transform=ax.transAxes, fontsize=10, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def create_feature_analysis_chart(self, quote_data: Dict, save_path: str = None) -> plt.Figure:
        """Create detailed feature analysis charts"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Feature counts radar chart
        features = quote_data.get('feature_counts', {})
        if features:
            feature_names = list(features.keys())
            feature_values = list(features.values())
            
            # Normalize values to 0-1 scale for radar chart
            max_val = max(feature_values) if feature_values else 1
            normalized_values = [v/max_val for v in feature_values]
            
            # Create radar chart
            angles = np.linspace(0, 2*np.pi, len(feature_names), endpoint=False).tolist()
            angles += angles[:1]  # Close the loop
            normalized_values += normalized_values[:1]
            
            ax1.plot(angles, normalized_values, 'o-', linewidth=2, color=self.colors['complexity'])
            ax1.fill(angles, normalized_values, alpha=0.25, color=self.colors['complexity'])
            ax1.set_xticks(angles[:-1])
            ax1.set_xticklabels(feature_names)
            ax1.set_ylim(0, 1)
            ax1.set_title('Feature Complexity Radar Chart', fontsize=14, fontweight='bold')
            ax1.grid(True)
        
        # Feature impact on cost
        if features:
            feature_costs = []
            for feature, count in features.items():
                # Estimate cost impact based on feature type and count
                base_impact = {'holes': 5, 'cavities': 15, 'pockets': 20, 'sharp_edges': 3}
                impact = base_impact.get(feature, 5) * count
                feature_costs.append(impact)
            
            bars = ax2.bar(feature_names, feature_costs, color=self.palettes['cost'][:len(feature_names)])
            ax2.set_ylabel('Estimated Cost Impact ($)')
            ax2.set_title('Feature Impact on Manufacturing Cost', fontsize=14, fontweight='bold')
            ax2.tick_params(axis='x', rotation=45)
            
            # Add value labels
            for bar, cost in zip(bars, feature_costs):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01 * max(feature_costs),
                        f'${cost:.0f}', ha='center', va='bottom', fontweight='bold')
        
        # Manufacturing difficulty assessment
        complexity_score = quote_data.get('complexity_score', 0)
        if complexity_score <= 3:
            difficulty = 'Easy'
            color = self.colors['success']
        elif complexity_score <= 7:
            difficulty = 'Medium'
            color = self.colors['warning']
        else:
            difficulty = 'Hard'
            color = self.colors['danger']
        
        ax3.pie([complexity_score, 10-complexity_score], labels=[difficulty, ''], 
                colors=[color, 'lightgray'], autopct='%1.1f%%', startangle=90)
        ax3.set_title('Manufacturing Difficulty Assessment', fontsize=14, fontweight='bold')
        
        # Cost efficiency metrics
        volume = quote_data.get('volume', 0)
        total_cost = quote_data.get('total_cost', 0)
        if volume > 0:
            cost_per_mm3 = total_cost / volume
            industry_benchmarks = {
                'Excellent': 0.0003,
                'Good': 0.0005,
                'Average': 0.0008,
                'Poor': 0.0012
            }
            
            # Determine efficiency rating
            if cost_per_mm3 <= industry_benchmarks['Excellent']:
                rating = 'Excellent'
                rating_color = self.colors['success']
            elif cost_per_mm3 <= industry_benchmarks['Good']:
                rating = 'Good'
                rating_color = self.colors['efficiency']
            elif cost_per_mm3 <= industry_benchmarks['Average']:
                rating = 'Average'
                rating_color = self.colors['warning']
            else:
                rating = 'Poor'
                rating_color = self.colors['danger']
            
            ax4.bar(['Your Quote', 'Industry Avg'], [cost_per_mm3, industry_benchmarks['Good']], 
                    color=[rating_color, 'lightgray'])
            ax4.set_ylabel('Cost per mm³ ($)')
            ax4.set_title(f'Cost Efficiency: {rating}', fontsize=14, fontweight='bold')
            ax4.text(0.5, 0.9, f'Rating: {rating}', transform=ax4.transAxes, 
                    ha='center', va='center', fontsize=12, fontweight='bold', color=rating_color)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def create_manufacturing_workflow_chart(self, quote_data: Dict, save_path: str = None) -> plt.Figure:
        """Create manufacturing workflow and timeline visualization"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Manufacturing workflow steps
        workflow_steps = ['CAD Analysis', 'CAM Programming', 'Material Prep', 'Setup', 'Machining', 'QC', 'Finishing']
        workflow_times = [0.5, 1.0, 0.3, 0.4, 2.0, 0.5, 0.3]  # hours
        
        # Adjust times based on complexity
        complexity_factor = quote_data.get('complexity_score', 5) / 5.0
        workflow_times = [t * complexity_factor for t in workflow_times]
        
        # Create workflow timeline
        y_pos = np.arange(len(workflow_steps))
        bars = ax1.barh(y_pos, workflow_times, color=self.palettes['efficiency'])
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(workflow_steps)
        ax1.set_xlabel('Time (hours)')
        ax1.set_title('Manufacturing Workflow Timeline', fontsize=14, fontweight='bold')
        
        # Add time labels
        for i, (bar, time) in enumerate(zip(bars, workflow_times)):
            ax1.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
                    f'{time:.1f}h', ha='left', va='center', fontweight='bold')
        
        # Lead time breakdown
        lead_time_days = quote_data.get('lead_time_days', 0)
        shipping_tier = quote_data.get('shipping_tier', 'standard')
        
        # Break down lead time components
        if shipping_tier == 'economy':
            processing_days = int(lead_time_days * 0.7)
            shipping_days = lead_time_days - processing_days
        elif shipping_tier == 'expedited':
            processing_days = int(lead_time_days * 0.8)
            shipping_days = lead_time_days - processing_days
        else:
            processing_days = int(lead_time_days * 0.75)
            shipping_days = lead_time_days - processing_days
        
        timeline_data = ['Processing', 'Shipping', 'Buffer']
        timeline_values = [processing_days, shipping_days, 1]
        timeline_colors = [self.colors['labor'], self.colors['material'], 'lightgray']
        
        bars2 = ax2.bar(timeline_data, timeline_values, color=timeline_colors)
        ax2.set_ylabel('Days')
        ax2.set_title(f'Lead Time Breakdown - {shipping_tier.title()} Shipping', fontsize=14, fontweight='bold')
        ax2.set_ylim(0, lead_time_days + 2)
        
        # Add day labels
        for bar, days in zip(bars2, timeline_values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f'{days} days', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def create_cost_breakdown_chart(self, quote_data: Dict, save_path: str = None) -> plt.Figure:
        """Create a pie chart showing cost breakdown"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Cost breakdown pie chart
        cost_labels = ['Material', 'Machine Time', 'Labor', 'Overhead']
        cost_values = [
            quote_data.get('material_cost', 0),
            quote_data.get('machine_time_cost', 0),
            quote_data.get('labor_cost', 0),
            quote_data.get('overhead_cost', 0)
        ]
        
        # Filter out zero values
        non_zero_costs = [(label, value) for label, value in zip(cost_labels, cost_values) if value > 0]
        if non_zero_costs:
            labels, values = zip(*non_zero_costs)
            colors = [self.colors['material'], self.colors['machine_time'], 
                     self.colors['labor'], self.colors['overhead']][:len(values)]
            
            ax1.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
            ax1.set_title('Cost Breakdown', fontsize=14, fontweight='bold')
        
        # Cost breakdown bar chart
        x_pos = np.arange(len(cost_labels))
        bars = ax2.bar(x_pos, cost_values, color=[self.colors['material'], self.colors['machine_time'], 
                                                  self.colors['labor'], self.colors['overhead']])
        ax2.set_xlabel('Cost Components')
        ax2.set_ylabel('Cost ($)')
        ax2.set_title('Cost Breakdown by Component', fontsize=14, fontweight='bold')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(cost_labels, rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars, cost_values):
            if value > 0:
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01 * max(cost_values),
                        f'${value:.2f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def create_complexity_analysis_chart(self, quote_data: Dict, save_path: str = None) -> plt.Figure:
        """Create charts showing complexity analysis"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Complexity score gauge
        complexity_score = quote_data.get('complexity_score', 0)
        ax1.add_patch(patches.Wedge((0.5, 0.5), 0.4, 0, 180, 
                                   color=self.colors['complexity'], alpha=0.7))
        ax1.add_patch(patches.Wedge((0.5, 0.5), 0.4, 180, 360, 
                                   color='lightgray', alpha=0.3))
        
        # Add complexity score text
        ax1.text(0.5, 0.5, f'{complexity_score:.1f}', ha='center', va='center', 
                fontsize=24, fontweight='bold')
        ax1.text(0.5, 0.3, 'Complexity Score', ha='center', va='center', 
                fontsize=12)
        ax1.text(0.5, 0.2, '0 = Simple, 10 = Complex', ha='center', va='center', 
                fontsize=10, style='italic')
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.set_aspect('equal')
        ax1.axis('off')
        ax1.set_title('Part Complexity Score', fontsize=14, fontweight='bold')
        
        # Part dimensions visualization
        dimensions = quote_data.get('bounding_box', {})
        if dimensions:
            length = dimensions.get('length', 0)
            width = dimensions.get('width', 0)
            height = dimensions.get('height', 0)
            
            # Create 3D-like representation
            x = [0, length, length, 0, 0]
            y = [0, 0, width, width, 0]
            ax2.plot(x, y, 'b-', linewidth=2, label='Base')
            ax2.fill(x, y, alpha=0.3, color='blue')
            
            # Add height indicator
            ax2.plot([0, 0], [0, 0], [0, height], 'r-', linewidth=3, label='Height')
            ax2.set_xlabel('Length (mm)')
            ax2.set_ylabel('Width (mm)')
            ax2.set_title('Part Dimensions', fontsize=14, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            ax2.legend()
        
        # Volume vs Surface Area
        volume = quote_data.get('volume', 0)
        surface_area = quote_data.get('surface_area', 0)
        
        ax3.scatter(volume, surface_area, s=200, c=self.colors['efficiency'], alpha=0.7)
        ax3.set_xlabel('Volume (mm³)')
        ax3.set_ylabel('Surface Area (mm²)')
        ax3.set_title('Volume vs Surface Area', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        # Add annotation
        ax3.annotate(f'V: {volume:.0f} mm³\nSA: {surface_area:.0f} mm²', 
                     (volume, surface_area), xytext=(10, 10), 
                     textcoords='offset points', bbox=dict(boxstyle='round,pad=0.3', 
                     facecolor='yellow', alpha=0.7))
        
        # Material efficiency
        material_waste = quote_data.get('material_waste_percentage', 0)
        efficiency = 100 - material_waste
        
        ax4.bar(['Efficiency', 'Waste'], [efficiency, material_waste], 
                color=[self.colors['efficiency'], 'lightcoral'])
        ax4.set_ylabel('Percentage (%)')
        ax4.set_title('Material Efficiency', fontsize=14, fontweight='bold')
        ax4.set_ylim(0, 100)
        
        # Add value labels
        ax4.text(0, efficiency/2, f'{efficiency:.1f}%', ha='center', va='center', 
                fontweight='bold', fontsize=12)
        ax4.text(1, material_waste/2, f'{material_waste:.1f}%', ha='center', va='center', 
                fontweight='bold', fontsize=12)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def create_pricing_comparison_chart(self, quote_data: Dict, save_path: str = None) -> plt.Figure:
        """Create charts showing pricing analysis and comparisons"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Per-unit vs total cost
        per_unit = quote_data.get('per_unit_cost', 0)
        total_cost = quote_data.get('total_cost', 0)
        quantity = quote_data.get('quantity', 1)
        
        if quantity > 1:
            ax1.bar(['Per Unit', 'Total'], [per_unit, total_cost], 
                    color=[self.colors['total'], self.colors['material']])
            ax1.set_ylabel('Cost ($)')
            ax1.set_title(f'Cost Comparison (Quantity: {quantity})', fontsize=14, fontweight='bold')
            
            # Add value labels
            ax1.text(0, per_unit/2, f'${per_unit:.2f}', ha='center', va='center', 
                    fontweight='bold', fontsize=12)
            ax1.text(1, total_cost/2, f'${total_cost:.2f}', ha='center', va='center', 
                    fontweight='bold', fontsize=12)
        
        # Lead time analysis
        lead_time = quote_data.get('lead_time_days', 0)
        shipping_tier = quote_data.get('shipping_tier', 'standard')
        
        # Create timeline visualization
        timeline_colors = {'economy': 'orange', 'standard': 'green', 'expedited': 'red'}
        color = timeline_colors.get(shipping_tier, 'blue')
        
        ax2.barh(['Lead Time'], [lead_time], color=color, alpha=0.7)
        ax2.set_xlabel('Days')
        ax2.set_title(f'Lead Time - {shipping_tier.title()} Shipping', fontsize=14, fontweight='bold')
        ax2.text(lead_time/2, 0, f'{lead_time} days', ha='center', va='center', 
                fontweight='bold', fontsize=14)
        
        # Cost per mm³ analysis
        volume = quote_data.get('volume', 0)
        if volume > 0:
            cost_per_mm3 = total_cost / volume if volume > 0 else 0
            
            # Industry benchmark comparison (example values)
            industry_avg = 0.0005  # $0.0005 per mm³ (example)
            
            ax3.bar(['Your Quote', 'Industry Avg'], [cost_per_mm3, industry_avg], 
                    color=[self.colors['total'], 'lightgray'])
            ax3.set_ylabel('Cost per mm³ ($)')
            ax3.set_title('Cost Efficiency Analysis', fontsize=14, fontweight='bold')
            ax3.grid(True, alpha=0.3)
        
        # Quantity discount analysis
        if 'quantity_discounts' in quote_data:
            quantities = list(quote_data['quantity_discounts'].keys())
            discounts = list(quote_data['quantity_discounts'].values())
            
            ax4.plot(quantities, discounts, 'o-', color=self.colors['efficiency'], 
                     linewidth=2, markersize=8)
            ax4.set_xlabel('Quantity')
            ax4.set_ylabel('Discount (%)')
            ax4.set_title('Quantity Discounts', fontsize=14, fontweight='bold')
            ax4.grid(True, alpha=0.3)
            ax4.set_xticks(quantities)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def create_interactive_dashboard(self, quote_data: Dict, save_path: str = None) -> str:
        """Create an interactive Plotly dashboard"""
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Cost Breakdown', 'Part Dimensions', 'Complexity Analysis', 
                           'Material Efficiency', 'Pricing Trends', 'Lead Time'),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "indicator"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "bar"}]]
        )
        
        # 1. Cost Breakdown Pie Chart
        cost_labels = ['Material', 'Machine Time', 'Labor', 'Overhead']
        cost_values = [
            quote_data.get('material_cost', 0),
            quote_data.get('machine_time_cost', 0),
            quote_data.get('labor_cost', 0),
            quote_data.get('overhead_cost', 0)
        ]
        
        # Filter out zero values
        non_zero_costs = [(label, value) for label, value in zip(cost_labels, cost_values) if value > 0]
        if non_zero_costs:
            labels, values = zip(*non_zero_costs)
            fig.add_trace(
                go.Pie(labels=labels, values=values, name="Cost Breakdown"),
                row=1, col=1
            )
        
        # 2. Part Dimensions Bar Chart
        dimensions = quote_data.get('bounding_box', {})
        if dimensions:
            dim_names = list(dimensions.keys())
            dim_values = list(dimensions.values())
            fig.add_trace(
                go.Bar(x=dim_names, y=dim_values, name="Dimensions (mm)", 
                       marker_color='lightblue'),
                row=1, col=2
            )
        
        # 3. Complexity Score Gauge
        complexity_score = quote_data.get('complexity_score', 0)
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=complexity_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Complexity Score"},
                gauge={'axis': {'range': [0, 10]},
                       'bar': {'color': "darkblue"},
                       'steps': [{'range': [0, 3], 'color': "lightgreen"},
                                {'range': [3, 7], 'color': "yellow"},
                                {'range': [7, 10], 'color': "red"}]}
            ),
            row=2, col=1
        )
        
        # 4. Material Efficiency
        material_waste = quote_data.get('material_waste_percentage', 0)
        efficiency = 100 - material_waste
        fig.add_trace(
            go.Bar(x=['Efficiency', 'Waste'], y=[efficiency, material_waste],
                   marker_color=['green', 'red'], name="Material Efficiency (%)"),
            row=2, col=2
        )
        
        # 5. Cost vs Volume Scatter
        volume = quote_data.get('volume', 0)
        total_cost = quote_data.get('total_cost', 0)
        if volume > 0:
            fig.add_trace(
                go.Scatter(x=[volume], y=[total_cost], mode='markers',
                           marker=dict(size=15, color='red'), name="Cost vs Volume"),
                row=3, col=1
            )
        
        # 6. Lead Time Bar
        lead_time = quote_data.get('lead_time_days', 0)
        shipping_tier = quote_data.get('shipping_tier', 'standard')
        fig.add_trace(
            go.Bar(x=[f'{shipping_tier.title()} Shipping'], y=[lead_time],
                   marker_color='orange', name="Lead Time (days)"),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text=f"CAD Quoting Engine Dashboard - {quote_data.get('part_name', 'Part Analysis')}",
            showlegend=True,
            height=800
        )
        
        # Save as HTML if path provided
        if save_path:
            fig.write_html(save_path)
        
        return fig.to_html(include_plotlyjs='cdn')
    
    def create_summary_report(self, quote_data: Dict, save_path: str = None) -> str:
        """Create a comprehensive summary report with visualizations"""
        report_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>CAD Quoting Engine Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; border-bottom: 3px solid #4ECDC4; padding-bottom: 20px; margin-bottom: 30px; }}
                .section {{ margin-bottom: 30px; padding: 20px; border-left: 4px solid #4ECDC4; background-color: #f9f9f9; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; background-color: #4ECDC4; color: white; border-radius: 5px; text-align: center; min-width: 120px; }}
                .metric-value {{ font-size: 24px; font-weight: bold; }}
                .metric-label {{ font-size: 12px; }}
                .cost-breakdown {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .cost-item {{ text-align: center; padding: 10px; }}
                .cost-amount {{ font-size: 20px; font-weight: bold; color: #FF6B6B; }}
                .cost-label {{ font-size: 14px; color: #666; }}
                .complexity-meter {{ width: 100%; height: 30px; background-color: #ddd; border-radius: 15px; overflow: hidden; margin: 10px 0; }}
                .complexity-fill {{ height: 100%; background: linear-gradient(90deg, #4ECDC4, #FF6B6B); width: {min(quote_data.get('complexity_score', 0) * 10, 100)}%; }}
                .dimensions {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .dimension {{ text-align: center; }}
                .dimension-value {{ font-size: 18px; font-weight: bold; color: #45B7D1; }}
                .dimension-label {{ font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏭 CAD Quoting Engine Report</h1>
                    <h2>{quote_data.get('part_name', 'Part Analysis')}</h2>
                    <p>Generated on {quote_data.get('timestamp', 'Unknown')}</p>
                </div>
                
                <div class="section">
                    <h3>📊 Key Metrics</h3>
                    <div class="metric">
                        <div class="metric-value">${quote_data.get('per_unit_cost', 0):.2f}</div>
                        <div class="metric-label">Per Unit Cost</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${quote_data.get('total_cost', 0):.2f}</div>
                        <div class="metric-label">Total Cost</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{quote_data.get('lead_time_days', 0)}</div>
                        <div class="metric-label">Lead Time (Days)</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{quote_data.get('complexity_score', 0):.1f}/10</div>
                        <div class="metric-label">Complexity Score</div>
                    </div>
                </div>
                
                <div class="section">
                    <h3>💰 Cost Breakdown</h3>
                    <div class="cost-breakdown">
                        <div class="cost-item">
                            <div class="cost-amount">${quote_data.get('material_cost', 0):.2f}</div>
                            <div class="cost-label">Material</div>
                        </div>
                        <div class="cost-item">
                            <div class="cost-amount">${quote_data.get('machine_time_cost', 0):.2f}</div>
                            <div class="cost-label">Machine Time</div>
                        </div>
                        <div class="cost-item">
                            <div class="cost-amount">${quote_data.get('labor_cost', 0):.2f}</div>
                            <div class="cost-label">Labor</div>
                        </div>
                        <div class="cost-item">
                            <div class="cost-amount">${quote_data.get('overhead_cost', 0):.2f}</div>
                            <div class="cost-label">Overhead</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h3>📐 Part Analysis</h3>
                    <div class="dimensions">
                        <div class="dimension">
                            <div class="dimension-value">{quote_data.get('bounding_box', {}).get('length', 0):.1f} mm</div>
                            <div class="dimension-label">Length</div>
                        </div>
                        <div class="dimension">
                            <div class="dimension-value">{quote_data.get('bounding_box', {}).get('width', 0):.1f} mm</div>
                            <div class="dimension-label">Width</div>
                        </div>
                        <div class="dimension">
                            <div class="dimension-value">{quote_data.get('bounding_box', {}).get('height', 0):.1f} mm</div>
                            <div class="dimension-label">Height</div>
                        </div>
                    </div>
                    <p><strong>Volume:</strong> {quote_data.get('volume', 0):.1f} mm³</p>
                    <p><strong>Surface Area:</strong> {quote_data.get('surface_area', 0):.1f} mm²</p>
                </div>
                
                <div class="section">
                    <h3>🎯 Complexity Analysis</h3>
                    <div class="complexity-meter">
                        <div class="complexity-fill"></div>
                    </div>
                    <p>Complexity Score: {quote_data.get('complexity_score', 0):.1f}/10</p>
                    <p><strong>Features Detected:</strong></p>
                    <ul>
                        <li>Holes: {quote_data.get('feature_counts', {}).get('holes', 0)}</li>
                        <li>Cavities: {quote_data.get('feature_counts', {}).get('cavities', 0)}</li>
                        <li>Pockets: {quote_data.get('feature_counts', {}).get('pockets', 0)}</li>
                        <li>Sharp Edges: {quote_data.get('feature_counts', {}).get('sharp_edges', 0)}</li>
                    </ul>
                </div>
                
                <div class="section">
                    <h3>📦 Material & Shipping</h3>
                    <p><strong>Material:</strong> 6061 Aluminum</p>
                    <p><strong>Material Waste:</strong> {quote_data.get('material_waste_percentage', 0):.1f}%</p>
                    <p><strong>Shipping Tier:</strong> {quote_data.get('shipping_tier', 'Standard').title()}</p>
                    <p><strong>Quantity:</strong> {quote_data.get('quantity', 1)}</p>
                    {f'<p><strong>Quantity Discount:</strong> {quote_data.get("quantity_discount_percentage", 0):.1f}%</p>' if quote_data.get('quantity', 1) > 1 else ''}
                </div>
            </div>
        </body>
        </html>
        """
        
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(report_html)
        
        return report_html
    
    def create_batch_analysis_chart(self, batch_results: List[Dict], save_path: str = None) -> plt.Figure:
        """Create charts comparing multiple parts in a batch"""
        if not batch_results:
            return None
            
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Extract data
        part_names = [result.get('part_name', f'Part {i+1}') for i, result in enumerate(batch_results)]
        costs = [result.get('per_unit_cost', 0) for result in batch_results]
        complexities = [result.get('complexity_score', 0) for result in batch_results]
        volumes = [result.get('volume', 0) for result in batch_results]
        lead_times = [result.get('lead_time_days', 0) for result in batch_results]
        
        # 1. Cost comparison
        bars1 = ax1.bar(part_names, costs, color=self.colors['total'])
        ax1.set_ylabel('Cost ($)')
        ax1.set_title('Cost Comparison Across Parts', fontsize=14, fontweight='bold')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar, cost in zip(bars1, costs):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01 * max(costs),
                    f'${cost:.0f}', ha='center', va='bottom', fontweight='bold')
        
        # 2. Complexity comparison
        bars2 = ax2.bar(part_names, complexities, color=self.colors['complexity'])
        ax2.set_ylabel('Complexity Score')
        ax2.set_title('Complexity Comparison', fontsize=14, fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)
        ax2.set_ylim(0, 10)
        
        # 3. Volume vs Cost scatter
        ax3.scatter(volumes, costs, s=100, c=self.colors['efficiency'], alpha=0.7)
        ax3.set_xlabel('Volume (mm³)')
        ax3.set_ylabel('Cost ($)')
        ax3.set_title('Volume vs Cost Relationship', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        # Add part labels
        for i, (vol, cost, name) in enumerate(zip(volumes, costs, part_names)):
            ax3.annotate(name, (vol, cost), xytext=(5, 5), textcoords='offset points', 
                        fontsize=8, bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
        
        # 4. Lead time comparison
        bars4 = ax4.bar(part_names, lead_times, color=self.colors['labor'])
        ax4.set_ylabel('Lead Time (Days)')
        ax4.set_title('Lead Time Comparison', fontsize=14, fontweight='bold')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig

def main():
    """Example usage of the visualizer"""
    # Sample data for demonstration
    sample_quote = {
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
    }
    
    visualizer = CADVisualizer()
    
    # Create output directory
    os.makedirs('outputs', exist_ok=True)
    
    # Generate all visualizations
    print("Generating visualizations...")
    
    # 1. Cost breakdown chart
    fig1 = visualizer.create_cost_breakdown_chart(sample_quote, 'outputs/cost_breakdown.png')
    print("Cost breakdown chart saved to outputs/cost_breakdown.png")
    
    # 2. Complexity analysis chart
    fig2 = visualizer.create_complexity_analysis_chart(sample_quote, 'outputs/complexity_analysis.png')
    print("Complexity analysis chart saved to outputs/complexity_analysis.png")
    
    # 3. Pricing comparison chart
    fig3 = visualizer.create_pricing_comparison_chart(sample_quote, 'outputs/pricing_comparison.png')
    print("Pricing comparison chart saved to outputs/pricing_comparison.png")
    
    # 4. Feature analysis chart
    fig4 = visualizer.create_feature_analysis_chart(sample_quote, 'outputs/feature_analysis.png')
    print("Feature analysis chart saved to outputs/feature_analysis.png")
    
    # 5. Manufacturing workflow chart
    fig5 = visualizer.create_manufacturing_workflow_chart(sample_quote, 'outputs/manufacturing_workflow.png')
    print("Manufacturing workflow chart saved to outputs/manufacturing_workflow.png")
    
    # 6. Interactive dashboard
    dashboard_html = visualizer.create_interactive_dashboard(sample_quote, 'outputs/interactive_dashboard.html')
    print("Interactive dashboard saved to outputs/interactive_dashboard.html")
    
    # 7. Summary report
    report_html = visualizer.create_summary_report(sample_quote, 'outputs/summary_report.html')
    print("Summary report saved to outputs/summary_report.html")
    
    print("\nAll visualizations generated successfully!")
    print("Check the 'outputs' folder for all generated files.")

if __name__ == "__main__":
    main()
