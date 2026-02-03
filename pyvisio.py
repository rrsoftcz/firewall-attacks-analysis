#!/usr/bin/env python3
"""
Pyvisio - Firewall Log Network Visualization Tool

Unified CLI tool for generating interactive network graphs from Sophos firewall logs.
"""
import argparse
import sys
from pathlib import Path

from core.data_loader import FirewallDataLoader
from core.data_processor import FirewallDataProcessor
from core.risk_reporter import RiskReporter
from core.hostname_resolver import HostnameResolver
from graph.graph_builder import FirewallGraphBuilder
from visualization.pyvis_renderer import PyVisRenderer
from config.presets import get_preset, list_presets, PRESETS
from config.config_loader import get_global_config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Pyvisio - Firewall Log Network Visualization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all presets (default behavior)
  %(prog)s

  # Generate all presets with custom input
  %(prog)s -i firewall_logs.csv

  # Generate specific preset only
  %(prog)s --preset heatmap

  # Generate with hostname resolution (internal IPs only)
  %(prog)s --resolve-internal-only

  # Generate with full hostname resolution (all IPs)
  %(prog)s --resolve-hostnames

  # Pre-cache hostnames for external IPs (run once)
  %(prog)s --pre-cache-hostnames

  # Show hostname cache statistics
  %(prog)s --show-cache-stats

  # Clear hostname cache
  %(prog)s --clear-hostname-cache

  # Show available presets
  %(prog)s --list-presets
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        default='sophos_data.csv',
        help='Input CSV file (default: sophos_data.csv)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output HTML file (default: preset-specific filename)'
    )
    
    parser.add_argument(
        '-p', '--preset',
        default='all',
        choices=['all', 'intensity', 'heatmap', 'micro', 'balanced'],
        help='Visualization preset - use "all" to generate all presets (default: all)'
    )
    
    parser.add_argument(
        '--top-n',
        type=int,
        help='Limit to top N connections by hits (default: preset-specific)'
    )
    
    parser.add_argument(
        '--risk-report',
        default='high_risk_attackers.csv',
        help='Risk report CSV filename (default: high_risk_attackers.csv)'
    )
    
    parser.add_argument(
        '--top-attackers',
        type=int,
        metavar='N',
        help='Print top N attackers to stdout (for firewall blocking)'
    )
    
    parser.add_argument(
        '--list-presets',
        action='store_true',
        help='List available visualization presets and exit'
    )
    
    parser.add_argument(
        '--resolve-hostnames',
        action='store_true',
        help='Resolve IP addresses to hostnames (shown in tooltips)'
    )
    
    parser.add_argument(
        '--resolve-internal-only',
        action='store_true',
        help='Only resolve internal/private IP addresses (10.x, 172.16.x, 192.168.x)'
    )
    
    parser.add_argument(
        '--pre-cache-hostnames',
        action='store_true',
        help='Pre-cache all hostnames (including external IPs) and exit'
    )
    
    parser.add_argument(
        '--clear-hostname-cache',
        action='store_true',
        help='Clear hostname cache and exit'
    )
    
    parser.add_argument(
        '--show-cache-stats',
        action='store_true',
        help='Show hostname cache statistics and exit'
    )
    
    args = parser.parse_args()
    
    # Handle utility commands
    if args.list_presets:
        print("Available Visualization Presets:\n")
        for name, desc in list_presets():
            print(f"  {name:12s} - {desc}")
        return 0
    
    if args.clear_hostname_cache:
        resolver = HostnameResolver()
        resolver.clear_cache()
        return 0
    
    if args.show_cache_stats:
        resolver = HostnameResolver()
        stats = resolver.get_cache_stats()
        print("\nHostname Cache Statistics:")
        print(f"  Total cached: {stats['total_cached']}")
        print(f"  Internal IPs: {stats['internal_ips']}")
        print(f"  External IPs: {stats['external_ips']}")
        print(f"  Failed resolutions: {stats['failed_resolutions']}")
        print(f"  Cache file: {stats['cache_file']}")
        print(f"  Cache exists: {stats['cache_file_exists']}")
        return 0
    
    if args.pre_cache_hostnames:
        print("Pre-caching hostnames for all IPs...\n")
        loader = FirewallDataLoader(args.input)
        df = loader.load()
        
        # Collect all unique IPs
        all_ips = list(set(df['Source IP'].unique().tolist() + df['Destination IP'].unique().tolist()))
        
        resolver = HostnameResolver()
        resolver.resolve_batch(
            all_ips,
            max_workers=50,
            timeout=2.0,  # Longer timeout for external IPs
            internal_only=False,  # Resolve everything
            show_progress=True
        )
        
        stats = resolver.get_cache_stats()
        print(f"\nPre-caching complete!")
        print(f"  Total cached: {stats['total_cached']}")
        print(f"  Internal IPs: {stats['internal_ips']}")
        print(f"  External IPs: {stats['external_ips']}")
        return 0
    
    try:
        # Load global configuration
        global_config = get_global_config()
        
        # Determine which presets to generate
        if args.preset == 'all':
            presets_to_generate = list(PRESETS.keys())
        else:
            presets_to_generate = [args.preset]
        
        # Initialize hostname resolver if requested
        hostname_resolver = None
        if args.resolve_hostnames or args.resolve_internal_only:
            hostname_resolver = HostnameResolver()
            print("Hostname resolution enabled")
        
        # Load and process data once (shared across all presets)
        print("Loading firewall data...")
        loader = FirewallDataLoader(args.input)
        df = loader.load()
        
        processor = FirewallDataProcessor(df)
        processor.clean()
        
        # Resolve hostnames if requested
        if hostname_resolver:
            all_ips = list(set(
                processor.df['Source IP'].unique().tolist() + 
                processor.df['Destination IP'].unique().tolist()
            ))
            hostname_resolver.resolve_batch(
                all_ips,
                max_workers=50,
                timeout=1.0,
                internal_only=args.resolve_internal_only,
                show_progress=True
            )
            print()
        
        # Generate risk report once
        reporter = RiskReporter(processor.df)
        risk_report = reporter.generate_risk_report(args.risk_report)
        
        # Print top attackers if requested
        if args.top_attackers:
            top_ips = reporter.get_top_attackers(risk_report, args.top_attackers)
            print(f"\nTop {args.top_attackers} Attackers (for firewall blocking):")
            for i, ip in enumerate(top_ips, 1):
                risk_score = risk_report[risk_report['Source IP'] == ip]['Risk Score'].iloc[0]
                print(f"  {i:2d}. {ip:15s} (Risk Score: {risk_score})")
            print()
        
        # Generate visualization for each preset
        for preset_name in presets_to_generate:
            print(f"\n{'='*60}")
            print(f"Generating preset: {preset_name}")
            print(f"{'='*60}")
            
            # Get preset configuration
            config = get_preset(preset_name)
            
            # Apply global config settings
            config = global_config.apply_to_preset(config)
            
            # Override with CLI args if provided
            if args.top_n:
                config['top_n'] = args.top_n
            
            # Determine output file
            if args.output and len(presets_to_generate) == 1:
                # Use custom output only if single preset
                output_file = args.output
            else:
                output_file = config['default_output']
            
            print(f"Top N connections: {config['top_n']}")
            
            # Aggregate for visualization (preset-specific top_n)
            viz_data = processor.aggregate_for_visualization(top_n=config['top_n'])
            print(f"Visualizing {len(viz_data)} connections")
            
            # Build graph
            builder = FirewallGraphBuilder(viz_data, config, hostname_resolver)
            graph = builder.build()
            print(f"Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
            
            # Render visualization
            renderer = PyVisRenderer(graph, config)
            renderer.render(output_file)
            
            print(f"Generated: {output_file}")
        
        print(f"\n{'='*60}")
        print(f"All done! Generated {len(presets_to_generate)} visualization(s).")
        print(f"{'='*60}")
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
