# Pyvis - Firewall Log Network Visualization

A powerful yet simple CLI tool for visualizing firewall logs. Point it at your Sophos CSV exports and get beautiful, interactive network graphs that show you exactly who's attacking what. Perfect for security analysis, incident reports, and identifying patterns in your firewall data.

## What It Does

Pyvisio transforms boring CSV firewall logs into interactive HTML visualizations where you can:
- See attack patterns at a glance with color-coded threat levels
- Identify your most aggressive attackers and their targets
- Understand which internal assets are being targeted most
- Generate prioritized risk reports for blocking decisions
- Explore your data interactively: zoom, drag nodes, hover for detailed tooltips

## Features

**Blazing Fast** - Handles 10K logs in under 3 seconds  
**Four Visualization Styles** - Pick the view that works for your analysis  
**Smart Risk Scoring** - Automatically ranks attackers by threat level  
**Hostname Resolution** - See actual server names instead of just IPs (optional)  
**Flexible Configuration** - Fine-tune everything via config.yaml  
**Zero Dependencies Fuss** - Just pandas, NetworkX, and PyVis

## Quick Start

### Installation

```bash
# Navigate to project directory
cd /pyvis-data-analysis

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Activate virtual environment
source venv/bin/activate

# Generate all four visualizations (default)
python pyvisio.py

# Generate a specific style
python pyvisio.py --preset heatmap

# Get top 10 attackers for firewall blocking
python pyvisio.py --top-attackers 10

# Show all available presets
python pyvisio.py --list-presets
```

## Command Reference

```bash
python pyvisio.py [OPTIONS]

Main Options:
  -i, --input FILE              Input CSV file (default: sophos_data.csv)
  -o, --output FILE             Output HTML file (default: preset-specific)
  -p, --preset PRESET           Visualization preset: all, intensity, heatmap, micro, balanced
  --top-n N                     Limit to top N connections by hits
  --top-attackers N             Print top N attackers to stdout

Hostname Resolution:
  --resolve-hostnames           Resolve all IP addresses to hostnames
  --resolve-internal-only       Only resolve private IPs (10.x, 172.16.x, 192.168.x)
  --pre-cache-hostnames         Pre-cache all hostnames and exit
  --show-cache-stats            Show hostname cache statistics
  --clear-hostname-cache        Clear hostname cache

Other:
  --list-presets                List available presets and exit
  --risk-report FILE            Risk report CSV filename (default: high_risk_attackers.csv)
  -h, --help                    Show help message
```

### Common Examples

```bash
# Default behavior - generate all four visualization styles
python pyvisio.py

# Just the heatmap view
python pyvisio.py --preset heatmap

# Custom input file
python pyvisio.py -i my_firewall_logs.csv

# Heatmap with top 500 connections
python pyvisio.py -p heatmap --top-n 500

# Get top 20 attackers for your firewall blocklist
python pyvisio.py --top-attackers 20

# Generate with hostname resolution (internal IPs only - fast)
python pyvisio.py --resolve-internal-only

# Pre-cache external hostnames once, then generate quickly
python pyvisio.py --pre-cache-hostnames
python pyvisio.py --resolve-hostnames
```

## Visualization Presets

Pyvisio offers four distinct visualization styles. Each one tells a different story with your data.

### 1. Intensity (Default)
The jack-of-all-trades view. Good balance between detail and readability.

- **Output**: `firewall_intensity_map.html`
- **Style**: Gray attackers, blue targets, color-coded edge intensity
- **Best for**: General-purpose security analysis
- **Shows**: 400 top connections with logarithmic node sizing

### 2. Heatmap
See your threat landscape in living color. Nodes go from green (quiet) to red (under siege).

- **Output**: `firewall_security_heatmap.html`
- **Style**: Color-coded nodes based on attack volume
- **Best for**: Quickly spotting hotspots and patterns
- **Shows**: 350 top connections with more spacing for clarity

### 3. Micro
The 30,000-foot view. Tiny nodes, maximum data density.

- **Output**: `firewall_micro_heatmap.html`
- **Style**: Minimal 3-12px nodes, white background, labels only for top threats
- **Best for**: Getting the big picture with complex data
- **Shows**: 400 connections in a compact, clean layout

### 4. Balanced
The presentation-ready view. Clean, professional, easy to read.

- **Output**: `firewall_clean_map.html`
- **Style**: Moderate node sizes, dark theme, clear spacing
- **Best for**: Reports and presentations
- **Shows**: 350 connections with balanced aesthetics

## Understanding the Visualizations

### What You're Looking At

**Nodes (circles and squares)**
- **Red circles** = Attackers (external IPs trying to get in)
- **Blue squares** = Targets (your internal assets being attacked)

**Edges (connecting lines)**
- **Thickness** = Number of attack attempts (thicker = more hits)
- **Color** = Threat intensity
  - Green = Low intensity (1-33% of maximum)
  - Yellow = Medium intensity (34-66%)
  - Orange = High intensity (67-99%)
  - Red = Critical (top threats)

### Interacting With the Graphs

- **Drag nodes** around to reorganize the layout
- **Hover** over nodes or edges to see detailed stats
- **Zoom** in/out with your mouse wheel
- **Pan** by dragging the background
- **Toggle physics** using the visualization controls to freeze or animate

## Hostname Resolution

By default, Pyvisio shows raw IP addresses. But if you want to see actual server names in your tooltips, enable hostname resolution.

### Quick Start

```bash
# Resolve internal IPs only (fast, recommended)
python pyvisio.py --resolve-internal-only

# Resolve all IPs (slower first time, but cached)
python pyvisio.py --resolve-hostnames
```

### How It Works

Pyvisio uses reverse DNS lookups to convert IPs to hostnames. Results are cached in `.hostname_cache.json` for 7 days, so subsequent runs are fast.

**Internal IPs** (10.x.x.x, 172.16-31.x.x, 192.168.x.x) resolve quickly through your local DNS.  
**External IPs** can take 60-120 seconds on the first run but only ~2 seconds once cached.

### Performance Tips

For large datasets with many external IPs, pre-cache once:

```bash
# Run this once (takes a few minutes)
python pyvisio.py --pre-cache-hostnames

# Then generate visualizations instantly
python pyvisio.py --resolve-hostnames
```

Check what's in your cache:
```bash
python pyvisio.py --show-cache-stats
```

Clear stale entries:
```bash
python pyvisio.py --clear-hostname-cache
```

### Privacy Note

Hostname resolution sends reverse DNS queries to your configured DNS servers. External IPs will trigger lookups visible to your DNS provider and potentially to the IP owner. For sensitive networks, use `--resolve-internal-only` to only resolve your own infrastructure.

## Configuration

Fine-tune your visualizations with `config.yaml` in the project root.

### Quick Adjustments

Create `config.yaml` and add:

```yaml
# Make all nodes smaller
node_size_multiplier: 0.7

# Make edges thicker
edge_width_multiplier: 1.2
```

**Node size multiplier** scales all nodes uniformly:
- `0.5` = 50% smaller (minimal nodes)
- `1.0` = default size
- `1.5` = 50% larger

**Edge width multiplier** scales connection thickness:
- `0.5` = 50% thinner
- `1.0` = default width
- `2.0` = twice as thick

### Canvas Size

```yaml
canvas:
  height: "1200px"  # Taller visualization
  width: "100%"     # Full browser width
```

Or go full-screen:
```yaml
canvas:
  height: "100vh"   # Full viewport height
  width: "100vw"    # Full viewport width
```

### Physics and Layout

Control how nodes repel and attract each other:

```yaml
physics:
  gravitational_constant: -30000    # More negative = more spacing
  spring_length: 200                # Longer springs = more spread
  central_gravity: 0.5              # Pull toward center
  damping: 0.4                      # Movement friction
```

### Curved Edges

Prefer curved connections instead of straight lines?

```yaml
physics:
  edge_smooth: true
  edge_smooth_type: 'dynamic'  # Smooth curves
  edge_roundness: 0.7          # How curvy (0.0-1.0)
```

Available curve types: `dynamic`, `continuous`, `discrete`, `curvedCW`, `curvedCCW`, `cubicBezier`, `horizontal`, `vertical`

### Preset-Specific Tweaks

Override settings for individual presets:

```yaml
presets:
  intensity:
    top_n: 500
    node_size_range: [2, 10]
  
  heatmap:
    gravitational_constant: -50000
```

### Configuration Priority

Settings are applied in this order (last wins):
1. Default preset configurations (in code)
2. Global settings in `config.yaml`
3. Preset-specific overrides in `config.yaml`
4. Command-line arguments

## Data Format

Your CSV must have these columns from Sophos firewall exports:

**Required:**
- `Source IP` - Attacker IP address
- `Destination IP` - Target IP address
- `Hits` - Number of attack attempts
- `Classification` - Attack type/category
- `Source Country` - Geographic origin

**Optional (not currently used in visualizations):**
- `Message`
- `OS`
- `Signature ID`

Column names are case-sensitive. Default input file: `sophos_data.csv`

## Risk Report

Every run generates `high_risk_attackers.csv` with attackers ranked by threat level.

**Risk Score Formula:** Total Hits + (Unique Targets × 10)

This penalizes attackers who scan multiple targets (network reconnaissance), not just those with high hit counts.

The report includes:
- Source IP
- Total hits across all targets
- Number of unique targets attacked
- Source country
- Primary attack classification
- Calculated risk score

Use `--top-attackers N` to get a quick blocklist:

```bash
python pyvisio.py --top-attackers 10
# Output:
#   1. 193.142.147.209  (Risk Score: 5049)
#   2. 192.159.99.95    (Risk Score: 1380)
#   ...
```

## Performance

### Real-World Numbers

With a 9,270-entry Sophos log file:
- **Total time**: ~2-3 seconds
- CSV loading: <0.1s
- Data cleaning: ~0.1s
- Graph building: ~0.5s
- HTML rendering: ~2s

### By Preset

- **Intensity**: 400 connections, 198 nodes, ~2.5s
- **Heatmap**: 350 connections, 169 nodes, ~2.2s
- **Micro**: 400 connections, 198 nodes, ~2.5s
- **Balanced**: 350 connections, 169 nodes, ~2.2s

### Scalability

- **10K logs**: 2-3 seconds
- **50K logs**: 5-10 seconds (estimated)
- **100K+ logs**: Still fast, but consider enabling progress bars (future feature)

### What Makes It Fast

- Pandas aggregation instead of row-by-row processing
- NetworkX directed graphs for efficient representation
- Top-N filtering reduces visualization complexity
- No external API calls or LLM processing

## Project Structure

```
pyvis-data-analysis/
├── pyvisio.py                 # Main CLI entry point
├── core/                      # Data processing
│   ├── data_loader.py         # CSV loading and validation
│   ├── data_processor.py      # Cleaning and aggregation
│   ├── risk_reporter.py       # Risk scoring and reports
│   └── hostname_resolver.py   # DNS resolution and caching
├── graph/                     # Graph construction
│   ├── graph_builder.py       # NetworkX graph building
│   └── styling.py             # Colors, sizes, gradients
├── visualization/             # Rendering
│   └── pyvis_renderer.py      # PyVis HTML generation
├── config/                    # Configuration
│   ├── presets.py             # Preset definitions
│   └── config_loader.py       # YAML config handling
├── requirements.txt           # Python dependencies
├── config.yaml                # Optional user configuration
├── sophos_data.csv            # Sample firewall data
├── high_risk_attackers.csv    # Generated risk report
├── *.html                     # Generated visualizations
├── README.md                  # This file
├── WARP.md                    # Developer guide
└── venv/                      # Python virtual environment
```

## Requirements

### System
- Python 3.13+ (3.13.7 recommended)
- macOS or Linux

### Python Dependencies
- pandas >= 2.3.0 - Data wrangling
- networkx >= 3.6.0 - Graph algorithms
- pyvis >= 0.3.2 - Interactive HTML visualizations
- numpy >= 2.4.0 - Numerical operations
- pyyaml >= 6.0 - Configuration parsing

Install everything with:
```bash
pip install -r requirements.txt
```

## Troubleshooting

### "Module not found" errors

Make sure your virtual environment is activated:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### CSV parsing errors

Check that your CSV has the required columns with exact names (case-sensitive). Most issues come from:
- Column name typos
- Missing required columns
- Empty or malformed CSV files

### Visualizations won't load in browser

- Check browser console for JavaScript errors
- Large files (>5MB) may slow down rendering
- Try reducing `--top-n` to show fewer connections
- Disable browser extensions that might interfere

### Hostname resolution is slow

- Use `--resolve-internal-only` for faster results
- Pre-cache external IPs once with `--pre-cache-hostnames`
- Check network/firewall for DNS query blocking

### Nodes are too large/small

Edit `config.yaml`:
```yaml
node_size_multiplier: 0.6  # Smaller nodes
# or
node_size_multiplier: 1.5  # Larger nodes
```

### Graph layout is cramped

Increase spacing in `config.yaml`:
```yaml
physics:
  gravitational_constant: -40000  # More negative = more space
  spring_length: 200              # Longer springs
```

## Changelog

### v1.0.0 (2026-01-21) - Unified CLI Release
- Consolidated five legacy scripts into single pyvisio.py tool
- Four visualization presets with distinct styles
- Automatic risk report generation
- Hostname resolution with intelligent caching
- Global YAML configuration support
- Modular architecture with clean separation of concerns
- Comprehensive documentation

### v0.2.0 (2026-01-20) - Performance Overhaul
- Reduced processing time from hours to seconds
- Added attack intensity color gradients
- Switched to directed graphs with arrows
- Removed LLM dependencies

### v0.1.0 - Initial Version
- Basic CSV to network graph conversion

## Contributing

For development guidelines, see `WARP.md`.

## License

[Add your license here]

## Acknowledgments

Built with excellent open-source tools:
- NetworkX for graph algorithms
- PyVis for interactive visualizations
- pandas for data processing
