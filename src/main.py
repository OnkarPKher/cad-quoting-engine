import os
import json
import argparse
import numpy as np
import trimesh
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class QuoteResult:
    """Container for quote results"""
    per_unit_cost: float
    lead_time_days: int
    material_cost: float
    machine_time_cost: float
    total_cost: float
    bounding_box: Dict[str, float]
    volume: float
    surface_area: float
    complexity_score: float
    breakdown: Dict[str, float]
    expedited: bool = False
    expedited_multiplier: float = 1.0

class CADQuotingEngine:
    """CAD Quoting Engine for CNC machining cost estimation"""
    
    def __init__(self):
        # Material properties - Baseline data from specification
        self.aluminum_density = 2.7  # g/cm³
        self.aluminum_price_per_kg = 5.0  # USD/kg
        self.cnc_rate_per_hour = 100.0  # USD/hour
        
        # Industry standard stock sizes (mm) - Based on common CNC machining practices
        # Format: [length, width, height] - optimized for minimal waste
        self.block_sizes = [
            # Small parts (0-50mm)
            [25, 25, 25],
            [50, 50, 50],
            [75, 75, 75],
            
            # Medium parts (50-150mm) - Most common sizes
            [100, 100, 100],
            [125, 125, 125],
            [150, 125, 125],
            [150, 150, 150],
            [175, 150, 150],
            [200, 150, 150],
            [200, 200, 150],
            [200, 200, 200],
            
            # Large parts (150-300mm) - Industry standard
            [250, 200, 200],
            [250, 250, 200],
            [250, 250, 250],
            [300, 250, 250],
            [300, 300, 250],
            [300, 300, 300],
            
            # Extra large parts (300mm+) - Special order
            [400, 300, 300],
            [400, 400, 300],
            [500, 400, 400],
            [600, 500, 500],
        ]
        
        # Material removal rates (mm³/sec)
        self.coarse_mrr = 350  # mm³/sec
        self.medium_mrr = 100  # mm³/sec
        self.fine_mrr = 20     # mm³/sec
        
        # Cost per mm³ for each milling phase
        self.coarse_cost_per_mm3 = 0.00011   # USD/mm³
        self.medium_cost_per_mm3 = 0.00039   # USD/mm³
        self.fine_cost_per_mm3 = 0.00175     # USD/mm³
        
        # Minimum price per part
        self.min_price_per_part = 200  # USD
        
        # Calibration factors based on part complexity and size
        self.complexity_calibration = {
            'low': 0.85,     # Simple parts get 15% discount
            'medium': 1.0,   # Standard complexity
            'high': 1.35     # Complex parts get 35% premium
        }
        
        # Size-based calibration factors
        self.size_calibration = {
            'small': 1.15,   # Small parts (< 50mm) get 15% premium
            'medium': 1.0,   # Standard size
            'large': 0.9     # Large parts (> 200mm) get 10% discount
        }
        
        # Base machining rate (USD per hour) - Baseline data from specification
        self.base_machining_rate = 100.0  # USD/hour
        
        # Labor rates for different operations (USD per hour)
        self.labor_rates = {
            'cad_cam_programming': 110.0,    # CAD/CAM programming
            'machine_setup': 65.0,           # Machine setup and fixturing
            'tool_setup': 55.0,              # Tool setup and calibration
            'quality_inspection': 65.0,      # Quality control and inspection
            'deburring_finishing': 45.0,     # Deburring and surface finishing
            'project_management': 85.0,      # Project coordination and documentation
        }
        
        # Setup time factors
        self.base_setup_time = 0.4  # hours
        
        # Complexity multipliers for different features
        self.feature_multipliers = {
            'holes': 1.03,      # 3% premium for holes
            'pockets': 1.07,     # 7% premium for pockets
            'threads': 1.1,      # 10% premium for threads
            'tight_tolerance': 1.15  # 15% premium for tight tolerances
        }
        
        # Expedited shipping options
        self.expedited_options = {
            '5_days': {
                'multiplier': 1.3,  # 30% premium for 5-day delivery
                'max_days': 5,
                'description': '5 business days'
            },
            '4_days': {
                'multiplier': 1.6,  # 60% premium for 4-day delivery
                'max_days': 4,
                'description': '4 business days'
            },
            '3_days': {
                'multiplier': 2.0,  # 100% premium for 3-day delivery
                'max_days': 3,
                'description': '3 business days'
            }
        }
    
    def load_step_file(self, filepath: str) -> trimesh.Trimesh:
        """Load a STEP file and return a trimesh object"""
        try:
            # Load the mesh from STEP file
            mesh = trimesh.load(filepath)
            
            # If it's a scene, get the first mesh
            if isinstance(mesh, trimesh.Scene):
                mesh = list(mesh.geometry.values())[0]
            
            # Check if the mesh needs unit conversion
            # If bounding box is very small (< 1mm), assume it's in meters
            bounds = mesh.bounds
            dimensions = bounds[1] - bounds[0]
            max_dimension = np.max(dimensions)
            
            if max_dimension < 1.0:  # Likely in meters, convert to mm
                print(f"Detected units in meters, converting to millimeters...")
                # Scale the mesh by 1000 to convert from meters to millimeters
                mesh.apply_transform(np.eye(4) * 1000)
            
            return mesh
        except Exception as e:
            raise ValueError(f"Failed to load STEP file: {e}")
    
    def get_bounding_box(self, mesh: trimesh.Trimesh) -> Dict[str, float]:
        """Calculate bounding box dimensions"""
        bounds = mesh.bounds
        dimensions = bounds[1] - bounds[0]
        
        return {
            "length": float(dimensions[0]),
            "width": float(dimensions[1]),
            "height": float(dimensions[2]),
            "x_min": float(bounds[0][0]),
            "y_min": float(bounds[0][1]),
            "z_min": float(bounds[0][2]),
            "x_max": float(bounds[1][0]),
            "y_max": float(bounds[1][1]),
            "z_max": float(bounds[1][2])
        }
    
    def calculate_volumes(self, mesh: trimesh.Trimesh) -> Dict[str, float]:
        """Calculate various volumes for pricing"""
        # Part volume
        part_volume = abs(mesh.volume)  # Use absolute value
        
        # Convex hull volume (coarse outline)
        convex_hull = mesh.convex_hull
        convex_hull_volume = abs(convex_hull.volume)
        
        # Shrink wrap volume (approximation using convex hull with some reduction)
        # This is a simplified approach - in practice, you'd use more sophisticated algorithms
        shrink_wrap_volume = convex_hull_volume * 0.8  # 80% of convex hull as approximation
        
        return {
            "part_volume": part_volume,
            "convex_hull_volume": convex_hull_volume,
            "shrink_wrap_volume": shrink_wrap_volume
        }
    
    def find_smallest_fitting_block(self, dimensions: List[float]) -> Optional[List[float]]:
        """Find the smallest block that can fit the part with industry-standard material optimization"""
        # Sort dimensions for comparison
        sorted_dimensions = sorted(dimensions)
        
        # Industry standard: aim for 20-40% material waste, not excessive waste
        fitting_blocks = []
        
        for block in self.block_sizes:
            sorted_block = sorted(block)
            
            # Check if part fits in block
            if all(d <= b for d, b in zip(sorted_dimensions, sorted_block)):
                # Calculate material efficiency
                block_volume = block[0] * block[1] * block[2]
                part_volume = dimensions[0] * dimensions[1] * dimensions[2]
                waste_ratio = (block_volume - part_volume) / block_volume
                
                # Industry standard: prefer blocks with 20-60% waste ratio
                # This balances material cost vs. excessive machining
                if waste_ratio <= 0.7:  # Maximum 70% waste (industry realistic)
                    fitting_blocks.append((block, waste_ratio, block_volume))
        
        if not fitting_blocks:
            # If no optimal blocks found, use the smallest fitting block
            for block in self.block_sizes:
                sorted_block = sorted(block)
                if all(d <= b for d, b in zip(sorted_dimensions, sorted_block)):
                    fitting_blocks.append((block, 0.8, block[0] * block[1] * block[2]))
        
        if not fitting_blocks:
            return None
        
        # Industry standard: prioritize blocks with optimal waste ratio (20-40%)
        # Then consider volume for cost optimization
        optimal_blocks = [b for b in fitting_blocks if 0.2 <= b[1] <= 0.6]
        
        if optimal_blocks:
            # Choose block with best waste ratio, then smallest volume
            return min(optimal_blocks, key=lambda x: (abs(x[1] - 0.3), x[2]))[0]
        else:
            # Fall back to smallest fitting block
            return min(fitting_blocks, key=lambda x: x[2])[0]
    
    def detect_features(self, mesh: trimesh.Trimesh) -> Dict[str, any]:
        """Detect basic features like holes, cavities, sharp edges, pockets"""
        features = {
            'holes': 0,
            'cavities': 0,
            'sharp_edges': 0,
            'pockets': 0,
            'feature_score': 0
        }
        
        try:
            # Get part dimensions and properties
            bounds = mesh.bounds
            dimensions = bounds[1] - bounds[0]
            volume = abs(mesh.volume)
            surface_area = mesh.area
            
            # More realistic hole detection - only count significant holes
            sa_volume_ratio = surface_area / volume if volume > 0 else 0
            if sa_volume_ratio > 0.15:  # Higher threshold for holes
                features['holes'] = max(1, min(5, int(sa_volume_ratio * 5)))  # Cap at 5 holes
            
            # More conservative cavity detection
            convex_hull = mesh.convex_hull
            cavity_ratio = 1 - (volume / abs(convex_hull.volume))
            if cavity_ratio > 0.2:  # Higher threshold for cavities
                features['cavities'] = max(1, min(3, int(cavity_ratio * 3)))  # Cap at 3 cavities
            
            # More realistic sharp edge detection
            edge_face_ratio = len(mesh.edges) / len(mesh.faces) if len(mesh.faces) > 0 else 0
            if edge_face_ratio > 3.0:  # Higher threshold for sharp edges
                features['sharp_edges'] = max(1, min(4, int(edge_face_ratio * 1.5)))  # Cap at 4 sharp edges
            
            # More conservative pocket detection
            face_count = len(mesh.faces)
            if face_count > 2000:  # Higher threshold for pockets
                features['pockets'] = max(1, min(8, int(face_count / 1000)))  # Cap at 8 pockets
            elif face_count > 1000:
                features['pockets'] = max(1, min(4, int(face_count / 800)))  # Cap at 4 pockets
            
            # Calculate overall feature score with more conservative weighting
            features['feature_score'] = (features['holes'] * 0.8 + 
                                       features['cavities'] * 0.6 + 
                                       features['sharp_edges'] * 0.4 + 
                                       features['pockets'] * 0.5)
            
        except Exception as e:
            # If feature detection fails, use basic complexity
            features['feature_score'] = 0
        
        return features
    
    def calculate_complexity_score(self, mesh: trimesh.Trimesh) -> float:
        """Calculate part complexity score based on various factors"""
        # Get feature detection
        features = self.detect_features(mesh)
        
        # Surface area to volume ratio (more conservative)
        sa_volume_ratio = mesh.area / abs(mesh.volume) if abs(mesh.volume) > 0 else 0
        sa_complexity = min(sa_volume_ratio * 0.15, 3.0)  # Cap surface area complexity at 3
        
        # Number of faces (more conservative)
        face_count = len(mesh.faces)
        face_complexity = min((face_count / 1000) * 2.0, 4.0)  # Cap face complexity at 4
        
        # Edge count (more conservative)
        edge_count = len(mesh.edges)
        edge_complexity = min((edge_count / 1000) * 2.0, 3.0)  # Cap edge complexity at 3
        
        # Feature complexity (holes, cavities, sharp edges, pockets) - more conservative
        feature_complexity = min(features['feature_score'] * 0.3, 2.0)  # Cap feature complexity at 2
        
        # Combine factors with more balanced weighting
        complexity = sa_complexity + face_complexity + edge_complexity + feature_complexity
        
        return min(complexity, 8.0)  # Cap at 8 instead of 10 for more realistic scoring
    
    def get_complexity_category(self, score: float) -> str:
        """Determine the complexity category based on the score."""
        if score < 4.0:
            return 'low'
        elif score < 6.0:
            return 'medium'
        else:
            return 'high'
    
    def get_size_category(self, length: float) -> str:
        """Determine the size category based on the length."""
        if length < 50:
            return 'small'
        elif length < 200:
            return 'medium'
        else:
            return 'large'
    
    def get_quantity_multiplier(self, quantity: int) -> float:
        """Get quantity discount multiplier"""
        tiers = [
            (1, 1.0),      # 1 part: 100% (baseline)
            (2, 0.95),     # 2 parts: 95% (5% discount)
            (3, 0.92),     # 3 parts: 92% (8% discount)
            (4, 0.90),     # 4 parts: 90% (10% discount)
            (5, 0.88),     # 5 parts: 88% (12% discount)
            (10, 0.85),    # 10 parts: 85% (15% discount)
            (15, 0.82),    # 15 parts: 82% (18% discount)
            (20, 0.80),    # 20 parts: 80% (20% discount)
            (25, 0.78),    # 25 parts: 78% (22% discount)
            (50, 0.75),    # 50 parts: 75% (25% discount)
            (100, 0.72),   # 100 parts: 72% (28% discount)
        ]
        
        if quantity < 1:
            return tiers[0][1]
        if quantity >= 5000:
            return tiers[-1][1]
        
        for i in range(len(tiers) - 1):
            lower_qty, lower_mult = tiers[i]
            upper_qty, upper_mult = tiers[i + 1]
            
            if lower_qty <= quantity <= upper_qty:
                # Linear interpolation between tiers
                t = (quantity - lower_qty) / (upper_qty - lower_qty)
                return lower_mult + (upper_mult - lower_mult) * t
        
        return tiers[0][1]
    
    def get_quantity_discount_percentage(self, quantity: int) -> float:
        """Calculate the discount percentage for a given quantity"""
        multiplier = self.get_quantity_multiplier(quantity)
        # Convert multiplier to discount percentage
        # multiplier of 1.0 = 0% discount, multiplier < 1.0 = discount
        if multiplier < 1.0:
            return (1.0 - multiplier) * 100
        else:
            return 0.0  # No discount for single parts
    
    def estimate_machine_time(self, volumes: Dict[str, float]) -> float:
        """Estimate machine time based on volumes and MRR"""
        coarse_volume = volumes.get("block_volume", 0) - volumes.get("convex_hull_volume", 0)
        medium_volume = volumes.get("convex_hull_volume", 0) - volumes.get("shrink_wrap_volume", 0)
        fine_volume = volumes.get("shrink_wrap_volume", 0) - volumes.get("part_volume", 0)
        
        coarse_time = coarse_volume / self.coarse_mrr if self.coarse_mrr > 0 else 0
        medium_time = medium_volume / self.medium_mrr if self.medium_mrr > 0 else 0
        fine_time = fine_volume / self.fine_mrr if self.fine_mrr > 0 else 0
        
        return coarse_time + medium_time + fine_time
    
    def calculate_labor_costs(self, mesh: trimesh.Trimesh, complexity_score: float, quantity: int = 1) -> Dict[str, float]:
        """Calculate comprehensive labor costs based on part complexity and quantity"""
        # Base setup time (programming, fixturing, tool setup)
        base_setup_hours = self.base_setup_time
        
        # Complexity-based adjustments
        if complexity_score < 3:
            complexity_factor = 0.8  # Simple parts
        elif complexity_score < 7:
            complexity_factor = 1.0  # Medium complexity
        else:
            complexity_factor = 1.4  # Complex parts
        
        # Calculate labor hours for different operations
        cad_cam_hours = base_setup_hours * 0.4 * complexity_factor  # 40% of setup time
        machine_setup_hours = base_setup_hours * 0.3 * complexity_factor  # 30% of setup time
        tool_setup_hours = base_setup_hours * 0.3 * complexity_factor  # 30% of setup time
        
        # Quality control time (based on complexity and surface area)
        surface_area_m2 = mesh.area / 1000000  # Convert to m²
        qc_hours = max(0.1, surface_area_m2 * 0.5) * complexity_factor
        
        # Finishing time (deburring, surface treatment)
        finishing_hours = max(0.1, surface_area_m2 * 0.3) * complexity_factor
        
        # Project management (fixed per job + complexity factor)
        project_mgmt_hours = 0.2 + (complexity_score / 20)  # 0.2-0.7 hours
        
        # Calculate costs
        labor_costs = {
            'cad_cam_programming': cad_cam_hours * self.labor_rates['cad_cam_programming'],
            'machine_setup': machine_setup_hours * self.labor_rates['machine_setup'],
            'tool_setup': tool_setup_hours * self.labor_rates['tool_setup'],
            'quality_inspection': qc_hours * self.labor_rates['quality_inspection'],
            'deburring_finishing': finishing_hours * self.labor_rates['deburring_finishing'],
            'project_management': project_mgmt_hours * self.labor_rates['project_management'],
        }
        
        # For multiple parts, some setup is done once, some per part
        if quantity > 1:
            # Setup costs are one-time
            # QC and finishing are per part
            per_part_costs = labor_costs['quality_inspection'] + labor_costs['deburring_finishing']
            total_labor_cost = (labor_costs['cad_cam_programming'] + 
                              labor_costs['machine_setup'] + 
                              labor_costs['tool_setup'] + 
                              labor_costs['project_management'] +
                              (per_part_costs * quantity))
        else:
            total_labor_cost = sum(labor_costs.values())
        
        labor_costs['total_labor_cost'] = total_labor_cost
        labor_costs['total_hours'] = (cad_cam_hours + machine_setup_hours + tool_setup_hours + 
                                    qc_hours + finishing_hours + project_mgmt_hours)
        
        return labor_costs
    
    def calculate_costs(self, mesh: trimesh.Trimesh, quantity: int = 1, expedited: str = None, part_name: str = None) -> QuoteResult:
        """Calculate all costs for the part"""
        # Get basic measurements
        bounding_box = self.get_bounding_box(mesh)
        volumes = self.calculate_volumes(mesh)
        complexity_score = self.calculate_complexity_score(mesh)
        
        # Find appropriate block size
        dimensions = [bounding_box["length"], bounding_box["width"], bounding_box["height"]]
        best_block = self.find_smallest_fitting_block(dimensions)
        
        if not best_block:
            raise ValueError("Part is too large for available block sizes")
        
        block_volume = best_block[0] * best_block[1] * best_block[2]
        volumes["block_volume"] = block_volume
        
        # Calculate milling volumes
        coarse_volume = max(0, block_volume - volumes["convex_hull_volume"])
        medium_volume = max(0, volumes["convex_hull_volume"] - volumes["shrink_wrap_volume"])
        fine_volume = max(0, volumes["shrink_wrap_volume"] - volumes["part_volume"])
        
        # Calculate costs
        coarse_cost = coarse_volume * self.coarse_cost_per_mm3
        medium_cost = medium_volume * self.medium_cost_per_mm3
        fine_cost = fine_volume * self.fine_cost_per_mm3
        
        machine_time_cost = coarse_cost + medium_cost + fine_cost
        
        # Material cost (more accurate calculation)
        material_volume_cm3 = volumes["part_volume"] / 1000  # Convert mm³ to cm³
        material_mass_kg = material_volume_cm3 * self.aluminum_density / 1000  # Convert g to kg
        material_cost = material_mass_kg * self.aluminum_price_per_kg
        
        # Calculate comprehensive labor costs
        labor_costs = self.calculate_labor_costs(mesh, complexity_score, quantity)
        total_labor_cost = labor_costs['total_labor_cost']
        
        # Apply complexity multiplier
        complexity_multiplier = self.complexity_calibration.get(self.get_complexity_category(complexity_score), 1.0)
        machine_time_cost *= complexity_multiplier
        
        # Apply size multiplier
        size_multiplier = self.size_calibration.get(self.get_size_category(bounding_box["length"]), 1.0)
        machine_time_cost *= size_multiplier
        
        # Apply algorithmic pricing
        
        # Apply quantity multiplier
        quantity_multiplier = self.get_quantity_multiplier(quantity)
        total_cost_per_unit = (machine_time_cost + material_cost + total_labor_cost) * quantity_multiplier
        
        # Apply minimum price
        if total_cost_per_unit < self.min_price_per_part:
            total_cost_per_unit = self.min_price_per_part
        
        # Handle expedited shipping
        expedited_multiplier = 1.0
        expedited_description = None
        
        if expedited and expedited in self.expedited_options:
            expedited_config = self.expedited_options[expedited]
            expedited_multiplier = expedited_config['multiplier']
            expedited_description = expedited_config['description']
            total_cost_per_unit *= expedited_multiplier
        
        # Estimate lead time
        machine_time_hours = self.estimate_machine_time(volumes) / 3600  # Convert seconds to hours
        
        # Lead time calculation
        # Base setup time (programming, fixturing, tool setup)
        setup_time_hours = self.base_setup_time * 0.5
        
        # Finishing time (deburring, cleaning, inspection)
        finishing_time_hours = machine_time_hours * 0.05
        
        # Quality control time
        qc_time_hours = (machine_time_hours + setup_time_hours + finishing_time_hours) * 0.03
        
        # Total time for one part
        total_time_per_part = machine_time_hours + setup_time_hours + finishing_time_hours + qc_time_hours
        
        # For multiple parts, setup is done once, but each part needs machining, finishing, and QC
        if quantity == 1:
            total_time_hours = total_time_per_part
        else:
            # Setup once, then machining time for each part
            total_time_hours = setup_time_hours + (machine_time_hours + finishing_time_hours + qc_time_hours) * quantity
        
        # Convert to days
        work_hours_per_day = 10
        efficiency_factor = 0.9
        buffer_factor = 1.1
        
        effective_hours_per_day = work_hours_per_day * efficiency_factor
        adjusted_total_hours = total_time_hours * buffer_factor
        
        lead_time_days = max(1, int(np.ceil(adjusted_total_hours / effective_hours_per_day)))
        
        # Lead time based on complexity
        if complexity_score < 5:
            standard_lead_time = 7  # Simple parts: 7 days
        elif complexity_score < 8:
            standard_lead_time = 10  # Medium complexity: 10 days
        else:
            standard_lead_time = 11  # Complex parts: 11 days
        
        # Set the lead time to the standard time
        lead_time_days = standard_lead_time
        
        # Apply expedited lead time if requested
        if expedited and expedited in self.expedited_options:
            expedited_config = self.expedited_options[expedited]
            # For expedited orders, reduce lead time
            if expedited == "3_days":
                lead_time_days = 3  # 3-day expedited
            elif expedited == "4_days":
                lead_time_days = 4  # 4-day expedited
            elif expedited == "5_days":
                lead_time_days = 5  # 5-day expedited
        
        return QuoteResult(
            per_unit_cost=total_cost_per_unit,
            lead_time_days=lead_time_days,
            material_cost=material_cost,
            machine_time_cost=machine_time_cost,
            total_cost=total_cost_per_unit * quantity,
            bounding_box=bounding_box,
            volume=volumes["part_volume"],
            surface_area=mesh.area,
            complexity_score=complexity_score,
            breakdown={
                "coarse_milling_cost": coarse_cost,
                "medium_milling_cost": medium_cost,
                "fine_milling_cost": fine_cost,
                "material_cost": material_cost,
                "labor_costs": labor_costs,
                "total_labor_cost": total_labor_cost,
                "complexity_multiplier": complexity_multiplier,
                "size_multiplier": size_multiplier,
                "quantity_multiplier": quantity_multiplier,
                "block_size": best_block,
                "block_volume": block_volume,
                "coarse_volume": coarse_volume,
                "medium_volume": medium_volume,
                "fine_volume": fine_volume,
                "expedited_multiplier": expedited_multiplier,
                "expedited_description": expedited_description
            },
            expedited=expedited is not None,
            expedited_multiplier=expedited_multiplier
        )

def main():
    parser = argparse.ArgumentParser(description="CAD Quoting Engine for CNC Machining")
    parser.add_argument("step_file", help="Path to the STEP file")
    parser.add_argument("--quantity", "-q", type=int, default=1, help="Quantity of parts")
    parser.add_argument("--expedited", "-e", choices=["5_days", "4_days", "3_days"], 
                       help="Expedited shipping option: 5_days (30%% premium), 4_days (60%% premium), 3_days (100%% premium)")
    parser.add_argument("--output", "-o", help="Output JSON file path (optional)")
    
    args = parser.parse_args()
    
    # Initialize the quoting engine
    engine = CADQuotingEngine()
    
    try:
        # Load the STEP file
        print(f"Loading STEP file: {args.step_file}")
        mesh = engine.load_step_file(args.step_file)
        
        # Calculate costs
        print("Calculating quote...")
        # Extract part name from filename for lead time determination
        part_name = os.path.basename(args.step_file)
        result = engine.calculate_costs(mesh, args.quantity, args.expedited, part_name)
        
        # Display results
        print("\n" + "="*50)
        print("CAD QUOTING ENGINE RESULTS")
        print("="*50)
        print(f"Input file: {args.step_file}")
        print(f"Quantity: {args.quantity}")
        
        if args.expedited:
            expedited_config = engine.expedited_options[args.expedited]
            print(f"Expedited shipping: {expedited_config['description']} (+{int((expedited_config['multiplier']-1)*100)}% premium)")
        
        if args.quantity > 1:
            discount_percentage = engine.get_quantity_discount_percentage(args.quantity)
            if discount_percentage > 0:
                print(f"\nQUANTITY DISCOUNT:")
                print(f"  Quantity discount: {discount_percentage:.1f}%")
            print(f"  Multiplier applied: {result.breakdown['quantity_multiplier']:.2f}x")
        
        print(f"\nCOST BREAKDOWN:")
        print(f"  Per unit cost: ${result.per_unit_cost:.2f}")
        print(f"  Total cost: ${result.total_cost:.2f}")
        print(f"  Material cost: ${result.material_cost:.2f}")
        print(f"  Machine time cost: ${result.machine_time_cost:.2f}")
        print(f"  Labor costs: ${result.breakdown['total_labor_cost']:.2f}")
        
        if args.expedited:
            print(f"  Expedited premium: +${(result.per_unit_cost / result.breakdown['expedited_multiplier'] * (result.breakdown['expedited_multiplier'] - 1)):.2f}")
        
        print(f"\nLEAD TIME:")
        print(f"  Estimated lead time: {result.lead_time_days} days")
        if args.expedited:
            print(f"  Expedited delivery: {result.breakdown['expedited_description']}")
        
        print(f"\nPART ANALYSIS:")
        print(f"  Dimensions (L×W×H): {result.bounding_box['length']:.1f} × {result.bounding_box['width']:.1f} × {result.bounding_box['height']:.1f} mm")
        print(f"  Volume: {result.volume:.1f} mm³")
        print(f"  Surface area: {result.surface_area:.1f} mm²")
        print(f"  Complexity score: {result.complexity_score:.1f}/10")
        print(f"  Block size: {result.breakdown['block_size']} mm")
        
        # Display industry-standard material analysis
        block_volume = result.breakdown['block_volume']
        part_volume = result.volume
        waste_volume = block_volume - part_volume
        waste_percentage = (waste_volume / block_volume) * 100
        
        print(f"\nINDUSTRY MATERIAL ANALYSIS:")
        print(f"  Block volume: {block_volume:,.0f} mm³")
        print(f"  Part volume: {part_volume:,.0f} mm³")
        print(f"  Material waste: {waste_volume:,.0f} mm³ ({waste_percentage:.1f}%)")
        print(f"  Material efficiency: {100-waste_percentage:.1f}%")
        
        # Display detected features
        features = engine.detect_features(mesh)
        print(f"\nDETECTED FEATURES:")
        print(f"  Holes: {features['holes']}")
        print(f"  Cavities: {features['cavities']}")
        print(f"  Sharp edges: {features['sharp_edges']}")
        print(f"  Pockets: {features['pockets']}")
        print(f"  Feature complexity score: {features['feature_score']}")
        
        print(f"\nCALIBRATION FACTORS:")
        print(f"  Complexity multiplier: {result.breakdown['complexity_multiplier']:.2f}x")
        print(f"  Size multiplier: {result.breakdown['size_multiplier']:.2f}x")
        print(f"  Quantity multiplier: {result.breakdown['quantity_multiplier']:.2f}x")
        if args.expedited:
            print(f"  Expedited multiplier: {result.breakdown['expedited_multiplier']:.2f}x")
        
        print(f"\nMILLING BREAKDOWN:")
        print(f"  Coarse milling: ${result.breakdown['coarse_milling_cost']:.2f}")
        print(f"  Medium milling: ${result.breakdown['medium_milling_cost']:.2f}")
        print(f"  Fine milling: ${result.breakdown['fine_milling_cost']:.2f}")
        
        print(f"\nLABOR COST BREAKDOWN:")
        print(f"  CAD/CAM Programming: ${result.breakdown['labor_costs']['cad_cam_programming']:.2f}")
        print(f"  Machine Setup: ${result.breakdown['labor_costs']['machine_setup']:.2f}")
        print(f"  Tool Setup: ${result.breakdown['labor_costs']['tool_setup']:.2f}")
        print(f"  Quality Inspection: ${result.breakdown['labor_costs']['quality_inspection']:.2f}")
        print(f"  Deburring/Finishing: ${result.breakdown['labor_costs']['deburring_finishing']:.2f}")
        print(f"  Project Management: ${result.breakdown['labor_costs']['project_management']:.2f}")
        print(f"  Total Labor Hours: {result.breakdown['labor_costs']['total_hours']:.2f} hours")
        
        print("\n" + "="*50)
        print("PRICING MODEL NOTES:")
        print("="*50)
        print("• Material costs: Based on 6061 Aluminum ($5.00/kg) - Baseline specification")
        print("• Machine time: Three-phase milling approach")
        print("• MRR: Coarse (350 mm³/sec), Medium (100 mm³/sec), Fine (20 mm³/sec)")
        print("• Complexity: Based on surface area, face count, edge count, and feature detection")
        print("• Feature detection: Holes, cavities, sharp edges, pockets")
        print("• Quantity discounts: Bulk pricing with 5-28% discounts")
        print("• Minimum price: $200.00 per part")
        print("• CNC rate: $100/hour - Haas CNC Machines (Baseline specification)")
        print("• Labor costs: Programming, setup, QC, and finishing operations")
        print("• Lead time: Based on part complexity and expedited options")
        if args.expedited:
            print(f"• Expedited shipping: {result.breakdown['expedited_description']} with {int((result.breakdown['expedited_multiplier']-1)*100)}% premium")
        
        # Save to JSON if output file specified
        if args.output:
            try:
                output_data = {
                    "input_file": args.step_file,
                    "quantity": args.quantity,
                    "expedited": args.expedited,
                    "quote": {
                        "per_unit_cost": result.per_unit_cost,
                        "total_cost": result.total_cost,
                        "material_cost": result.material_cost,
                        "machine_time_cost": result.machine_time_cost,
                        "lead_time_days": result.lead_time_days,
                        "bounding_box": result.bounding_box,
                        "volume": result.volume,
                        "surface_area": result.surface_area,
                        "complexity_score": result.complexity_score,
                        "breakdown": result.breakdown
                    }
                }
                
                with open(args.output, 'w') as f:
                    json.dump(output_data, f, indent=2)
                print(f"\nQuote saved to: {args.output}")
                
            except Exception as e:
                print(f"Warning: Could not save to JSON file: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
