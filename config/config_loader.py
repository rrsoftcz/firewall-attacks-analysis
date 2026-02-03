"""Configuration loader for global settings."""
import yaml
from pathlib import Path


class ConfigLoader:
    """Loads and manages global configuration from config.yaml."""
    
    def __init__(self, config_file='config.yaml'):
        """
        Initialize configuration loader.
        
        Args:
            config_file: Path to YAML config file
        """
        self.config_file = Path(config_file)
        self.config = {}
        self.load()
    
    def load(self):
        """Load configuration from YAML file."""
        if not self.config_file.exists():
            print(f"Warning: Config file not found: {self.config_file}, using defaults")
            self.config = self._get_defaults()
            return
        
        try:
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            print(f"Warning: Error parsing config.yaml: {e}")
            print("Using default settings")
            self.config = self._get_defaults()
        except Exception as e:
            print(f"Warning: Error loading config: {e}")
            self.config = self._get_defaults()
    
    def _get_defaults(self):
        """Get default configuration values."""
        return {
            'node_size_multiplier': 1.0,
            'edge_width_multiplier': 1.0,
            'default_input': 'sophos_data.csv',
            'default_risk_report': 'high_risk_attackers.csv',
            'hostname_labels': {
                'show_in_labels': False,  # Show hostnames in node labels
                'prefer_hostname': False,  # Use hostname instead of IP in label
                'show_both': False         # Show "IP\nhostname" format
            }
        }
    
    def get(self, key, default=None):
        """Get configuration value by key."""
        return self.config.get(key, default)
    
    def get_node_size_multiplier(self):
        """Get global node size multiplier."""
        return self.config.get('node_size_multiplier', 1.0)
    
    def get_edge_width_multiplier(self):
        """Get global edge width multiplier."""
        return self.config.get('edge_width_multiplier', 1.0)
    
    def apply_to_preset(self, preset_config):
        """
        Apply global settings to a preset configuration.
        
        Args:
            preset_config: Preset dictionary to modify
            
        Returns:
            dict: Modified preset config
        """
        config = preset_config.copy()
        
        # Apply node size multiplier
        node_mult = self.get_node_size_multiplier()
        if 'node_size_range' in config:
            config['node_size_range'] = [
                max(1, size * node_mult) for size in config['node_size_range']
            ]
        if 'target_size_range' in config:
            config['target_size_range'] = [
                max(1, size * node_mult) for size in config['target_size_range']
            ]
        
        # Apply edge width multiplier
        edge_mult = self.get_edge_width_multiplier()
        if 'edge_width_range' in config:
            config['edge_width_range'] = [
                width * edge_mult for width in config['edge_width_range']
            ]
        
        # Apply preset-specific overrides from config.yaml
        preset_overrides = self.config.get('presets', {}) or {}
        preset_name = preset_config.get('name', '').lower().replace(' ', '_')
        
        # Try to find override by preset key
        for key in preset_overrides.keys():
            if key in ['intensity', 'heatmap', 'micro', 'balanced']:
                if key in preset_name or preset_name in key:
                    override = preset_overrides[key]
                    config.update(override)
                    break
        
        # Apply global physics overrides
        if 'physics' in self.config:
            if 'physics' not in config:
                config['physics'] = {}
            config['physics'].update(self.config['physics'])
        
        # Apply global theme overrides
        if 'theme' in self.config:
            if 'theme' not in config:
                config['theme'] = {}
            config['theme'].update(self.config['theme'])
        
        # Apply canvas overrides (can be in 'canvas' or 'theme' section)
        if 'canvas' in self.config:
            if 'theme' not in config:
                config['theme'] = {}
            canvas = self.config['canvas']
            if 'height' in canvas:
                config['theme']['height'] = canvas['height']
            if 'width' in canvas:
                config['theme']['width'] = canvas['width']
        
        # Apply node settings overrides
        if 'node_settings' in self.config and self.config['node_settings']:
            node_settings = self.config['node_settings']
            if node_settings and 'default_size_range' in node_settings and 'node_size_range' not in config:
                config['node_size_range'] = node_settings['default_size_range']
            # Add other node settings as needed
        
        # Apply edge settings overrides
        if 'edge_settings' in self.config and self.config['edge_settings']:
            edge_settings = self.config['edge_settings']
            if edge_settings:
                if 'default_width_range' in edge_settings and 'edge_width_range' not in config:
                    config['edge_width_range'] = edge_settings['default_width_range']
                if 'opacity' in edge_settings and 'edge_opacity' not in config:
                    config['edge_opacity'] = edge_settings['opacity']
                if 'scale_arrows_with_edges' in edge_settings:
                    config['scale_arrows_with_edges'] = edge_settings['scale_arrows_with_edges']
                if 'base_arrow_scale' in edge_settings:
                    config['base_arrow_scale'] = edge_settings['base_arrow_scale']
        
        # Apply hostname label settings
        if 'hostname_labels' in self.config:
            if 'hostname_labels' not in config:
                config['hostname_labels'] = {}
            config['hostname_labels'].update(self.config['hostname_labels'])
        
        return config
    
    def get_default_input(self):
        """Get default input CSV filename."""
        return self.config.get('default_input', 'sophos_data.csv')
    
    def get_default_risk_report(self):
        """Get default risk report filename."""
        return self.config.get('default_risk_report', 'high_risk_attackers.csv')


# Global instance
_global_config = None


def get_global_config():
    """Get or create global configuration instance."""
    global _global_config
    if _global_config is None:
        _global_config = ConfigLoader()
    return _global_config
