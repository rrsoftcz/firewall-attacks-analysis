"""Styling functions for graph nodes and edges."""
import numpy as np


def get_color_gradient(hits, max_hits, thresholds=(0.2, 0.6)):
    """
    Map hit count to color gradient: Green -> Orange -> Red.
    
    Args:
        hits: Number of hits for this connection
        max_hits: Maximum hits in dataset
        thresholds: Tuple of (low, high) ratio thresholds
        
    Returns:
        str: Hex color code
    """
    if max_hits == 0:
        return '#2ecc71'  # Green
    
    ratio = hits / max_hits
    low_threshold, high_threshold = thresholds
    
    if ratio < low_threshold:
        return '#2ecc71'  # Green (Safe/Low)
    elif ratio < high_threshold:
        return '#f39c12'  # Orange (Warning)
    else:
        return '#e74c3c'  # Red (Critical)


def get_smooth_gradient(value, min_val, max_val):
    """
    Calculate smooth color gradient from green to red based on min/max values.
    Uses RGB interpolation for smooth transitions.
    
    Args:
        value: Current value
        min_val: Minimum value in dataset
        max_val: Maximum value in dataset
        
    Returns:
        str: Hex color code
    """
    if max_val == min_val:
        return '#2ecc71'  # Green if all values are the same
    
    # Normalize value to 0-1 range
    ratio = (value - min_val) / (max_val - min_val)
    
    # Define color stops: Green -> Yellow -> Orange -> Red
    # Green: (46, 204, 113)
    # Yellow: (241, 196, 15)
    # Orange: (230, 126, 34)
    # Red: (231, 76, 60)
    
    if ratio < 0.33:
        # Green to Yellow transition
        local_ratio = ratio / 0.33
        r = int(46 + (241 - 46) * local_ratio)
        g = int(204 + (196 - 204) * local_ratio)
        b = int(113 + (15 - 113) * local_ratio)
    elif ratio < 0.67:
        # Yellow to Orange transition
        local_ratio = (ratio - 0.33) / 0.34
        r = int(241 + (230 - 241) * local_ratio)
        g = int(196 + (126 - 196) * local_ratio)
        b = int(15 + (34 - 15) * local_ratio)
    else:
        # Orange to Red transition
        local_ratio = (ratio - 0.67) / 0.33
        r = int(230 + (231 - 230) * local_ratio)
        g = int(126 + (76 - 126) * local_ratio)
        b = int(34 + (60 - 34) * local_ratio)
    
    return f'#{r:02x}{g:02x}{b:02x}'


def get_heatmap_color(value, max_val, thresholds=(0.15, 0.4, 0.7)):
    """
    Return color based on intensity for heatmap style.
    Green -> Yellow -> Orange -> Red gradient.
    
    Args:
        value: Current value
        max_val: Maximum value in dataset
        thresholds: Tuple of ratio thresholds for color transitions
        
    Returns:
        str: Hex color code
    """
    if max_val == 0:
        return '#2ecc71'
    
    ratio = value / max_val
    
    if ratio < thresholds[0]:
        return '#2ecc71'  # Soft Green
    elif ratio < thresholds[1]:
        return '#f1c40f'  # Yellow
    elif ratio < thresholds[2]:
        return '#e67e22'  # Orange
    else:
        return '#e74c3c'  # Bright Red


def scale_linear(val, min_val, max_val, target_min, target_max):
    """
    Linear scaling of values to target range.
    
    Args:
        val: Value to scale
        min_val: Minimum value in dataset
        max_val: Maximum value in dataset
        target_min: Minimum output value
        target_max: Maximum output value
        
    Returns:
        float: Scaled value
    """
    if max_val == min_val:
        return target_min
    
    return target_min + (float(val - min_val) / float(max_val - min_val) * (target_max - target_min))


def scale_log(val, multiplier=6):
    """
    Logarithmic scaling using log1p (log(1+x)).
    
    Args:
        val: Value to scale
        multiplier: Scale multiplier
        
    Returns:
        float: Scaled value
    """
    return np.log1p(val) * multiplier


def scale_log_range(val, min_val, max_val, target_min, target_max):
    """
    Logarithmic scaling with normalization to target range.
    Uses log1p to handle small values and scales to specified output range.
    
    Args:
        val: Value to scale
        min_val: Minimum value in dataset
        max_val: Maximum value in dataset
        target_min: Minimum output value
        target_max: Maximum output value
        
    Returns:
        float: Scaled value in target range
    """
    if max_val == min_val:
        return target_min
    
    # Apply log transform
    val_log = np.log1p(val)
    min_log = np.log1p(min_val)
    max_log = np.log1p(max_val)
    
    # Normalize to target range
    return target_min + (float(val_log - min_log) / float(max_log - min_log) * (target_max - target_min))


def scale_sqrt(val, min_val, max_val, target_min, target_max):
    """
    Square root scaling to flatten growth curve.
    
    Args:
        val: Value to scale
        min_val: Minimum value in dataset
        max_val: Maximum value in dataset
        target_min: Minimum output value
        target_max: Maximum output value
        
    Returns:
        float: Scaled value
    """
    if max_val == min_val:
        return target_min
    
    val_sqrt = np.sqrt(val)
    min_sqrt = np.sqrt(min_val)
    max_sqrt = np.sqrt(max_val)
    
    return target_min + (float(val_sqrt - min_sqrt) / float(max_sqrt - min_sqrt) * (target_max - target_min))


def scale_edge_width_sqrt(hits, multiplier=0.5):
    """
    Scale edge width using square root for visual balance.
    
    Args:
        hits: Number of hits
        multiplier: Width multiplier
        
    Returns:
        float: Edge width
    """
    return np.sqrt(hits) * multiplier
