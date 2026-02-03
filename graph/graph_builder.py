"""NetworkX graph construction for firewall visualizations."""
import networkx as nx
from .styling import (
    get_color_gradient,
    get_heatmap_color,
    get_smooth_gradient,
    scale_linear,
    scale_log,
    scale_log_range,
    scale_sqrt,
    scale_edge_width_sqrt
)


class FirewallGraphBuilder:
    """Builds NetworkX directed graphs from firewall data."""
    
    def __init__(self, viz_data, preset_config, hostname_resolver=None):
        """
        Initialize graph builder.
        
        Args:
            viz_data: Aggregated pandas DataFrame with attack data
            preset_config: Configuration dict with styling parameters
            hostname_resolver: Optional HostnameResolver instance
        """
        self.viz_data = viz_data
        self.config = preset_config
        self.hostname_resolver = hostname_resolver
        self.graph = nx.DiGraph()
    
    def build(self):
        """
        Build complete NetworkX graph with nodes and edges.
        
        Returns:
            networkx.DiGraph: Constructed graph
        """
        # Calculate global statistics
        max_hits = self.viz_data['Hits'].max()
        min_hits = self.viz_data['Hits'].min()
        
        # Calculate node statistics based on styling mode
        if self.config.get('node_sizing') == 'separate':
            attacker_stats = self.viz_data.groupby('Source IP')['Hits'].sum()
            target_stats = self.viz_data.groupby('Destination IP')['Hits'].sum()
            max_attacker_vol = attacker_stats.max()
            max_target_vol = target_stats.max()
            node_stats = None
        else:
            # Combined node sizing (default)
            node_stats = self.viz_data.groupby('Source IP')['Hits'].sum().add(
                self.viz_data.groupby('Destination IP')['Hits'].sum(), 
                fill_value=0
            )
            attacker_stats = target_stats = None
            max_attacker_vol = max_target_vol = None
        
        # Build graph from aggregated data
        for _, row in self.viz_data.iterrows():
            src = str(row['Source IP'])
            dst = str(row['Destination IP'])
            hits = int(row['Hits'])
            
            # Add nodes
            if self.config.get('node_sizing') == 'separate':
                self._add_attacker_node_separate(src, row, attacker_stats, max_attacker_vol)
                self._add_target_node_separate(dst, target_stats, max_target_vol)
            else:
                self._add_node_combined(src, dst, row, node_stats)
            
            # Add edge
            self._add_edge(src, dst, hits, row, max_hits, min_hits)
        
        return self.graph
    
    def _add_node_combined(self, src, dst, row, node_stats):
        """Add nodes with combined sizing (used by intensity preset)."""
        node_size_range = self.config.get('node_size_range', [3, 15])
        
        # Get min/max stats for scaling
        min_stats = node_stats.min()
        max_stats = node_stats.max()
        
        # Source node (attacker) - scale to configured range
        src_size = scale_log_range(node_stats[src], min_stats, max_stats, 
                                     node_size_range[0], node_size_range[1])
        # Build tooltip with hostname if available
        src_hostname = self._get_hostname(src)
        if src_hostname != src:
            src_title = f"ATTACKER: {src}\nHostname: {src_hostname}\nCountry: {row['Source Country']}"
        else:
            src_title = f"ATTACKER: {src}\nCountry: {row['Source Country']}"
        
        src_label = self._format_node_label(src, src_hostname)
        self.graph.add_node(
            src,
            label=src_label,
            size=src_size,
            color='#bdc3c7',  # Gray for attackers
            title=src_title
        )
        
        # Destination node (target) - scale to configured range
        dst_size = scale_log_range(node_stats[dst], min_stats, max_stats,
                                     node_size_range[0], node_size_range[1])
        # Build tooltip with hostname if available
        dst_hostname = self._get_hostname(dst)
        if dst_hostname != dst:
            dst_title = f"TARGET: {dst}\nHostname: {dst_hostname}"
        else:
            dst_title = f"TARGET: {dst}"
        
        dst_label = self._format_node_label(dst, dst_hostname)
        self.graph.add_node(
            dst,
            label=dst_label,
            size=dst_size,
            color='#3498db',  # Blue for targets
            title=dst_title
        )
    
    def _add_attacker_node_separate(self, src, row, attacker_stats, max_attacker_vol):
        """Add attacker node with separate sizing (used by heatmap/micro presets)."""
        src_vol = attacker_stats[src]
        node_size_range = self.config.get('node_size_range', [6, 28])
        
        # Determine sizing method
        if self.config.get('node_scale_method') == 'sqrt':
            src_size = scale_sqrt(src_vol, 0, max_attacker_vol, node_size_range[0], node_size_range[1])
        else:
            src_size = scale_linear(src_vol, 0, max_attacker_vol, node_size_range[0], node_size_range[1])
        
        # Determine color
        color_mode = self.config.get('color_mode', 'gradient')
        if color_mode == 'heatmap':
            thresholds = self.config.get('color_thresholds', (0.15, 0.4, 0.7))
            src_color = get_heatmap_color(src_vol, max_attacker_vol, thresholds)
        else:
            src_color = '#bdc3c7'  # Default gray
        
        # Get hostname if available
        src_hostname = self._get_hostname(src)
        
        # Label only significant attackers for micro preset
        if self.config.get('label_threshold'):
            if src_vol > (max_attacker_vol * self.config['label_threshold']):
                src_label = self._format_node_label(src, src_hostname)
            else:
                src_label = ""
        else:
            src_label = self._format_node_label(src, src_hostname)
        
        # Build tooltip with hostname if available
        if src_hostname != src:
            src_title = f"ATTACKER: {src}\nHostname: {src_hostname}\nCountry: {row['Source Country']}\nTotal Hits: {src_vol}"
        else:
            src_title = f"ATTACKER: {src}\nCountry: {row['Source Country']}\nTotal Hits: {src_vol}"
        
        self.graph.add_node(
            src,
            label=src_label,
            size=src_size,
            color=src_color,
            borderWidth=2,
            shape='dot',
            title=src_title
        )
    
    def _add_target_node_separate(self, dst, target_stats, max_target_vol):
        """Add target node with separate sizing."""
        dst_vol = target_stats[dst]
        target_size_range = self.config.get('target_size_range', [8, 30])
        
        if self.config.get('node_scale_method') == 'sqrt':
            dst_size = scale_sqrt(dst_vol, 0, max_target_vol, target_size_range[0], target_size_range[1])
        else:
            dst_size = scale_linear(dst_vol, 0, max_target_vol, target_size_range[0], target_size_range[1])
        
        # Build tooltip with hostname if available
        dst_hostname = self._get_hostname(dst)
        if dst_hostname != dst:
            dst_title = f"TARGET: {dst}\nHostname: {dst_hostname}\nIncoming Hits: {dst_vol}"
        else:
            dst_title = f"TARGET: {dst}\nIncoming Hits: {dst_vol}"
        
        dst_label = self._format_node_label(dst, dst_hostname)
        self.graph.add_node(
            dst,
            label=dst_label,
            size=dst_size,
            color='#2c3e50',  # Dark blue
            borderWidth=3,
            borderColor='#3498db',  # Blue border
            title=dst_title
        )
    
    def _add_edge(self, src, dst, hits, row, max_hits, min_hits):
        """Add edge between nodes."""
        edge_width_range = self.config.get('edge_width_range', [1, 6])
        
        # Determine edge width
        if self.config.get('edge_scale_method') == 'sqrt_simple':
            # Use sqrt scaling but scale to edge_width_range
            # Map sqrt(hits) to the configured range
            import numpy as np
            sqrt_hits = np.sqrt(hits)
            sqrt_min = np.sqrt(min_hits)
            sqrt_max = np.sqrt(max_hits)
            if sqrt_max > sqrt_min:
                normalized = (sqrt_hits - sqrt_min) / (sqrt_max - sqrt_min)
                edge_width = edge_width_range[0] + normalized * (edge_width_range[1] - edge_width_range[0])
            else:
                edge_width = edge_width_range[0]
        elif self.config.get('edge_scale_method') == 'linear':
            edge_width = scale_linear(hits, min_hits, max_hits, edge_width_range[0], edge_width_range[1])
        else:
            # Default sqrt with range
            edge_width = scale_linear(hits, min_hits, max_hits, edge_width_range[0], edge_width_range[1])
        
        # Determine edge color
        color_mode = self.config.get('color_mode', 'gradient')
        use_smooth_gradient = self.config.get('use_smooth_gradient', True)
        
        if use_smooth_gradient:
            # Use smooth gradient based on min/max values
            edge_color = get_smooth_gradient(hits, min_hits, max_hits)
        elif color_mode == 'heatmap':
            thresholds = self.config.get('color_thresholds', (0.15, 0.4, 0.7))
            edge_color = get_heatmap_color(hits, max_hits, thresholds)
        else:
            thresholds = self.config.get('color_thresholds', (0.2, 0.6))
            edge_color = get_color_gradient(hits, max_hits, thresholds)
        
        # Calculate arrow scale based on edge width if enabled
        arrow_scale_factor = None
        if self.config.get('scale_arrows_with_edges', False):
            # Scale arrow size proportionally to edge width
            base_arrow_scale = self.config.get('base_arrow_scale', 0.5)
            # Normalize edge width to get scaling factor
            width_ratio = edge_width / edge_width_range[0]  # Ratio compared to minimum
            arrow_scale_factor = base_arrow_scale * width_ratio
        
        # Add edge attributes
        # Use explicit 'width' for precise control over edge thickness
        # (not using 'value' to avoid vis.js auto-scaling)
        edge_attrs = {
            'width': edge_width,  # Explicit pixel width from our calculation
            'color': edge_color,
            'title': f"Hits: {hits}\nType: {row['Classification']}"
        }
        
        # Add arrow scaling if enabled
        if arrow_scale_factor is not None:
            edge_attrs['arrows'] = {
                'to': {
                    'enabled': True,
                    'scaleFactor': arrow_scale_factor
                }
            }
        
        # Optional opacity for micro preset
        if self.config.get('edge_opacity'):
            edge_attrs['opacity'] = self.config['edge_opacity']
        
        self.graph.add_edge(src, dst, **edge_attrs)
    
    def _get_hostname(self, ip):
        """
        Get hostname for IP if resolver is available.
        
        Args:
            ip: IP address string
            
        Returns:
            str: Hostname or IP if not available
        """
        if self.hostname_resolver:
            return self.hostname_resolver.get_hostname(ip)
        return ip
    
    def _format_node_label(self, ip, hostname):
        """
        Format node label based on hostname settings.
        
        Args:
            ip: IP address string
            hostname: Resolved hostname or IP
            
        Returns:
            str: Formatted label
        """
        hostname_settings = self.config.get('hostname_labels', {})
        
        # If hostname resolution not enabled or no hostname, return IP
        if not self.hostname_resolver or hostname == ip:
            return ip
        
        # Check if hostname labels are enabled
        if not hostname_settings.get('show_in_labels', False):
            return ip
        
        # Determine label format
        if hostname_settings.get('prefer_hostname', False):
            # Use hostname only
            return hostname
        elif hostname_settings.get('show_both', False):
            # Show both IP and hostname
            return f"{ip}\n{hostname}"
        else:
            # Default: show IP only
            return ip
