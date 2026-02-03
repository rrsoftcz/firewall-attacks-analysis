"""PyVis HTML visualization rendering."""
from pyvis.network import Network


class PyVisRenderer:
    """Renders NetworkX graphs to interactive HTML using PyVis."""
    
    def __init__(self, graph, preset_config):
        """
        Initialize renderer.
        
        Args:
            graph: NetworkX DiGraph to render
            preset_config: Configuration dict with physics and theme settings
        """
        self.graph = graph
        self.config = preset_config
    
    def render(self, output_file):
        """
        Render graph to HTML file.
        
        Args:
            output_file: Output HTML filename
            
        Returns:
            str: Output filename
        """
        # Get theme settings
        theme = self.config.get('theme', {})
        height = theme.get('height', '900px')
        width = theme.get('width', '100%')
        bgcolor = theme.get('bgcolor', '#0b0e11')
        font_color = theme.get('font_color', 'white')
        
        # Create PyVis network
        net = Network(
            height=height,
            width=width,
            bgcolor=bgcolor,
            font_color=font_color,
            directed=True
        )
        
        # Manually add nodes and edges to preserve all attributes
        # (PyVis's from_nx() ignores the 'width' attribute)
        for node, attrs in self.graph.nodes(data=True):
            net.add_node(node, **attrs)
        
        for src, dst, attrs in self.graph.edges(data=True):
            net.add_edge(src, dst, **attrs)
        
        # Apply physics configuration
        physics = self.config.get('physics', {})
        options = self._build_options(physics)
        net.set_options(options)
        
        # Save HTML
        net.save_graph(output_file)
        print(f"Visualization: {output_file}")
        
        return output_file
    
    def _build_options(self, physics_config):
        """
        Build PyVis options string from config.
        
        Args:
            physics_config: Physics configuration dict
            
        Returns:
            str: JavaScript options string
        """
        # Default physics settings
        gravitational = physics_config.get('gravitational_constant', -20000)
        central_gravity = physics_config.get('central_gravity', 0.8)
        spring_length = physics_config.get('spring_length', 100)
        spring_constant = physics_config.get('spring_constant', 0.05)
        damping = physics_config.get('damping', 0.3)
        stabilization_iter = physics_config.get('stabilization_iterations', 40)
        
        # Edge settings
        edge_smooth = physics_config.get('edge_smooth', False)
        edge_smooth_type = physics_config.get('edge_smooth_type', 'dynamic')  # dynamic, continuous, discrete, etc.
        edge_roundness = physics_config.get('edge_roundness', 0.5)  # 0.0 to 1.0
        arrow_scale = physics_config.get('arrow_scale', 0.4)
        
        # Build smooth configuration
        if edge_smooth:
            # Advanced smooth configuration with type
            smooth_config = f"""{{
              "enabled": true,
              "type": "{edge_smooth_type}",
              "roundness": {edge_roundness}
            }}"""
        else:
            smooth_config = "false"
        
        options = f"""
        var options = {{
          "edges": {{
            "smooth": {smooth_config},
            "arrows": {{ "to": {{ "enabled": true, "scaleFactor": {arrow_scale} }} }},
            "color": {{ "inherit": false }}
          }},
          "physics": {{
            "barnesHut": {{
              "gravitationalConstant": {gravitational},
              "centralGravity": {central_gravity},
              "springLength": {spring_length},
              "springConstant": {spring_constant},
              "damping": {damping}
            }},
            "stabilization": {{ "enabled": true, "iterations": {stabilization_iter} }}
          }},
          "interaction": {{
            "tooltipDelay": 100,
            "hideEdgesOnDrag": false
          }},
          "nodes": {{
            "font": {{ "multi": "html" }}
          }}
        }}
        """
        
        return options
