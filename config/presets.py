"""Visualization preset configurations."""

# Preset configurations matching original scripts
PRESETS = {
    'intensity': {
        # Original: analyze_firewall.py & firewall_analyzer_pro.py
        'name': 'Intensity Map',
        'description': 'Balanced visualization with intensity-based coloring',
        'default_output': 'firewall_intensity_map.html',
        'top_n': 400,
        
        # Node configuration
        'node_sizing': 'combined',  # Combined attacker + target stats
        'node_size_range': [3, 15],  # Reduced from [6, 30]
        
        # Edge configuration
        'edge_width_range': [1, 6],
        'edge_scale_method': 'sqrt_simple',  # sqrt(hits) * 0.5
        
        # Color configuration
        'color_mode': 'gradient',  # Green -> Orange -> Red
        'color_thresholds': (0.2, 0.6),
        
        # Theme
        'theme': {
            'height': '900px',
            'width': '100%',
            'bgcolor': '#0b0e11',
            'font_color': 'white'
        },
        
        # Physics
        'physics': {
            'gravitational_constant': -20000,
            'central_gravity': 0.8,
            'spring_length': 100,
            'edge_smooth': False,
            'arrow_scale': 0.4,
            'stabilization_iterations': 40
        }
    },
    
    'heatmap': {
        # Original: firewall_heatmap_nodes.py
        'name': 'Security Heatmap',
        'description': 'Advanced heatmap with color-coded nodes by intensity',
        'default_output': 'firewall_security_heatmap.html',
        'top_n': 350,
        
        # Node configuration
        'node_sizing': 'separate',  # Separate attacker/target stats
        'node_size_range': [3, 14],  # Reduced from [6, 28]
        'target_size_range': [4, 15],  # Reduced from [8, 30]
        'node_scale_method': 'linear',
        
        # Edge configuration
        'edge_width_range': [1, 7],
        'edge_scale_method': 'linear',
        
        # Color configuration
        'color_mode': 'heatmap',  # Green -> Yellow -> Orange -> Red
        'color_thresholds': (0.15, 0.4, 0.7),
        
        # Theme
        'theme': {
            'height': '950px',
            'width': '100%',
            'bgcolor': '#0d1117',
            'font_color': '#f0f6fc'
        },
        
        # Physics
        'physics': {
            'gravitational_constant': -40000,
            'central_gravity': 0.5,
            'spring_length': 180,
            'spring_constant': 0.05,
            'damping': 0.4,
            'edge_smooth': False,
            'arrow_scale': 0.4,
            'stabilization_iterations': 60
        }
    },
    
    'micro': {
        # Original: firewall_micro_heatmap.py
        'name': 'Micro-Scale Heatmap',
        'description': 'Compact visualization with micro-scale nodes for high-density data',
        'default_output': 'firewall_micro_map.html',
        'top_n': 400,
        
        # Node configuration
        'node_sizing': 'separate',
        'node_size_range': [2, 8],  # Very small nodes - reduced from [3, 12]
        'target_size_range': [6, 6],  # Fixed target size - reduced from 10
        'node_scale_method': 'sqrt',
        'label_threshold': 0.1,  # Only label top 10% attackers
        
        # Edge configuration
        'edge_width_range': [0.5, 4],
        'edge_scale_method': 'linear',
        'edge_opacity': 0.4,
        
        # Color configuration
        'color_mode': 'heatmap',
        'color_thresholds': (0.2, 0.5, 0.8),
        
        # Theme
        'theme': {
            'height': '1280px',
            'width': '100%',
            'bgcolor': '#ffffff',  # White background
            'font_color': '#8b949e'
        },
        
        # Physics
        'physics': {
            'gravitational_constant': -50000,
            'central_gravity': 0.3,
            'spring_length': 200,
            'spring_constant': 0.05,
            'damping': 0.5,
            'edge_smooth': False,
            'arrow_scale': 0.2,  # Small arrows
            'stabilization_iterations': 50
        }
    },
    
    'balanced': {
        # Original: firewall_pro_balanced.py
        'name': 'Balanced Clean Map',
        'description': 'Clean readable version with balanced sizing and spacing',
        'default_output': 'firewall_balanced_map.html',
        'top_n': 350,
        
        # Node configuration
        'node_sizing': 'combined',
        'node_size_range': [3, 12],  # Reduced from [5, 25]
        
        # Edge configuration
        'edge_width_range': [1, 6],
        'edge_scale_method': 'linear',
        
        # Color configuration
        'color_mode': 'gradient',
        'color_thresholds': (0.2, 0.6),
        
        # Theme
        'theme': {
            'height': '900px',
            'width': '100%',
            'bgcolor': '#111111',
            'font_color': '#ecf0f1'
        },
        
        # Physics
        'physics': {
            'gravitational_constant': -30000,
            'central_gravity': 0.3,
            'spring_length': 150,
            'spring_constant': 0.05,
            'damping': 0.3,
            'edge_smooth': False,
            'arrow_scale': 0.3,
            'stabilization_iterations': 50
        }
    }
}


def get_preset(name):
    """
    Get preset configuration by name.
    
    Args:
        name: Preset name (intensity, heatmap, micro, balanced)
        
    Returns:
        dict: Preset configuration
        
    Raises:
        ValueError: If preset name is invalid
    """
    if name not in PRESETS:
        available = ', '.join(PRESETS.keys())
        raise ValueError(f"Unknown preset '{name}'. Available: {available}")
    
    return PRESETS[name].copy()


def list_presets():
    """
    List all available presets with descriptions.
    
    Returns:
        list: List of (name, description) tuples
    """
    return [(name, config['description']) for name, config in PRESETS.items()]
