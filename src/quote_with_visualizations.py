#!/usr/bin/env python3
"""
CAD Quoting Engine with Integrated Visualizations
This script runs the CAD quoting engine and automatically generates visualizations
"""

import os
import sys
import json
from pathlib import Path
import argparse

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent))

from main import CADQuotingEngine
from visualizer import CADVisualizer

def run_quote_with_visualizations(step_file_path: str, quantity: int = 1, 
                                shipping: str = 'standard', output_file: str = None,
                                generate_visualizations: bool = True):
    """
    Run the CAD quoting engine and generate visualizations
    
    Args:
        step_file_path: Path to the STEP file
        quantity: Number of parts to quote
        shipping: Shipping tier (economy, standard, expedited)
        output_file: Optional JSON output file path
        generate_visualizations: Whether to generate visualizations
    """
    
    print(f"🏭 CAD Quoting Engine with Visualizations")
    print("=" * 50)
    
    # Initialize the quoting engine
    engine = CADQuotingEngine()
    
    # Get the part name from the file path
    part_name = Path(step_file_path).stem
    
    print(f"📁 Processing: {part_name}")
    print(f"📊 Quantity: {quantity}")
    print(f"🚚 Shipping: {shipping}")
    print()
    
    try:
        # Generate the quote
        print("🔄 Analyzing 3D geometry and calculating costs...")
        mesh = engine.load_step_file(step_file_path)
        quote_result = engine.calculate_costs(
            mesh, 
            quantity, 
            None,  # expedited option
            shipping, 
            part_name
        )
        
        # Convert quote result to dictionary for visualization
        quote_data = {
            'part_name': part_name,
            'per_unit_cost': quote_result.per_unit_cost,
            'total_cost': quote_result.total_cost,
            'material_cost': quote_result.breakdown.get('material_cost', 0),
            'machine_time_cost': quote_result.breakdown.get('machine_time_cost', 0),
            'labor_cost': quote_result.breakdown.get('labor_cost', 0),
            'overhead_cost': quote_result.breakdown.get('overhead_cost', 0),
            'bounding_box': quote_result.bounding_box,
            'volume': quote_result.volume,
            'surface_area': quote_result.surface_area,
            'complexity_score': quote_result.complexity_score,
            'lead_time_days': quote_result.lead_time_days,
            'shipping_tier': shipping,
            'quantity': quantity,
            'material_waste_percentage': getattr(quote_result, 'material_waste_percentage', 0),
            'feature_counts': getattr(quote_result, 'feature_counts', {}),
            'timestamp': getattr(quote_result, 'timestamp', 'Unknown')
        }
        
        # Add quantity discount information if applicable
        if quantity > 1:
            discount_percentage = ((quote_data['per_unit_cost'] * quantity - quote_data['total_cost']) / 
                                 (quote_data['per_unit_cost'] * quantity)) * 100
            quote_data['quantity_discount_percentage'] = discount_percentage
        
        # Display quote summary
        print("✅ Quote Generated Successfully!")
        print(f"💰 Per Unit Cost: ${quote_data['per_unit_cost']:.2f}")
        print(f"💰 Total Cost: ${quote_data['total_cost']:.2f}")
        print(f"⏰ Lead Time: {quote_data['lead_time_days']} days")
        print(f"🎯 Complexity Score: {quote_data['complexity_score']:.1f}/10")
        print()
        
        # Save to JSON if requested
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(quote_data, f, indent=2)
            print(f"💾 Quote saved to: {output_file}")
            print()
        
        # Generate visualizations if requested
        if generate_visualizations:
            print("🎨 Generating Visualizations...")
            visualizer = CADVisualizer()
            
            # Create output directory
            output_dir = f"outputs/{part_name.replace(' ', '_')}"
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate all visualization types
            print("  📊 Creating cost breakdown chart...")
            visualizer.create_cost_breakdown_chart(
                quote_data, 
                f"{output_dir}/cost_breakdown.png"
            )
            
            print("  🎯 Creating complexity analysis chart...")
            visualizer.create_complexity_analysis_chart(
                quote_data, 
                f"{output_dir}/complexity_analysis.png"
            )
            
            print("  💰 Creating pricing comparison chart...")
            visualizer.create_pricing_comparison_chart(
                quote_data, 
                f"{output_dir}/pricing_comparison.png"
            )
            
            print("  🔍 Creating feature analysis chart...")
            visualizer.create_feature_analysis_chart(
                quote_data, 
                f"{output_dir}/feature_analysis.png"
            )
            
            print("  ⚙️  Creating manufacturing workflow chart...")
            visualizer.create_manufacturing_workflow_chart(
                quote_data, 
                f"{output_dir}/manufacturing_workflow.png"
            )
            
            # Try to create 3D visualization if mesh is available
            try:
                print("  🎨 Creating 3D part visualization...")
                mesh = engine.load_step_file(step_file_path)
                visualizer.create_3d_part_visualization(mesh, f"{output_dir}/3d_visualization.png")
                print("    ✓ 3D visualization created successfully")
            except Exception as e:
                print(f"    ⚠️  3D visualization skipped: {e}")
            
            print("  🖥️  Creating interactive dashboard...")
            visualizer.create_interactive_dashboard(
                quote_data, 
                f"{output_dir}/interactive_dashboard.html"
            )
            
            print("  📋 Creating summary report...")
            visualizer.create_summary_report(
                quote_data, 
                f"{output_dir}/summary_report.html"
            )
            
            print(f"\n✅ All visualizations saved to: {output_dir}/")
            print("📁 Files generated:")
            print("   • cost_breakdown.png - Cost breakdown charts")
            print("   • complexity_analysis.png - Complexity and geometry analysis")
            print("   • pricing_comparison.png - Pricing and efficiency analysis")
            print("   • feature_analysis.png - Feature complexity and cost impact analysis")
            print("   • manufacturing_workflow.png - Manufacturing timeline and workflow")
            print("   • 3d_visualization.png - 3D part visualization with bounding box")
            print("   • interactive_dashboard.html - Interactive Plotly dashboard")
            print("   • summary_report.html - Professional HTML report")
        
        return quote_data
        
    except Exception as e:
        print(f"❌ Error generating quote: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_batch_analysis(step_files: list, quantity: int = 1, shipping: str = 'standard'):
    """
    Run batch analysis on multiple STEP files
    
    Args:
        step_files: List of STEP file paths
        quantity: Number of parts to quote
        shipping: Shipping tier
    """
    
    print(f"📈 Batch Analysis - {len(step_files)} Parts")
    print("=" * 50)
    
    all_quotes = []
    
    for i, step_file in enumerate(step_files, 1):
        print(f"\n📁 Processing {i}/{len(step_files)}: {Path(step_file).stem}")
        
        quote_data = run_quote_with_visualizations(
            step_file, 
            quantity=quantity, 
            shipping=shipping,
            generate_visualizations=False  # We'll generate batch visualizations later
        )
        
        if quote_data:
            all_quotes.append(quote_data)
    
    if all_quotes:
        print(f"\n🎨 Generating Batch Visualizations...")
        visualizer = CADVisualizer()
        
        # Create batch output directory
        batch_dir = "outputs/batch_analysis"
        os.makedirs(batch_dir, exist_ok=True)
        
        # Generate batch comparison chart
        print("  📊 Creating batch comparison chart...")
        visualizer.create_batch_analysis_chart(
            all_quotes, 
            f"{batch_dir}/batch_comparison.png"
        )
        
        # Generate individual visualizations for each part
        for quote_data in all_quotes:
            part_name = quote_data['part_name'].replace(' ', '_')
            part_dir = f"{batch_dir}/{part_name}"
            os.makedirs(part_dir, exist_ok=True)
            
            print(f"  🎨 Creating visualizations for {quote_data['part_name']}...")
            
            visualizer.create_cost_breakdown_chart(
                quote_data, 
                f"{part_dir}/cost_breakdown.png"
            )
            
            visualizer.create_complexity_analysis_chart(
                quote_data, 
                f"{part_dir}/complexity_analysis.png"
            )
            
            visualizer.create_summary_report(
                quote_data, 
                f"{part_dir}/summary_report.html"
            )
        
        print(f"\n✅ Batch analysis completed! Check: {batch_dir}/")
        
        # Save batch results to JSON
        batch_file = f"{batch_dir}/batch_results.json"
        with open(batch_file, 'w') as f:
            json.dump(all_quotes, f, indent=2)
        print(f"💾 Batch results saved to: {batch_file}")

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description="CAD Quoting Engine with Integrated Visualizations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate quote with visualizations for a single part
  python quote_with_visualizations.py data/suspension-mount.step
  
  # Generate quote for 10 parts with economy shipping
  python quote_with_visualizations.py data/suspension-mount.step --quantity 10 --shipping economy
  
  # Generate quote and save to JSON file
  python quote_with_visualizations.py data/suspension-mount.step --output my_quote.json
  
  # Run batch analysis on all STEP files in data directory
  python quote_with_visualizations.py --batch data/*.step
  
  # Run batch analysis with specific quantity and shipping
  python quote_with_visualizations.py --batch data/*.step --quantity 5 --shipping expedited
        """
    )
    
    parser.add_argument('step_file', nargs='?', help='Path to STEP file')
    parser.add_argument('--batch', nargs='+', help='Batch process multiple STEP files')
    parser.add_argument('--quantity', '-q', type=int, default=1, help='Quantity of parts (default: 1)')
    parser.add_argument('--shipping', '-s', choices=['economy', 'standard', 'expedited'], 
                       default='standard', help='Shipping tier (default: standard)')
    parser.add_argument('--output', '-o', help='Output JSON file path')
    parser.add_argument('--no-viz', action='store_true', help='Skip visualization generation')
    
    args = parser.parse_args()
    
    if args.batch:
        # Batch processing mode
        if not args.batch:
            print("❌ Error: No STEP files specified for batch processing")
            return
        
        # Expand glob patterns
        step_files = []
        for pattern in args.batch:
            if '*' in pattern:
                import glob
                step_files.extend(glob.glob(pattern))
            else:
                step_files.append(pattern)
        
        if not step_files:
            print("❌ Error: No STEP files found matching the patterns")
            return
        
        print(f"🔍 Found {len(step_files)} STEP files for batch processing")
        run_batch_analysis(step_files, args.quantity, args.shipping)
        
    elif args.step_file:
        # Single file processing mode
        if not os.path.exists(args.step_file):
            print(f"❌ Error: STEP file not found: {args.step_file}")
            return
        
        run_quote_with_visualizations(
            args.step_file,
            quantity=args.quantity,
            shipping=args.shipping,
            output_file=args.output,
            generate_visualizations=not args.no_viz
        )
        
    else:
        print("❌ Error: Please specify a STEP file or use --batch for multiple files")
        parser.print_help()

if __name__ == "__main__":
    main()
