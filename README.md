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
- **NEW**: Shipping tiers (Economy, Standard, Expedited)

## What You'll See When You Run It

When you run the quoting engine, you'll get a **detailed cost breakdown** including:

 **Cost Summary**
- Per unit cost and total cost
- Material cost breakdown (now scales properly with quantity)
- Machine time cost (coarse/medium/fine milling) - per part AND total
- Labor costs (programming, setup, QC, finishing) - per part AND total

 **Part Analysis**
- Dimensions (length × width × height)
- Volume and surface area
- Complexity score (0-10 scale)
- Detected features (holes, cavities, pockets, sharp edges)

 **Material Efficiency**
- Raw material block size needed
- Material waste percentage
- Industry-standard optimization analysis

 **Pricing Details**
- Quantity discounts applied (fixed exponential growth issue)
- Complexity and size multipliers
- **NEW**: Shipping tier options (Economy/Standard/Expedited)
- Lead time estimation (now scales with quantity)

**Example Output**: Run `python src/main.py data/suspension-mount.step` to see a complete quote for a sample part!

## Recent Improvements (v2.0)

### Fixed Major Issues
- **Material costs now scale properly** with quantity (was stuck at $2.43)
- **Eliminated exponential cost growth** with quantity increases
- **Milling costs now scale** with number of parts
- **Labor costs now scale** with number of parts  
- **Lead time now scales** with quantity (was fixed at 11 days)
- **Added shipping tiers**: Economy (15% discount), Standard, Expedited (30% premium)

### More Realistic Pricing
- Updated aluminum price from $5.00/kg to $8.50/kg for more realistic material costs
- Fixed quantity multiplier logic to prevent excessive discounts
- Improved cost breakdown to show both per-part and total costs
- Better lead time calculation that accounts for setup vs. per-part operations

**Example**: A part that costs $200 for 1 unit now costs ~$170 for 10 units (15% discount) instead of the previous exponential growth.

## Features

### Geometry Analysis
- Calculate bounding box dimensions (length, width, height)
- Calculate part volume and surface area
- Detect part complexity based on surface area to volume ratio, face count, and edge count
- Automatic block size selection for raw material

### Cost Estimation Logic
- Material cost calculation based on volume × density × price per unit mass
- Machine time estimation using three-phase milling approach:
  - Coarse milling (350 mm³/sec)
  - Medium milling (100 mm³/sec) 
  - Fine milling (20 mm³/sec)
- Labor costs for programming, setup, QC, and finishing
- Complexity multipliers based on part features
- Feature detection for holes, cavities, sharp edges, and pockets
- **Fixed**: Quantity discounts with realistic tiered pricing
- **NEW**: Shipping tier options (Economy/Standard/Expedited)

### Lead Time Estimation
- **Fixed**: Lead times now scale with quantity and complexity
- Setup time considerations
- Workday assumptions with efficiency factors
- **NEW**: Shipping tier affects lead time (Economy = longer, Expedited = shorter)

## Installation

### Prerequisites
- Python 3.8+ 
  - **Windows users**: Download from [python.org](https://python.org) OR use the **Microsoft Store** (often easier!)
  - **Mac/Linux users**: Download from [python.org](https://python.org)
- Git (Download from [git-scm.com](https://git-scm.com))

### Step-by-Step Setup (Windows)

**Step 1: Download the Code**
```bash
# Open PowerShell or Command Prompt, then run:
git clone https://github.com/OnkarPKher/cad-quoting-engine.git
cd cad-quoting-engine
```

**Step 2: Set up Python Environment**
```bash
# Create a virtual environment
python -m venv venv

# Activate the environment (Windows)
.\venv\Scripts\Activate.ps1

# You should see (venv) at the start of your command line
```

**Step 3: Install Required Packages**
```bash
pip install -r requirements.txt
```

### Step-by-Step Setup (Mac/Linux)
```bash
# Clone the repository
git clone https://github.com/OnkarPKher/cad-quoting-engine.git
cd cad-quoting-engine

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

## Usage

### Command Line Interface

**Basic Usage - Get Quote for 1 Part:**
```bash
python src/main.py data/suspension-mount.step
```

**Get Quote for Multiple Parts (with quantity discount):**
```bash
python src/main.py data/suspension-mount.step --quantity 10
```

**Get Quote with Different Shipping Tiers:**
```bash
# Economy shipping (15% discount, longer lead time)
python src/main.py data/suspension-mount.step --shipping economy

# Standard shipping (default)
python src/main.py data/suspension-mount.step --shipping standard

# Expedited shipping (30% premium, faster delivery)
python src/main.py data/suspension-mount.step --shipping expedited
```

**Get Quote with Expedited Shipping (Legacy):**
```bash
# 5-day delivery (+30% premium)
python src/main.py data/suspension-mount.step --expedited 5_days

# 4-day delivery (+60% premium)  
python src/main.py data/suspension-mount.step --expedited 4_days

# 3-day delivery (+100% premium)
python src/main.py data/suspension-mount.step --expedited 3_days
```

**Save Results to File:**
```bash
python src/main.py data/suspension-mount.step --quantity 5 --output my_quote.json
```

**Test Different Sample Parts:**
```bash
# Simple bracket
python src/main.py data/suspension-mount.step

# Complex gear
python src/main.py data/test-gear.STEP

# Piston head
python src/main.py data/piston-head.STEP

# Control bracket
python src/main.py data/control-bracket.STEP

# Complex manifold
python src/main.py "data/Pump Manifold v3.step"
```

### Command Line Options

- `step_file`: Path to the STEP file (required)
- `--quantity, -q`: Quantity of parts (default: 1)
- `--shipping, -s`: Shipping tier (economy, standard, expedited) - **NEW!**
- `--expedited, -e`: Expedited shipping option (5_days, 4_days, 3_days) - Legacy
- `--output, -o`: Output JSON file path (optional)

## Project Structure

```
cad-quoting-engine/
├── src/
│   └── main.py              # Main quoting engine (38KB, 823 lines)
├── data/                    # Sample STEP files for testing
│   ├── suspension-mount.step    # Simple bracket (341KB)
│   ├── piston-head.STEP         # Complex piston (405KB)
│   ├── control-bracket.STEP     # Control bracket (121KB)
│   ├── test-gear.STEP           # Complex gear (322KB)
│   └── Pump Manifold v3.step    # Complex manifold (493KB)
├── requirements.txt         # Python dependencies
├── README.md               # This comprehensive guide
├── IMPROVEMENTS_SUMMARY.md # Detailed improvements documentation
├── .gitignore              # Git ignore rules
└── venv/                   # Virtual environment (not in git)
```

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

**Current Rates (Customizable):**
- **CAD/CAM Programming**: $110/hour
- **Machine Setup**: $65/hour
- **Tool Setup**: $55/hour
- **Quality Inspection**: $65/hour
- **Deburring/Finishing**: $45/hour
- **Project Management**: $85/hour

**Note**: These are baseline rates based on industry averages. The system is designed so that **manufacturers can customize these rates** based on their:
- Geographic location and local market rates
- Shop overhead and operating costs
- Experience level and specialization
- Equipment quality and capabilities
- Target profit margins

To customize rates, edit the `labor_rates` dictionary in `src/main.py`.

### **NEW**: Shipping Tiers

**Economy (15% discount)**
- Longer lead time (1.5x standard)
- Best for non-urgent projects
- Significant cost savings

**Standard (baseline)**
- Normal pricing and lead time
- Best balance of cost and speed

**Expedited (30% premium)**
- Faster delivery (0.7x standard lead time)
- Best for urgent projects
- Premium pricing

### Baseline Specification Data
- **Aluminum 6061 Density**: 2.7 g/cm³
- **Aluminum Price**: $8.50/kg (**Updated from $5.00/kg for realism**)
- **CNC Machine Type**: Haas CNC Machines
- **CNC Machining Rate**: $100/hour

### Understanding the $200 Minimum Price

The $200 minimum price per part covers the **fixed costs** that every CNC job requires, regardless of part size:

- **CAD/CAM Programming**: Creating toolpaths and machine instructions
- **Machine Setup**: Fixturing, workholding, and machine preparation
- **Tool Setup**: Installing and calibrating cutting tools
- **Quality Inspection**: Measuring and verifying part dimensions
- **Administrative Overhead**: Order processing, documentation, and project management

Even a very simple, small part requires these steps, so this minimum ensures the shop doesn't lose money on basic jobs. For complex parts, the actual cost will be higher based on material, machining time, and complexity factors.

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

1. **Material Cost**: `volume_cm³ × density_g/cm³ × price_per_kg` (**Now scales with quantity**)
2. **Machine Time Cost**: Sum of three milling phases with different rates (**Now scales with quantity**)
3. **Labor Costs**: Programming, setup, QC, and finishing operations (**Now scales with quantity**)
4. **Complexity Multiplier**: Based on surface area to volume ratio, face count, and edge count
5. **Quantity Multiplier**: **Fixed**: Tiered discounts for larger quantities (5-30%)
6. **Shipping Tier**: Economy (0.85x), Standard (1.0x), Expedited (1.3x)

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

## Assumptions and Limitations

### Assumptions Made

1. **Material**: 6061 Aluminum (density: 2.7 g/cm³, price: $8.50/kg) - **Updated for realism**
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

1. **Lead Times**: **Fixed**: Now scale with quantity and complexity
2. **Expedited Shipping**: 5-day (+30%), 4-day (+60%), 3-day (+100%) options
3. **Quantity Discounts**: **Fixed**: Bulk pricing with 5-30% discounts (no more exponential growth)
4. **Complexity Scoring**: Based on surface area, face count, and edge count
5. **Size-Based Pricing**: Adjustments for small, medium, and large parts
6. **Three-Phase Milling**: Coarse, medium, and fine milling cost calculation
7. **Labor Costs**: Comprehensive labor cost breakdown (**Now scales with quantity**)
8. **Industry-Standard Material Optimization**: Smart block size selection with 20-40% waste target
9. **Material Efficiency Analysis**: Real-time waste percentage and efficiency reporting
10. **Feature Detection**: Advanced detection of holes, cavities, sharp edges, and pockets
11. **NEW: Shipping Tiers**: Economy, Standard, and Expedited options with different pricing and lead times

## Future Enhancements

1. **Advanced Geometry Analysis**: Better detection of holes, pockets, threads, and complex features
2. **Material Selection**: Support for multiple materials (steel, titanium, plastics)
3. **Tolerance Analysis**: Cost impact of tight tolerances or surface finishes
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

This project is open source and available under the [MIT License](LICENSE).

## Support

For questions, issues, or contributions, please:
1. Review existing issues on GitHub
2. Create a new issue with detailed information
3. Consider contributing a pull request

---
