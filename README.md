# CAD Quoting Engine

A Python-based CAD quoting engine that analyzes 3D STEP files and estimates CNC machining costs for 6061 Aluminum parts.

## Overview

This project implements an automated quoting system for CNC machining that analyzes 3D CAD files and provides cost estimates based on:
- Part geometry analysis (volume, surface area, complexity)
- Material costs (6061 Aluminum)
- Machine time estimation using multi-phase milling approach
- Labor costs for various operations
- Quantity discounts
- Lead time estimation

## Features

### Geometry Analysis
- ✅ Calculate bounding box dimensions (length, width, height)
- ✅ Calculate part volume and surface area
- ✅ Detect part complexity based on surface area to volume ratio, face count, and edge count
- ✅ Automatic block size selection for raw material

### Cost Estimation Logic
- ✅ Material cost calculation based on volume × density × price per unit mass
- ✅ Machine time estimation using three-phase milling approach:
  - Coarse milling (350 mm³/sec)
  - Medium milling (100 mm³/sec) 
  - Fine milling (20 mm³/sec)
- ✅ Labor costs for programming, setup, QC, and finishing
- ✅ Complexity multipliers based on part features
- ✅ Feature detection for holes, cavities, sharp edges, and pockets
- ✅ Quantity discounts with tiered pricing
- ✅ Expedited shipping options

### Lead Time Estimation
- ✅ Lead times based on part complexity
- ✅ Setup time considerations
- ✅ Workday assumptions with efficiency factors

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd cad-quoting-engine
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Basic usage:
```bash
python src/main.py data/suspension-mount.step
```

With quantity:
```bash
python src/main.py data/suspension-mount.step --quantity 10
```

Save results to JSON:
```bash
python src/main.py data/suspension-mount.step --quantity 5 --output quote_results.json
```

### Command Line Options

- `step_file`: Path to the STEP file (required)
- `--quantity, -q`: Quantity of parts (default: 1)
- `--expedited, -e`: Expedited shipping option (5_days, 4_days, 3_days)
- `--output, -o`: Output JSON file path (optional)

## Methodology

### Pricing Approach

The quoting engine uses a three-phase milling approach:

1. **Coarse Milling**: Removes bulk material to create the rough outline
2. **Medium Milling**: Refines the shape to approximate the final part
3. **Fine Milling**: Final finishing to achieve the exact part geometry

### Cost Rates
- **Coarse milling**: $0.00011/mm³
- **Medium milling**: $0.00039/mm³
- **Fine milling**: $0.00175/mm³

### Labor Costs
- **CAD/CAM Programming**: $110/hour
- **Machine Setup**: $65/hour
- **Tool Setup**: $55/hour
- **Quality Inspection**: $65/hour
- **Deburring/Finishing**: $45/hour
- **Project Management**: $85/hour

### Baseline Specification Data
- **Aluminum 6061 Density**: 2.7 g/cm³
- **Aluminum Price**: $5.00/kg
- **CNC Machine Type**: Haas CNC Machines
- **CNC Machining Rate**: $100/hour

### Industry Standards
- **Material Waste Target**: 20-40% (industry optimal)
- **Block Size Selection**: Smart optimization for minimal waste
- **Material Efficiency**: Real-time analysis and reporting

### Volume Calculations

- **Block Volume**: Raw material block size (automatically selected)
- **Convex Hull Volume**: Coarse outline of the part
- **Shrink Wrap Volume**: Approximated as 80% of convex hull volume
- **Part Volume**: Actual part volume

### Cost Factors

1. **Material Cost**: `volume_cm³ × density_g/cm³ × price_per_kg`
2. **Machine Time Cost**: Sum of three milling phases with different rates
3. **Labor Costs**: Programming, setup, QC, and finishing operations
4. **Complexity Multiplier**: Based on surface area to volume ratio, face count, and edge count
5. **Quantity Multiplier**: Tiered discounts for larger quantities

### Complexity Scoring

The complexity score (0-10) is calculated using:
- Surface area to volume ratio (40% weight)
- Face count normalized to 1000 faces (30% weight)
- Edge count normalized to 1000 edges (30% weight)

## Technical Details

### Dependencies

- **trimesh**: 3D mesh processing and STEP file loading
- **numpy**: Numerical computations

### Key Classes

- `CADQuotingEngine`: Main engine class for cost calculations
- `QuoteResult`: Data class for storing quote results

### File Structure

```
cad-quoting-engine/
├── src/
│   └── main.py              # Main quoting engine
├── data/                    # Sample STEP files
│   ├── suspension-mount.step
│   ├── piston-head.STEP
│   ├── control-bracket.STEP
│   ├── test-gear.STEP
│   └── Pump Manifold v3.step
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── venv/                   # Virtual environment
```

## Assumptions and Limitations

### Assumptions Made

1. **Material**: 6061 Aluminum (density: 2.7 g/cm³, price: $5.00/kg) - Baseline specification
2. **Machine Rate**: $100/hour for Haas CNC Machines - Baseline specification
3. **Block Sizes**: Industry-optimized sizes from 25×25×25mm to 600×500×500mm
4. **Setup Time**: 0.4 hours base setup time
5. **Shrink Wrap Volume**: Approximated as 80% of convex hull volume
6. **Minimum Price**: $200.00 per part
7. **Material Waste**: Industry-standard 20-40% target (not excessive waste)

### Limitations

1. **Simplified Geometry**: Complex features like threads, undercuts, and internal cavities may not be accurately represented
2. **Material Removal**: Assumes uniform material removal rates
3. **Tolerance**: Does not account for tight tolerances or surface finish requirements
4. **Setup Complexity**: Simplified setup time estimation
5. **Machine Specifics**: Generic machine capabilities, not specific to particular CNC models

## Current Features

1. **Lead Times**: Based on part complexity
2. **Expedited Shipping**: 5-day (+30%), 4-day (+60%), 3-day (+100%) options
3. **Quantity Discounts**: Bulk pricing with 5-28% discounts for larger orders
4. **Complexity Scoring**: Based on surface area, face count, and edge count
5. **Size-Based Pricing**: Adjustments for small, medium, and large parts
6. **Three-Phase Milling**: Coarse, medium, and fine milling cost calculation
7. **Labor Costs**: Comprehensive labor cost breakdown
8. **Industry-Standard Material Optimization**: Smart block size selection with 20-40% waste target
9. **Material Efficiency Analysis**: Real-time waste percentage and efficiency reporting
10. **Feature Detection**: Advanced detection of holes, cavities, sharp edges, and pockets

## Future Enhancements

1. **Advanced Geometry Analysis**: Better detection of holes, pockets, threads, and complex features
2. **Material Selection**: Support for multiple materials (steel, titanium, plastics)
3. **Tolerance Analysis**: Cost impact of tight tolerances and surface finishes
4. **Machine Selection**: Different machine types and capabilities
5. **Setup Optimization**: More sophisticated setup time estimation
6. **Batch Processing**: Process multiple files simultaneously
7. **Web Interface**: REST API or web application
8. **Database Integration**: Store historical quotes and pricing data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
